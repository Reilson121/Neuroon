package com.Neuron.demo;

import com.Neuron.demo.integration.ai.AiClient;
import com.Neuron.demo.common.ErroNegocio;
import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

class AiClientTests {
 HttpServer server;AiClient client;String body;int status;
 @BeforeEach void preparar() throws Exception {
  server=HttpServer.create(new InetSocketAddress("127.0.0.1",0),0);
  server.createContext("/internal/v1/practice/answers",exchange -> {
   assertEquals("chave-teste",exchange.getRequestHeaders().getFirst("X-Internal-Token"));
   exchange.getRequestBody().readAllBytes();
   byte[] bytes=body.getBytes(StandardCharsets.UTF_8);
   exchange.getResponseHeaders().set("Content-Type","application/json");exchange.sendResponseHeaders(status,bytes.length);
   try(var out=exchange.getResponseBody()){out.write(bytes);}
  });server.start();client=new AiClient("http://127.0.0.1:"+server.getAddress().getPort(),"chave-teste");
 }
 @AfterEach void encerrar(){server.stop(0);}
 @Test void preservaConflitoDeRespostaSemRefletirMensagemInterna(){
  status=409;body="{\"detail\":{\"codigo\":\"RESPOSTA_JA_REGISTRADA\",\"mensagem\":\"SENTINELA_PRIVADA\"}}";
  var e=assertThrows(ErroNegocio.class,()->client.corrigir(Map.of()));
  assertEquals(409,e.getStatus());assertEquals("RESPOSTA_JA_REGISTRADA",e.getCodigo());assertFalse(e.getMessage().contains("SENTINELA_PRIVADA"));
 }
 @Test void preservaSessaoExpirada(){
  status=404;body="{\"detail\":{\"codigo\":\"SESSAO_NAO_ENCONTRADA\"}}";
  assertEquals(404,assertThrows(ErroNegocio.class,()->client.corrigir(Map.of())).getStatus());
 }
 @Test void sanitizaFalhaDesconhecida(){
  status=500;body="{\"detail\":\"SENTINELA_PRIVADA\"}";
  var e=assertThrows(ErroNegocio.class,()->client.corrigir(Map.of()));assertEquals(503,e.getStatus());assertFalse(e.getMessage().contains("SENTINELA_PRIVADA"));
 }
 @Test void encaminhaSucesso(){status=200;body="{\"correto\":true}";assertEquals(Boolean.TRUE,client.corrigir(Map.of()).get("correto"));}
}
