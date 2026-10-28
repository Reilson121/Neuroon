package com.Neuron.demo.avaliacao;

import com.Neuron.demo.usuario.Usuario;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.time.LocalDateTime;

@Entity @Table(name="feedback_plataforma") @Getter @Setter
public class AvaliacaoPlataforma {
 @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
 @ManyToOne(fetch=FetchType.LAZY,optional=false) private Usuario usuario;
 @Column(nullable=false) private Short nota;
 @Column(columnDefinition="text") private String comentario;
 @Column(nullable=false) private LocalDateTime criadoEm;
}
