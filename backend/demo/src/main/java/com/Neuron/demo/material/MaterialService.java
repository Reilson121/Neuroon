package com.Neuron.demo.material;
import com.Neuron.demo.academico.CatalogoService;
import com.Neuron.demo.common.ErroNegocio;
import com.Neuron.demo.integration.ai.AiClient;
import com.Neuron.demo.usuario.UsuarioAtual;
import jakarta.validation.constraints.NotNull;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.transaction.PlatformTransactionManager;
@Service
public class MaterialService {
 public record MaterialRequest(@NotNull Boolean ativo,@NotNull Boolean fonteMonitorVirtual,@NotNull Boolean disponivelParaPratica,@NotNull Boolean autorizacaoProfessor){}
 private record Salvo(Long id,boolean indexar){}
 private final MaterialRepository materiais;
 private final UsuarioAtual usuarios;
 private final CatalogoService catalogo;
 private final AiClient ai;
 private final TransactionTemplate tx;
 public MaterialService(MaterialRepository materiais,UsuarioAtual usuarios,CatalogoService catalogo,AiClient ai,PlatformTransactionManager manager){this.materiais=materiais;this.usuarios=usuarios;this.catalogo=catalogo;this.ai=ai;this.tx=new TransactionTemplate(manager);}
 public void atualizarPermissoes(Long id,MaterialRequest r,Authentication auth){
  Salvo salvo=tx.execute(status -> {
   usuarios.exigirAdministrador(auth);
   Material m=materiais.findById(id).orElseThrow(() -> new ErroNegocio(404,"MATERIAL_NAO_ENCONTRADO","Material não encontrado."));
   catalogo.exigirDisciplina(m.getDisciplina().getId());
   if(!m.assuntoPertenceADisciplina())throw new ErroNegocio(400,"ASSUNTO_DE_OUTRA_DISCIPLINA","Assunto incompatível com a disciplina.");
   if(r.disponivelParaPratica()){
    if(!m.getDisciplina().oferecePratica())throw new ErroNegocio(409,"DISCIPLINA_SEM_PROVA","Disciplina não está habilitada para prática.");
    if(!m.getTipo().aceitaPratica() || !r.autorizacaoProfessor() || !r.ativo())throw new ErroNegocio(400,"MATERIAL_NAO_ELEGIVEL","Prática exige lista ou prova ativa e autorização do professor.");
   }
   if(r.fonteMonitorVirtual() && m.getTipo().aceitaPratica())throw new ErroNegocio(400,"TIPO_INCOMPATIVEL","Nesta disciplina, listas e provas são referências de prática, não fontes do Monitor.");
   m.setAtivo(r.ativo());m.setFonteMonitorVirtual(r.fonteMonitorVirtual());m.setDisponivelParaPratica(r.disponivelParaPratica());m.setAutorizacaoProfessor(r.autorizacaoProfessor());
   materiais.save(m);return new Salvo(m.getId(),m.isAtivo() && (m.isFonteMonitorVirtual() || m.isDisponivelParaPratica()));
  });
  if(salvo.indexar()){
   try{ai.indexar(salvo.id());}
   catch(RuntimeException e){
    tx.executeWithoutResult(status -> {var m=materiais.findById(salvo.id()).orElseThrow();m.setFonteMonitorVirtual(false);m.setDisponivelParaPratica(false);materiais.save(m);});
    throw e;
   }
  }else ai.remover(salvo.id());
 }
 public void desativar(Long id,Authentication auth){
  tx.executeWithoutResult(status -> {usuarios.exigirAdministrador(auth);var m=materiais.findById(id).orElseThrow(() -> new ErroNegocio(404,"MATERIAL_NAO_ENCONTRADO","Material não encontrado."));m.desativar();m.setFonteMonitorVirtual(false);m.setDisponivelParaPratica(false);materiais.save(m);});
  ai.remover(id);
 }
}
