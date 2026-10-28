package com.Neuron.demo.monitorvirtual;
import com.Neuron.demo.academico.CatalogoService;
import com.Neuron.demo.usuario.UsuarioAtual;
import com.Neuron.demo.common.LimiteRequisicoes;
import com.Neuron.demo.integration.ai.AiClient;
import jakarta.validation.constraints.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.security.core.Authentication;
import org.springframework.transaction.annotation.Transactional;
import java.util.*;
@Service @RequiredArgsConstructor
public class MonitorVirtualService {
 private final CatalogoService catalogo;
 private final UsuarioAtual usuarios;
 private final LimiteRequisicoes limite;
 private final AiClient ai;
 private final HistoricoMonitorService historico;
 public record ChatRequest(@NotNull @Positive Long disciplinaId,@Positive Long assuntoId,@NotBlank @Size(max=4000) String pergunta,UUID threadId){}
 public record Preparacao(Map<String,Object> requisicao,Long usuarioId,ChatRequest entrada){}
 @Transactional(readOnly=true)
 public Preparacao preparar(ChatRequest r,Authentication auth){
  var u=usuarios.exigir(auth);limite.exigir(u.getId(),"monitor");
  var d=catalogo.exigirDisciplina(r.disciplinaId());var a=catalogo.exigirAssunto(r.assuntoId(),d.getId());
  var contexto=historico.contexto(r.threadId(),u.getId(),d.getId(),r.assuntoId());
  Map<String,Object> req=new HashMap<>();req.put("pergunta",r.pergunta());req.put("disciplina",d.getSlug());req.put("assunto",a==null?null:a.getSlug());req.put("historico",contexto);return new Preparacao(req,u.getId(),r);
 }
 public Map<String,Object> conversar(Preparacao p){return ai.chat(p.requisicao());}
 public UUID salvar(Preparacao p,Map<String,Object> resposta){var r=p.entrada();return historico.registrar(r.threadId(),p.usuarioId(),r.disciplinaId(),r.assuntoId(),r.pergunta(),resposta);}
}
