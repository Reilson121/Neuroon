package com.Neuron.demo.usuario;

import java.time.LocalDateTime;
import java.time.Clock;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

@Component @EnableScheduling @RequiredArgsConstructor
public class VisitanteCleanup {
 private final JdbcTemplate jdbc;
 @Transactional public void remover(String email){
  Long id=jdbc.query("SELECT id FROM usuario WHERE email=? AND perfil='VISITANTE'",rs -> rs.next()?rs.getLong(1):null,email);
  if(id==null)return;
  jdbc.update("DELETE FROM mensagem_monitor WHERE conversa_id IN (SELECT id FROM conversa_monitor WHERE usuario_id=?)",id);
  jdbc.update("DELETE FROM conversa_monitor WHERE usuario_id=?",id);
  jdbc.update("DELETE FROM usuario WHERE id=? AND perfil='VISITANTE'",id);
 }
 @Transactional @Scheduled(fixedDelay=3600000)
 public void limparAntigos(){
  LocalDateTime limite=LocalDateTime.now(Clock.systemUTC()).minusDays(1);
  jdbc.queryForList("SELECT email FROM usuario WHERE perfil='VISITANTE' AND criado_em<?",String.class,limite)
   .forEach(this::remover);
 }
}
