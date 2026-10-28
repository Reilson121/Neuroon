package com.Neuron.demo.usuario;
import com.Neuron.demo.common.EntidadeAtiva;
import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
@Entity @Table(name="usuario") @Getter @Setter
public class Usuario extends EntidadeAtiva {
 private String nome;
 private String email;
 @JsonIgnore private String senhaHash;
 @Enumerated(EnumType.STRING) private Perfil perfil;
 public boolean ehAdministrador(){return ativo && perfil==Perfil.ADMINISTRADOR;}
}
