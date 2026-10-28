package com.Neuron.demo.monitorvirtual;

import com.Neuron.demo.usuario.Usuario;
import com.Neuron.demo.disciplina.Disciplina;
import com.Neuron.demo.assunto.Assunto;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.time.Instant;
import java.util.UUID;

@Entity @Table(name="conversa_monitor") @Getter @Setter
public class ConversaMonitor {
 @Id private UUID id;
 @ManyToOne(fetch=FetchType.LAZY,optional=false) private Usuario usuario;
 @ManyToOne(fetch=FetchType.LAZY,optional=false) private Disciplina disciplina;
 @ManyToOne(fetch=FetchType.LAZY) private Assunto assunto;
 @Column(length=100,nullable=false) private String titulo;
 private Instant criadoEm;
 private Instant atualizadoEm;
}
