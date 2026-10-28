package com.Neuron.demo;

import com.Neuron.demo.usuario.UsuarioRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.context.WebApplicationContext;
import java.util.regex.Pattern;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.springSecurity;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest @Transactional
class VisitanteApiTests {
 @Autowired WebApplicationContext context;
 @Autowired UsuarioRepository usuarios;
 @Autowired JdbcTemplate jdbc;
 MockMvc mvc;

 @BeforeEach void preparar(){mvc=MockMvcBuilders.webAppContextSetup(context).apply(springSecurity()).build();}
 long id(String json){
  var match=Pattern.compile("\"id\":(\\d+)").matcher(json);
  assertThat(match.find()).isTrue();
  return Long.parseLong(match.group(1));
 }

 @Test void visitanteExploraSemContaMasNaoAdministra() throws Exception {
  var entrada=mvc.perform(post("/api/v1/auth/visitante").with(csrf()))
   .andExpect(status().isOk()).andExpect(jsonPath("$.perfil").value("VISITANTE"))
   .andExpect(jsonPath("$.email").isEmpty()).andReturn();
  Long id=id(entrada.getResponse().getContentAsString());
  String email=usuarios.findById(id).orElseThrow().getEmail();
  MockHttpSession sessao=(MockHttpSession)entrada.getRequest().getSession(false);
  assertThat(sessao).isNotNull();

  mvc.perform(get("/api/v1/auth/me").session(sessao)).andExpect(status().isOk())
   .andExpect(jsonPath("$.id").value(id)).andExpect(jsonPath("$.perfil").value("VISITANTE"));
  mvc.perform(get("/api/v1/periodos").session(sessao)).andExpect(status().isOk());
  mvc.perform(get("/api/v1/admin/materiais/1").session(sessao)).andExpect(status().isForbidden());
  mvc.perform(get("/api/v1/pratica/sessoes").session(sessao)).andExpect(status().isForbidden());
  mvc.perform(get("/api/v1/avaliacao-plataforma/minha").session(sessao)).andExpect(status().isForbidden());

  mvc.perform(post("/api/v1/auth/logout").session(sessao).with(csrf())).andExpect(status().isNoContent());
  assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM usuario WHERE email=?",Integer.class,email)).isZero();
 }

 @Test void cadaVisitanteRecebeUmaIdentidadeSeparada() throws Exception {
  var primeira=mvc.perform(post("/api/v1/auth/visitante").with(csrf())).andExpect(status().isOk()).andReturn();
  var segunda=mvc.perform(post("/api/v1/auth/visitante").with(csrf())).andExpect(status().isOk()).andReturn();
  long id1=id(primeira.getResponse().getContentAsString());
  long id2=id(segunda.getResponse().getContentAsString());
  assertThat(id1).isNotEqualTo(id2);
  mvc.perform(post("/api/v1/auth/logout").session((MockHttpSession)primeira.getRequest().getSession(false)).with(csrf())).andExpect(status().isNoContent());
  mvc.perform(post("/api/v1/auth/logout").session((MockHttpSession)segunda.getRequest().getSession(false)).with(csrf())).andExpect(status().isNoContent());
 }
}
