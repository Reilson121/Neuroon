package com.Neuron.demo.common;
public class ErroNegocio extends RuntimeException {
 private final int status;
 private final String codigo;
 public ErroNegocio(int status,String codigo,String mensagem){super(mensagem);this.status=status;this.codigo=codigo;}
 public int getStatus(){return status;}
 public String getCodigo(){return codigo;}
}
