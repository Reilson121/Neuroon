package com.Neuron.demo.periodo;
import com.Neuron.demo.common.EntidadeAtiva;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
@Entity @Table(name="periodo") @Getter @Setter
public class Periodo extends EntidadeAtiva {
 private int numero;
 private String nome;
 @Column(columnDefinition="text") private String descricao;
 private int ordem;
}
