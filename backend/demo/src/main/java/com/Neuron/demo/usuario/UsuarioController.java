package com.Neuron.demo.usuario;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api/v1/admin/usuarios") @RequiredArgsConstructor
public class UsuarioController {
 private final UsuarioService service;
 private final UsuarioAtual atual;
 @GetMapping public UsuarioService.Lista listar(@RequestParam(defaultValue="0") int pagina,Authentication a){
  atual.exigirAdministrador(a);return service.listar(pagina);
 }
 @GetMapping("/{id}") public UsuarioService.Resposta consultar(@PathVariable Long id,Authentication a){
  atual.exigirAdministrador(a);return service.consultar(id);
 }
 @PostMapping @ResponseStatus(HttpStatus.CREATED)
 public UsuarioService.Resposta criar(@Valid @RequestBody UsuarioService.Criar r,Authentication a){
  atual.exigirAdministrador(a);return service.criar(r);
 }
 @PutMapping("/{id}") public UsuarioService.Resposta editar(@PathVariable Long id,@Valid @RequestBody UsuarioService.Editar r,Authentication a){
  atual.exigirAdministrador(a);return service.editar(id,r);
 }
 @DeleteMapping("/{id}") @ResponseStatus(HttpStatus.NO_CONTENT)
 public void excluir(@PathVariable Long id,Authentication a){atual.exigirAdministrador(a);service.excluir(id);}
}
