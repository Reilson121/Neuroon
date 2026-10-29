package com.Neuron.demo.usuario;

import com.Neuron.demo.common.ErroNegocio;
import jakarta.validation.constraints.*;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.nio.charset.StandardCharsets;
import java.util.*;

@Service @RequiredArgsConstructor @Transactional
public class UsuarioService {
 private final UsuarioRepository usuarios;
 private final PasswordEncoder encoder;
 public record Criar(@NotBlank @Size(max=150) String nome,
                     @NotBlank @Email @Size(max=255) String email,
                     @NotBlank @Size(min=8,max=72) String senha){
  public Criar { nome=nome==null?null:nome.trim();email=normalizar(email); }
 }
 public record Editar(@NotBlank @Size(max=150) String nome,
                      @NotBlank @Email @Size(max=255) String email,
                      @Size(max=72) String senha){
  public Editar { nome=nome==null?null:nome.trim();email=normalizar(email); }
 }
 public record Resposta(Long id,String nome,String email,String perfil) {
  static Resposta de(Usuario u){return new Resposta(u.getId(),u.getNome(),u.getEmail(),u.getPerfil().name());}
 }
 public record Lista(List<Resposta> usuarios,int pagina,int totalPaginas,long total){}
 private static String normalizar(String email){return email==null?null:email.trim().toLowerCase(Locale.ROOT);}
 public Resposta criar(Criar r){
  if(usuarios.existsByEmail(r.email()))throw new ErroNegocio(409,"EMAIL_EM_USO","Este email já está cadastrado.");
  Usuario u=new Usuario();u.setNome(r.nome());u.setEmail(r.email());u.setPerfil(Perfil.ESTUDANTE);
  u.setSenhaHash(hash(r.senha()));return Resposta.de(usuarios.saveAndFlush(u));
 }
 @Transactional(readOnly=true) public Lista listar(int pagina){
  if(pagina<0)throw new ErroNegocio(400,"PAGINA_INVALIDA","Informe uma página válida.");
  var resultado=usuarios.findByAtivoTrueAndPerfilNot(Perfil.VISITANTE,PageRequest.of(pagina,10,Sort.by("nome").ascending().and(Sort.by("id"))));
  return new Lista(resultado.getContent().stream().map(Resposta::de).toList(),pagina,resultado.getTotalPages(),resultado.getTotalElements());
 }
 @Transactional(readOnly=true) public Resposta consultar(Long id){return Resposta.de(buscar(id));}
 public Resposta editar(Long id,Editar r){
  Usuario u=buscar(id);exigirEstudante(u);
  if(usuarios.existsByEmailAndIdNot(r.email(),id))throw new ErroNegocio(409,"EMAIL_EM_USO","Este email já está cadastrado.");
  u.setNome(r.nome());u.setEmail(r.email());
  if(r.senha()!=null&&!r.senha().isEmpty())u.setSenhaHash(hash(r.senha()));
  return Resposta.de(usuarios.saveAndFlush(u));
 }
 public void excluir(Long id){Usuario u=buscar(id);exigirEstudante(u);u.desativar();usuarios.saveAndFlush(u);}
 private Usuario buscar(Long id){return usuarios.findById(id).filter(u->u.isAtivo()&&u.getPerfil()!=Perfil.VISITANTE)
  .orElseThrow(()->new ErroNegocio(404,"USUARIO_NAO_ENCONTRADO","Usuário não encontrado."));}
 private void exigirEstudante(Usuario u){if(u.getPerfil()!=Perfil.ESTUDANTE)
  throw new ErroNegocio(403,"CONTA_PROTEGIDA","Contas de administrador são protegidas neste cadastro.");}
 private String hash(String senha){
  if(senha.length()<8||senha.isBlank()||senha.getBytes(StandardCharsets.UTF_8).length>72)
   throw new ErroNegocio(400,"SENHA_INVALIDA","Use uma senha de pelo menos 8 caracteres e no máximo 72 bytes.");
  return encoder.encode(senha);
 }
}
