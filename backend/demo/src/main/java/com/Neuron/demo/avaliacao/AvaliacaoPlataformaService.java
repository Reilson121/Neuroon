package com.Neuron.demo.avaliacao;

import com.Neuron.demo.common.ErroNegocio;
import com.Neuron.demo.usuario.*;
import jakarta.persistence.EntityManager;
import jakarta.persistence.LockModeType;
import jakarta.validation.constraints.*;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.*;

@Service @RequiredArgsConstructor @Transactional(readOnly=true)
public class AvaliacaoPlataformaService {
 private final AvaliacaoPlataformaRepository avaliacoes;
 private final UsuarioAtual usuarios;
 private final EntityManager entityManager;
 public record Entrada(@NotNull @Min(1) @Max(5) Integer nota,@Size(max=2000) String comentario){}
 public record Resposta(int nota,String comentario,LocalDateTime enviadoEm){}

 public Resposta minha(Authentication auth){
  var aluno=exigirAluno(auth);
  return avaliacoes.findFirstByUsuarioIdOrderByIdDesc(aluno.getId()).map(this::resposta).orElse(null);
 }
 @Transactional
 public Resposta salvar(Entrada entrada,Authentication auth){
  var aluno=exigirAluno(auth);
  // Serializa envios da mesma conta sem alterar a tabela de feedback existente.
  entityManager.lock(aluno,LockModeType.PESSIMISTIC_WRITE);
  var avaliacao=avaliacoes.findFirstByUsuarioIdOrderByIdDesc(aluno.getId()).orElseGet(AvaliacaoPlataforma::new);
  avaliacao.setUsuario(aluno);avaliacao.setNota(entrada.nota().shortValue());
  String comentario=entrada.comentario()==null?null:entrada.comentario().strip();
  avaliacao.setComentario(comentario==null||comentario.isEmpty()?null:comentario);
  avaliacao.setCriadoEm(LocalDateTime.now(Clock.systemUTC()));
  return resposta(avaliacoes.save(avaliacao));
 }
 private Usuario exigirAluno(Authentication auth){
  var usuario=usuarios.exigir(auth);
  if(usuario.getPerfil()!=Perfil.ESTUDANTE)throw new ErroNegocio(403,"AVALIACAO_APENAS_ESTUDANTES","A avaliação da plataforma está disponível para estudantes.");
  return usuario;
 }
 private Resposta resposta(AvaliacaoPlataforma avaliacao){return new Resposta(avaliacao.getNota(),avaliacao.getComentario(),avaliacao.getCriadoEm());}
}
