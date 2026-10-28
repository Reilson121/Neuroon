package com.Neuron.demo.integration.ai;
import com.Neuron.demo.common.ErroNegocio;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import java.time.Duration;
import java.util.Map;
@Component
public class AiClient {
 private final WebClient http;
 private final String token;
 public AiClient(@Value("${ai-service.base-url}") String url,@Value("${ai-service.token}") String token){
  this.token=token;this.http=WebClient.builder().baseUrl(url).defaultHeader("X-Internal-Token",token).build();
 }
 private Map<String,Object> post(String path,Map<String,Object> body){
  if(token==null || token.isBlank())throw new ErroNegocio(503,"IA_NAO_CONFIGURADA","O serviço interno de IA não está configurado.");
  try{
   Map<String,Object> r=http.post().uri(path).bodyValue(body).retrieve()
    .onStatus(s -> s.isError(),res -> res.bodyToMono(new ParameterizedTypeReference<Map<String,Object>>(){}).map(AiClient::erroInterno).defaultIfEmpty(indisponivel()).onErrorReturn(indisponivel()))
    .bodyToMono(new ParameterizedTypeReference<Map<String,Object>>(){}).block(Duration.ofSeconds(120));
   if(r==null)throw new IllegalStateException("Resposta vazia.");return r;
  }catch(ErroNegocio e){throw e;}catch(Exception e){throw new ErroNegocio(503,"IA_INDISPONIVEL","Não foi possível concluir a operação no serviço de IA.");}
 }
 private static ErroNegocio indisponivel(){return new ErroNegocio(503,"IA_INDISPONIVEL","Não foi possível concluir a operação no serviço de IA.");}
 private static ErroNegocio erroInterno(Map<String,Object> corpo){
  Object detalhe=corpo.get("detail");Object codigo=detalhe instanceof Map<?,?> m?m.get("codigo"):null;
  if(!(codigo instanceof String c))return indisponivel();
  // Mensagens públicas próprias: nenhum texto do provedor é refletido.
  return switch(c){
   case "SESSAO_NAO_ENCONTRADA" -> new ErroNegocio(404,c,"A sessão expirou ou não está disponível.");
   case "QUESTAO_NAO_ENCONTRADA" -> new ErroNegocio(404,c,"A questão não pertence à sessão.");
   case "MATERIAL_INDISPONIVEL" -> new ErroNegocio(409,c,"Os materiais desta prática não estão mais disponíveis.");
   case "RESPOSTA_JA_REGISTRADA" -> new ErroNegocio(409,c,"Esta questão já foi respondida.");
   case "SESSAO_EXISTENTE" -> new ErroNegocio(409,c,"Esta sessão já foi iniciada.");
   case "LIMITE_SESSOES" -> new ErroNegocio(429,c,"Aguarde antes de iniciar outra prática.");
   case "MATERIAL_NAO_PREPARADO" -> new ErroNegocio(409,c,"O material precisa ser preparado e validado antes da indexação.");
   default -> indisponivel();
  };
 }
 public Map<String,Object> chat(Map<String,Object> req){return post("/internal/v1/chat",req);}
 public Map<String,Object> montarQuestoes(Map<String,Object> req){return post("/internal/v1/practice/questions",req);}
 public Map<String,Object> corrigir(Map<String,Object> req){return post("/internal/v1/practice/answers",req);}
 public void indexar(Long id){post("/internal/v1/materials/index",Map.of("material_id",id));}
 public void remover(Long id){
  if(token==null || token.isBlank())throw new ErroNegocio(503,"IA_NAO_CONFIGURADA","Serviço interno não configurado.");
  try{http.delete().uri("/internal/v1/materials/{id}",id).retrieve().toBodilessEntity().block(Duration.ofSeconds(20));}
  catch(Exception e){throw new ErroNegocio(503,"INDICE_PENDENTE","O material foi desativado, mas a limpeza do índice precisa ser repetida.");}
 }
}
