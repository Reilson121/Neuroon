package com.Neuron.demo.avaliacao;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api/v1/avaliacao-plataforma/minha") @RequiredArgsConstructor
public class AvaliacaoPlataformaController {
 private final AvaliacaoPlataformaService service;
 @GetMapping ResponseEntity<AvaliacaoPlataformaService.Resposta> minha(Authentication auth){
  var atual=service.minha(auth);return atual==null?ResponseEntity.noContent().build():ResponseEntity.ok(atual);
 }
 @PutMapping AvaliacaoPlataformaService.Resposta salvar(@Valid @RequestBody AvaliacaoPlataformaService.Entrada entrada,Authentication auth){return service.salvar(entrada,auth);}
}
