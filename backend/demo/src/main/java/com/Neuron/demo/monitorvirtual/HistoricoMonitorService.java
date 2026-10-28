package com.Neuron.demo.monitorvirtual;

import com.Neuron.demo.academico.CatalogoService;
import com.Neuron.demo.common.ErroNegocio;
import com.Neuron.demo.usuario.*;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import tools.jackson.core.type.TypeReference;
import tools.jackson.databind.json.JsonMapper;
import java.time.Instant;
import java.util.*;

@Service @RequiredArgsConstructor @Transactional(readOnly=true)
public class HistoricoMonitorService {
 private final ConversaMonitorRepository conversas;
 private final MensagemMonitorRepository mensagens;
 private final UsuarioAtual usuarios;
 private final UsuarioRepository contas;
 private final CatalogoService catalogo;
 private static final JsonMapper JSON=JsonMapper.builder().build();
 public record Resumo(UUID id,String titulo,Long disciplinaId,Long assuntoId,Instant atualizadoEm){}
 public record Mensagem(Long id,String papel,String conteudo,List<Map<String,Object>> fontes,Instant criadoEm){}
 public record Detalhe(Resumo conversa,List<Mensagem> mensagens){}

 public List<Resumo> listar(Long disciplinaId,Long assuntoId,Authentication auth){
  var usuario=usuarios.exigir(auth);catalogo.exigirDisciplina(disciplinaId);catalogo.exigirAssunto(assuntoId,disciplinaId);
  return conversas.listar(usuario.getId(),disciplinaId,assuntoId,PageRequest.of(0,50)).stream().map(this::resumo).toList();
 }
 public Detalhe detalhar(UUID id,Authentication auth){
  var c=exigir(id,usuarios.exigir(auth).getId());
  catalogo.exigirDisciplina(c.getDisciplina().getId());catalogo.exigirAssunto(assuntoId(c),c.getDisciplina().getId());
  return new Detalhe(resumo(c),mensagens.findByConversaIdOrderByIdAsc(id).stream().map(m -> new Mensagem(m.getId(),m.getPapel(),m.getConteudo(),JSON.readValue(m.getFontes(),new TypeReference<List<Map<String,Object>>>(){}),m.getCriadoEm())).toList());
 }
 public void validar(UUID id,Long usuarioId,Long disciplinaId,Long assuntoId){
  if(id==null)return;
  validarContexto(exigir(id,usuarioId),disciplinaId,assuntoId);
  if(mensagens.countByConversaId(id)>=200)throw new ErroNegocio(409,"CONVERSA_COMPLETA","Esta conversa atingiu o limite. Inicie uma nova conversa.");
 }
 public List<Map<String,String>> contexto(UUID id,Long usuarioId,Long disciplinaId,Long assuntoId){
  if(id==null)return List.of();
  validar(id,usuarioId,disciplinaId,assuntoId);
  var recentes=new ArrayList<>(mensagens.findByConversaIdOrderByIdDesc(id,PageRequest.of(0,8)));
  Collections.reverse(recentes);
  return recentes.stream().map(m -> Map.of("papel",m.getPapel(),"conteudo",m.getConteudo().substring(0,Math.min(2000,m.getConteudo().length())))).toList();
 }
 @Transactional
 public UUID registrar(UUID id,Long usuarioId,Long disciplinaId,Long assuntoId,String pergunta,Map<String,Object> resposta){
  var dono=contas.findById(usuarioId).filter(Usuario::isAtivo).orElseThrow(() -> new ErroNegocio(401,"NAO_AUTENTICADO","Conta indisponível."));
  var d=catalogo.exigirDisciplina(disciplinaId);var a=catalogo.exigirAssunto(assuntoId,disciplinaId);
  var agora=Instant.now();ConversaMonitor c;
  if(id==null){
   c=new ConversaMonitor();c.setId(UUID.randomUUID());c.setUsuario(dono);c.setDisciplina(d);c.setAssunto(a);
   String titulo=pergunta.strip().replaceAll("\\s+"," ");c.setTitulo(titulo.substring(0,Math.min(100,titulo.length())));c.setCriadoEm(agora);
  }else{
   c=conversas.bloquear(id,usuarioId).orElseThrow(this::naoEncontrada);validarContexto(c,disciplinaId,assuntoId);
   if(mensagens.countByConversaId(id)>=200)throw new ErroNegocio(409,"CONVERSA_COMPLETA","Inicie uma nova conversa para continuar.");
  }
  if(!(resposta.get("resposta") instanceof String texto) || texto.isBlank())throw new IllegalStateException("Resposta do Monitor inválida.");
  c.setAtualizadoEm(agora);c=conversas.save(c);
  salvar(c,"USUARIO",pergunta.strip(),"[]",agora);
  salvar(c,"MONITOR",texto,JSON.writeValueAsString(resposta.getOrDefault("fontes",List.of())),agora);
  return c.getId();
 }
 private void salvar(ConversaMonitor c,String papel,String conteudo,String fontes,Instant agora){
  MensagemMonitor m=new MensagemMonitor();m.setConversa(c);m.setPapel(papel);m.setConteudo(conteudo);m.setFontes(fontes);m.setCriadoEm(agora);mensagens.save(m);
 }
 private ConversaMonitor exigir(UUID id,Long usuarioId){return conversas.findByIdAndUsuarioId(id,usuarioId).orElseThrow(this::naoEncontrada);}
 private ErroNegocio naoEncontrada(){return new ErroNegocio(404,"CONVERSA_NAO_ENCONTRADA","Conversa não encontrada.");}
 private Long assuntoId(ConversaMonitor c){return c.getAssunto()==null?null:c.getAssunto().getId();}
 private void validarContexto(ConversaMonitor c,Long disciplinaId,Long assuntoId){
  if(!c.getDisciplina().getId().equals(disciplinaId) || !Objects.equals(assuntoId(c),assuntoId))throw new ErroNegocio(400,"CONTEXTO_DIFERENTE","Abra uma conversa da disciplina e do assunto selecionados.");
 }
 private Resumo resumo(ConversaMonitor c){return new Resumo(c.getId(),c.getTitulo(),c.getDisciplina().getId(),assuntoId(c),c.getAtualizadoEm());}
}
