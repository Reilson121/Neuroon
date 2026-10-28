package com.Neuron.demo.monitorvirtual;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.time.Instant;

@Entity @Table(name="mensagem_monitor") @Getter @Setter
public class MensagemMonitor {
 @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
 @ManyToOne(fetch=FetchType.LAZY,optional=false) private ConversaMonitor conversa;
 @Column(length=12,nullable=false) private String papel;
 @Column(columnDefinition="text",nullable=false) private String conteudo;
 @Column(columnDefinition="text",nullable=false) private String fontes;
 private Instant criadoEm;
}
