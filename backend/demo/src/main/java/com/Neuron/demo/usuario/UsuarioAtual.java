package com.Neuron.demo.usuario;
import com.Neuron.demo.common.ErroNegocio;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;
@Service @RequiredArgsConstructor
public class UsuarioAtual {
 private final UsuarioRepository usuarios;
 public Usuario exigir(Authentication a){
  if(a==null || !a.isAuthenticated())throw new ErroNegocio(401,"NAO_AUTENTICADO","Entre na sua conta.");
  return usuarios.findByEmailAndAtivoTrue(a.getName()).orElseThrow(() -> new ErroNegocio(401,"NAO_AUTENTICADO","Conta indisponível."));
 }
 public Usuario exigirAdministrador(Authentication a){
  Usuario u=exigir(a);if(!u.ehAdministrador())throw new ErroNegocio(403,"ACESSO_NEGADO","Operação administrativa.");return u;
 }
}
