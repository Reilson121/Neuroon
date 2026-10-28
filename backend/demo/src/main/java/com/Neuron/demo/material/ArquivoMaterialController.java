package com.Neuron.demo.material;

import lombok.RequiredArgsConstructor;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api/v1/materiais") @RequiredArgsConstructor
public class ArquivoMaterialController {
 private final ArquivoMaterialService arquivos;
 @GetMapping("/{id}/arquivo")
 ResponseEntity<FileSystemResource> abrir(@PathVariable Long id,Authentication auth){return arquivos.abrir(id,auth);}
}
