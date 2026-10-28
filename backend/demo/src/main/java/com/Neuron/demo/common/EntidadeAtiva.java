package com.Neuron.demo.common;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.time.LocalDateTime;
import java.time.Clock;
@MappedSuperclass @Getter @Setter
public abstract class EntidadeAtiva {
 @Id @GeneratedValue(strategy=GenerationType.IDENTITY) protected Long id;
 protected boolean ativo = true;
 protected LocalDateTime criadoEm;
 protected LocalDateTime atualizadoEm;
 @PrePersist void criar(){ criadoEm=LocalDateTime.now(Clock.systemUTC()); atualizadoEm=criadoEm; }
 @PreUpdate void atualizar(){ atualizadoEm=LocalDateTime.now(Clock.systemUTC()); }
 public void desativar(){ ativo=false; }
}
