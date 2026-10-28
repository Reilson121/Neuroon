package com.Neuron.demo.monitorvirtual;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import org.springframework.security.core.Authentication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import java.util.*;
import java.util.concurrent.*;
@RestController @RequestMapping("/api/v1/monitor") @RequiredArgsConstructor
public class MonitorVirtualController {
 private final MonitorVirtualService service;
 private final ExecutorService monitorExecutor;
 @PostMapping(value="/chat",produces="text/event-stream")
 SseEmitter chat(@Valid @RequestBody MonitorVirtualService.ChatRequest r,Authentication auth){
  var req=service.preparar(r,auth);var emitter=new SseEmitter(125000L);
  monitorExecutor.submit(() -> {
   try{
    emitter.send(SseEmitter.event().name("status").data(Map.of("mensagem","Consultando os materiais da disciplina…")));
    var resposta=service.conversar(req);
    var threadId=service.salvar(req,resposta);
    emitter.send(SseEmitter.event().name("token").data(Map.of("texto",resposta.get("resposta"))));
    emitter.send(SseEmitter.event().name("sources").data(Map.of("fontes",resposta.get("fontes"))));
    emitter.send(SseEmitter.event().name("done").data(Map.of("fallback",resposta.get("fallback"),"threadId",threadId)));
    emitter.complete();
   }catch(Exception e){
    try{emitter.send(SseEmitter.event().name("error").data(Map.of("codigo","IA_INDISPONIVEL","mensagem","Não foi possível concluir a resposta. Tente novamente.")));emitter.complete();}
    catch(Exception ignored){emitter.completeWithError(new IllegalStateException("Conexão encerrada."));}
   }
  });
  return emitter;
 }
 @Configuration static class ExecutorConfig {
  @Bean(destroyMethod="shutdown") ExecutorService monitorExecutor(){return new ThreadPoolExecutor(2,4,30,TimeUnit.SECONDS,new ArrayBlockingQueue<>(32),new ThreadPoolExecutor.AbortPolicy());}
 }
}
