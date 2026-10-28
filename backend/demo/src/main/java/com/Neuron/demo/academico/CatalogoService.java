package com.Neuron.demo.academico;
import com.Neuron.demo.periodo.*;
import com.Neuron.demo.disciplina.*;
import com.Neuron.demo.assunto.*;
import com.Neuron.demo.material.*;
import com.Neuron.demo.common.ErroNegocio;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
@Service @RequiredArgsConstructor @Transactional(readOnly=true)
public class CatalogoService {
 private final PeriodoRepository periodos;
 private final DisciplinaRepository disciplinas;
 private final AssuntoRepository assuntos;
 private final MaterialRepository materiais;
 public record PeriodoResponse(Long id,int numero,String nome){}
 public record DisciplinaResponse(Long id,String nome,String descricao,boolean possuiProva,Long periodoId){}
 public record AssuntoResponse(Long id,String nome,String descricao,int ordem){}
 public record MaterialResponse(Long id,String titulo,String tipo,Long assuntoId,boolean fonteMonitorVirtual,boolean disponivelParaPratica,boolean contemGabarito,boolean autorizacaoProfessor,boolean arquivoDisponivel){}
 public List<PeriodoResponse> periodos(){return periodos.findByAtivoTrueOrderByOrdemAsc().stream().map(p -> new PeriodoResponse(p.getId(),p.getNumero(),p.getNome())).toList();}
 public List<DisciplinaResponse> disciplinas(Long periodoId){return disciplinas.findByPeriodoIdAndAtivoTrueOrderByNomeAsc(periodoId).stream().filter(d -> d.getPeriodo().isAtivo()).map(this::resposta).toList();}
 public Disciplina exigirDisciplina(Long id){
  Disciplina d=disciplinas.findByIdAndAtivoTrue(id).orElseThrow(() -> new ErroNegocio(404,"DISCIPLINA_NAO_ENCONTRADA","Disciplina não encontrada."));
  if(!d.getPeriodo().isAtivo())throw new ErroNegocio(404,"DISCIPLINA_NAO_ENCONTRADA","Disciplina não encontrada.");return d;
 }
 public Assunto exigirAssunto(Long id,Long disciplinaId){
  if(id==null)return null;
  Assunto a=assuntos.findByIdAndAtivoTrue(id).orElseThrow(() -> new ErroNegocio(404,"ASSUNTO_NAO_ENCONTRADO","Assunto não encontrado."));
  if(!a.getDisciplina().getId().equals(disciplinaId))throw new ErroNegocio(400,"ASSUNTO_DE_OUTRA_DISCIPLINA","O assunto não pertence à disciplina.");return a;
 }
 public DisciplinaResponse detalhar(Long id){return resposta(exigirDisciplina(id));}
 public List<AssuntoResponse> assuntos(Long id){exigirDisciplina(id);return assuntos.findByDisciplinaIdAndAtivoTrueOrderByOrdemAsc(id).stream().map(a -> new AssuntoResponse(a.getId(),a.getNome(),a.getDescricao(),a.getOrdem())).toList();}
 public List<MaterialResponse> materiais(Long id,Long assuntoId){exigirDisciplina(id);exigirAssunto(assuntoId,id);return materiais.findByDisciplinaIdAndAtivoTrueOrderByTituloAsc(id).stream().filter(m -> m.getAssunto()==null || m.getAssunto().isAtivo()).filter(m -> assuntoId==null || m.getAssunto()==null || assuntoId.equals(m.getAssunto().getId())).map(m -> new MaterialResponse(m.getId(),m.getTitulo(),m.getTipo().name(),m.getAssunto()==null?null:m.getAssunto().getId(),m.isFonteMonitorVirtual(),m.podeSerPratica(),m.isContemGabarito(),m.isAutorizacaoProfessor(),ArquivoMaterialService.possuiArquivo(m.getReferenciaExterna()))).toList();}
 private DisciplinaResponse resposta(Disciplina d){return new DisciplinaResponse(d.getId(),d.getNome(),d.getDescricao(),d.oferecePratica(),d.getPeriodo().getId());}
}
