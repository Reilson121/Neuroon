package com.Neuron.demo.material;
import com.Neuron.demo.common.EntidadeAtiva;
import com.Neuron.demo.disciplina.Disciplina;
import com.Neuron.demo.assunto.Assunto;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
@Entity @Table(name="material") @Getter @Setter
public class Material extends EntidadeAtiva {
 @ManyToOne(fetch=FetchType.LAZY,optional=false) @JoinColumn(name="disciplina_id") private Disciplina disciplina;
 @ManyToOne(fetch=FetchType.LAZY) @JoinColumn(name="assunto_id") private Assunto assunto;
 private String titulo;
 @Column(columnDefinition="text") private String descricao;
 @Enumerated(EnumType.STRING) private TipoMaterial tipo;
 @Column(columnDefinition="text") private String referenciaExterna;
 private boolean fonteMonitorVirtual;
 private boolean disponivelParaPratica;
 private boolean contemGabarito;
 private boolean autorizacaoProfessor;
 public boolean assuntoPertenceADisciplina(){return assunto==null || disciplina.getId().equals(assunto.getDisciplina().getId());}
 public boolean podeSerPratica(){return ativo && disciplina.oferecePratica() && tipo.aceitaPratica() && autorizacaoProfessor && disponivelParaPratica;}
}
