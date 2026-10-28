package com.Neuron.demo.material;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/v1/admin/materiais") @RequiredArgsConstructor
public class MaterialController {
 private final MaterialService service;
 @PutMapping("/{id}") @ResponseStatus(org.springframework.http.HttpStatus.NO_CONTENT)
 void atualizar(@PathVariable Long id,@Valid @RequestBody MaterialService.MaterialRequest r,Authentication auth){service.atualizarPermissoes(id,r,auth);}
 @DeleteMapping("/{id}") @ResponseStatus(org.springframework.http.HttpStatus.NO_CONTENT)
 void desativar(@PathVariable Long id,Authentication auth){service.desativar(id,auth);}
}
