package com.Neuron.demo.material;
public enum TipoMaterial {
 SLIDE_AULA, LISTA_EXERCICIOS, PROVA_ANTIGA, RESUMO, ARQUIVO, LINK, TRECHO_LIVRO, OUTRO;
 public boolean aceitaPratica(){return this==LISTA_EXERCICIOS || this==PROVA_ANTIGA;}
}
