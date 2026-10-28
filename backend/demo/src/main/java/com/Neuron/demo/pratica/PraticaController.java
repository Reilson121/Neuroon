package com.Neuron.demo.pratica;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.Authentication;
import java.util.UUID;
@RestController @RequestMapping("/api/v1/pratica") @RequiredArgsConstructor
public class PraticaController {
 private final PraticaService service;
 @PostMapping("/sessoes") ResponseEntity<PraticaService.SessaoResponse> iniciar(@Valid @RequestBody PraticaService.PraticaRequest r,Authentication auth){var s=service.iniciarSessao(r,auth);return ResponseEntity.status(s.questoes().isEmpty()?200:201).body(s);}
 @PostMapping("/sessoes/{id}/respostas") PraticaService.CorrecaoResponse responder(@PathVariable UUID id,@Valid @RequestBody PraticaService.RespostaRequest r,Authentication auth){return service.corrigir(id,r,auth);}
}
