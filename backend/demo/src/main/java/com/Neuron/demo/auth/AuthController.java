package com.Neuron.demo.auth;

import com.Neuron.demo.common.ErroNegocio;
import com.Neuron.demo.usuario.*;
import jakarta.servlet.http.*;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.*;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.context.SecurityContextRepository;
import org.springframework.security.web.authentication.session.SessionAuthenticationStrategy;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api/v1/auth") @RequiredArgsConstructor
public class AuthController {
 private final AuthenticationManager authenticationManager;
 private final SecurityContextRepository contexts;
 private final SessionAuthenticationStrategy sessionStrategy;
 private final UsuarioRepository usuarios;
 public record LoginRequest(@NotBlank @Email @Size(max=255) String email,@NotBlank @Size(max=200) String senha){}
 public record UsuarioResponse(Long id,String nome,String email,String perfil){}
 public record CsrfResponse(String headerName,String token){}
 @GetMapping("/csrf") CsrfResponse csrf(CsrfToken token){return new CsrfResponse(token.getHeaderName(),token.getToken());}
 @PostMapping("/login") UsuarioResponse login(@Valid @RequestBody LoginRequest r,HttpServletRequest req,HttpServletResponse res){
  Authentication auth=authenticationManager.authenticate(UsernamePasswordAuthenticationToken.unauthenticated(r.email().trim().toLowerCase(java.util.Locale.ROOT),r.senha()));
  sessionStrategy.onAuthentication(auth,req,res);
  var context=SecurityContextHolder.createEmptyContext();context.setAuthentication(auth);
  SecurityContextHolder.setContext(context);contexts.saveContext(context,req,res);
  return me(auth);
 }
 @GetMapping("/me") public UsuarioResponse me(Authentication a){
  Usuario u=usuarios.findByEmailAndAtivoTrue(a.getName()).orElseThrow(() -> new ErroNegocio(401,"NAO_AUTENTICADO","Conta indisponível."));
  return new UsuarioResponse(u.getId(),u.getNome(),u.getEmail(),u.getPerfil().name());
 }
}
