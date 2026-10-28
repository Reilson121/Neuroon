package com.Neuron.demo.usuario;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.ApplicationArguments;
import org.springframework.core.env.Environment;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
@Component @RequiredArgsConstructor
public class BootstrapAdmin implements ApplicationRunner {
 private final UsuarioRepository usuarios;
 private final PasswordEncoder encoder;
 private final Environment env;
 public void run(ApplicationArguments args){
  String email=env.getProperty("NEURON_BOOTSTRAP_ADMIN_EMAIL");String senha=env.getProperty("NEURON_BOOTSTRAP_ADMIN_PASSWORD");
  if(email==null || senha==null)return;
  if(senha.length()<12)throw new IllegalStateException("Senha inicial deve conter pelo menos 12 caracteres.");
  email=email.trim().toLowerCase(java.util.Locale.ROOT);
  if(!usuarios.existsByEmail(email)){
   Usuario u=new Usuario();u.setNome("Administrador");u.setEmail(email);u.setSenhaHash(encoder.encode(senha));u.setPerfil(Perfil.ADMINISTRADOR);usuarios.save(u);
  }
 }
}
