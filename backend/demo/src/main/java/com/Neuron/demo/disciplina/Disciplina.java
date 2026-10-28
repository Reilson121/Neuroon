package com.Neuron.demo.disciplina;
import com.Neuron.demo.common.EntidadeAtiva;
import com.Neuron.demo.periodo.Periodo;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
@Entity @Table(name="disciplina") @Getter @Setter
public class Disciplina extends EntidadeAtiva {
 @ManyToOne(fetch=FetchType.LAZY,optional=false) @JoinColumn(name="periodo_id") private Periodo periodo;
 private String nome;
 private String slug;
 @Column(columnDefinition="text") private String descricao;
 @Column(columnDefinition="text") private String dicas;
 private boolean possuiProva;
 public boolean oferecePratica(){return ativo && periodo.isAtivo() && possuiProva;}
}
