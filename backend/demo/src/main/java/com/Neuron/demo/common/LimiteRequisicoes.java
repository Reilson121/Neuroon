package com.Neuron.demo.common;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import java.util.concurrent.ConcurrentHashMap;
@Component
public class LimiteRequisicoes {
 private record Janela(long inicio,int usadas){}
 private final ConcurrentHashMap<String,Janela> janelas=new ConcurrentHashMap<>();
 private final int limite;
 public LimiteRequisicoes(@Value("${neuron.rate-limit.por-minuto:30}") int limite){this.limite=limite;}
 public void exigir(Long usuario,String operacao){
  long agora=System.currentTimeMillis();
  if(janelas.size()>10000)janelas.entrySet().removeIf(e -> agora-e.getValue().inicio()>60000);
  String chave=usuario+":"+operacao;
  janelas.compute(chave,(k,v) -> {
   if(v==null || agora-v.inicio()>60000)return new Janela(agora,1);
   if(v.usadas()>=limite)throw new ErroNegocio(429,"LIMITE_REQUISICOES","Aguarde um momento antes de tentar novamente.");
   return new Janela(v.inicio(),v.usadas()+1);
  });
 }
}
