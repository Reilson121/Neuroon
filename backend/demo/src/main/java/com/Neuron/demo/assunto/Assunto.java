package com.Neuron.demo.assunto;
import com.Neuron.demo.common.EntidadeAtiva;
import com.Neuron.demo.disciplina.Disciplina;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
@Entity @Table(name="assunto") @Getter @Setter
public class Assunto extends EntidadeAtiva {
 @ManyToOne(fetch=FetchType.LAZY,optional=false) @JoinColumn(name="disciplina_id") private Disciplina disciplina;
 private String nome;
 private String slug;
 @Column(columnDefinition="text") private String descricao;
 private int ordem;
}
