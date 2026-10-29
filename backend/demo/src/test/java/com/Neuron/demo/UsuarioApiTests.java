package com.Neuron.demo;

import com.Neuron.demo.usuario.*;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.context.WebApplicationContext;
import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.springSecurity;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest @Transactional
class UsuarioApiTests {
 @Autowired WebApplicationContext context;
 @Autowired UsuarioRepository usuarios;
 @Autowired PasswordEncoder encoder;
 MockMvc mvc;Usuario admin;
 private static final String DADOS="{\"nome\":\" Ana Silva \",\"email\":\" ANA@EXAMPLE.TEST \",\"senha\":\"senha-segura-123\",\"perfil\":\"ADMINISTRADOR\"}";
 @BeforeEach void preparar(){
  mvc=MockMvcBuilders.webAppContextSetup(context).apply(springSecurity()).build();
  admin=new Usuario();admin.setNome("Admin");admin.setEmail("admin-crud@example.test");admin.setSenhaHash(encoder.encode("senha-admin-123"));admin.setPerfil(Perfil.ADMINISTRADOR);usuarios.saveAndFlush(admin);
 }
 @Test void cadastroPublicoNormalizaProtegeSenhaEPermiteLogin() throws Exception {
  mvc.perform(post("/api/v1/auth/cadastro").with(csrf()).contentType("application/json").content(DADOS))
   .andExpect(status().isCreated()).andExpect(jsonPath("$.nome").value("Ana Silva"))
   .andExpect(jsonPath("$.email").value("ana@example.test")).andExpect(jsonPath("$.perfil").value("ESTUDANTE"))
   .andExpect(jsonPath("$.senhaHash").doesNotExist()).andExpect(jsonPath("$.senha").doesNotExist());
  var u=usuarios.findByEmailAndAtivoTrue("ana@example.test").orElseThrow();
  assertThat(encoder.matches("senha-segura-123",u.getSenhaHash())).isTrue();
  mvc.perform(post("/api/v1/auth/login").with(csrf()).contentType("application/json").content("{\"email\":\"ana@example.test\",\"senha\":\"senha-segura-123\"}"))
   .andExpect(status().isOk());
 }
 @Test void validaDadosDuplicidadeECsrf() throws Exception {
  mvc.perform(post("/api/v1/auth/cadastro").contentType("application/json").content(DADOS)).andExpect(status().isForbidden());
  mvc.perform(post("/api/v1/auth/cadastro").with(csrf()).contentType("application/json").content("{\"nome\":\" \",\"email\":\"invalido\",\"senha\":\"123\"}"))
   .andExpect(status().isBadRequest());
  mvc.perform(post("/api/v1/auth/cadastro").with(csrf()).contentType("application/json").content(DADOS)).andExpect(status().isCreated());
  mvc.perform(post("/api/v1/auth/cadastro").with(csrf()).contentType("application/json").content(DADOS)).andExpect(status().isConflict());
 }
 @Test void administradorExecutaCrudEExclusaoBloqueiaSessao() throws Exception {
  var auth=user(admin.getEmail()).roles("ADMINISTRADOR");
  mvc.perform(post("/api/v1/admin/usuarios").with(auth).with(csrf()).contentType("application/json").content(DADOS)).andExpect(status().isCreated());
  var u=usuarios.findByEmailAndAtivoTrue("ana@example.test").orElseThrow();Long id=u.getId();String hash=u.getSenhaHash();
  mvc.perform(get("/api/v1/admin/usuarios").with(auth)).andExpect(status().isOk()).andExpect(jsonPath("$.total").value(2));
  mvc.perform(get("/api/v1/admin/usuarios/"+id).with(auth)).andExpect(status().isOk()).andExpect(jsonPath("$.nome").value("Ana Silva"));
  mvc.perform(put("/api/v1/admin/usuarios/"+id).with(auth).with(csrf()).contentType("application/json").content("{\"nome\":\"Ana Souza\",\"email\":\"ana@example.test\",\"senha\":\"\"}"))
   .andExpect(status().isOk()).andExpect(jsonPath("$.nome").value("Ana Souza"));
  assertThat(usuarios.findById(id).orElseThrow().getSenhaHash()).isEqualTo(hash);
  mvc.perform(delete("/api/v1/admin/usuarios/"+id).with(auth).with(csrf())).andExpect(status().isNoContent());
  assertThat(usuarios.findById(id).orElseThrow().isAtivo()).isFalse();
  mvc.perform(get("/api/v1/periodos").with(user(u.getEmail()).roles("ESTUDANTE"))).andExpect(status().isUnauthorized());
  mvc.perform(get("/api/v1/admin/usuarios/"+id).with(auth)).andExpect(status().isNotFound());
  mvc.perform(post("/api/v1/auth/login").with(csrf()).contentType("application/json").content("{\"email\":\"ana@example.test\",\"senha\":\"senha-segura-123\"}"))
   .andExpect(status().isUnauthorized());
 }
 @Test void restringeAcessoEProtegeAdministrador() throws Exception {
  mvc.perform(get("/api/v1/admin/usuarios")).andExpect(status().isUnauthorized());
  Usuario u=new Usuario();u.setNome("Aluno");u.setEmail("aluno-crud@example.test");u.setSenhaHash("hash");u.setPerfil(Perfil.ESTUDANTE);usuarios.saveAndFlush(u);
  mvc.perform(get("/api/v1/admin/usuarios").with(user(u.getEmail()).roles("ESTUDANTE"))).andExpect(status().isForbidden());
  mvc.perform(delete("/api/v1/admin/usuarios/"+admin.getId()).with(user(admin.getEmail()).roles("ADMINISTRADOR")).with(csrf())).andExpect(status().isForbidden());
 }
 @Test void edicaoValidaEmailESenhaEAtualizaHash() throws Exception {
  mvc.perform(post("/api/v1/auth/cadastro").with(csrf()).contentType("application/json").content(DADOS)).andExpect(status().isCreated());
  var u=usuarios.findByEmailAndAtivoTrue("ana@example.test").orElseThrow();
  var auth=user(admin.getEmail()).roles("ADMINISTRADOR");String rota="/api/v1/admin/usuarios/"+u.getId();
  mvc.perform(put(rota).with(auth).with(csrf()).contentType("application/json").content("{\"nome\":\"Ana\",\"email\":\"admin-crud@example.test\",\"senha\":\"\"}"))
   .andExpect(status().isConflict());
  mvc.perform(put(rota).with(auth).with(csrf()).contentType("application/json").content("{\"nome\":\"Ana\",\"email\":\"ana@example.test\",\"senha\":\"curta\"}"))
   .andExpect(status().isBadRequest());
  mvc.perform(put(rota).with(auth).with(csrf()).contentType("application/json").content("{\"nome\":\"Ana\",\"email\":\"nova@example.test\",\"senha\":\"nova-senha-123\"}"))
   .andExpect(status().isOk());
  assertThat(encoder.matches("nova-senha-123",usuarios.findById(u.getId()).orElseThrow().getSenhaHash())).isTrue();
 }
 @Test void sessaoNaoAssumeOutraContaQuandoEmailEReutilizado() throws Exception {
  mvc.perform(post("/api/v1/auth/cadastro").with(csrf()).contentType("application/json").content(DADOS)).andExpect(status().isCreated());
  var login=mvc.perform(post("/api/v1/auth/login").with(csrf()).contentType("application/json")
   .content("{\"email\":\"ana@example.test\",\"senha\":\"senha-segura-123\"}")).andExpect(status().isOk()).andReturn();
  var sessao=(org.springframework.mock.web.MockHttpSession)login.getRequest().getSession(false);
  var u=usuarios.findByEmailAndAtivoTrue("ana@example.test").orElseThrow();u.setEmail("novo-email@example.test");usuarios.saveAndFlush(u);
  Usuario outra=new Usuario();outra.setNome("Outra pessoa");outra.setEmail("ana@example.test");outra.setSenhaHash("hash");outra.setPerfil(Perfil.ESTUDANTE);usuarios.saveAndFlush(outra);
  mvc.perform(get("/api/v1/auth/me").session(sessao)).andExpect(status().isUnauthorized());
 }
}
