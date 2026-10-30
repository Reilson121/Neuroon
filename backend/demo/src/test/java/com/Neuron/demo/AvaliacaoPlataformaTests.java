package com.Neuron.demo;

import com.Neuron.demo.avaliacao.*;
import com.Neuron.demo.usuario.*;
import jakarta.persistence.EntityManager;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.context.WebApplicationContext;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.springSecurity;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest @Transactional
class AvaliacaoPlataformaTests {
 @Autowired WebApplicationContext context;
 @Autowired UsuarioRepository usuarios;
 @Autowired AvaliacaoPlataformaRepository avaliacoes;
 @Autowired EntityManager entityManager;
 MockMvc mvc;
 final String rota="/api/v1/avaliacao-plataforma/minha";
 @BeforeEach void preparar(){
  mvc=MockMvcBuilders.webAppContextSetup(context).apply(springSecurity()).build();
  criar("aluno@example.test",Perfil.ESTUDANTE);criar("outro@example.test",Perfil.ESTUDANTE);criar("admin@example.test",Perfil.ADMINISTRADOR);
 }
 void criar(String email,Perfil perfil){Usuario u=new Usuario();u.setNome("Conta de teste");u.setEmail(email);u.setSenhaHash("hash-de-teste");u.setPerfil(perfil);usuarios.save(u);}
 @Test void exigeAutenticacaoECsrf() throws Exception {
  mvc.perform(get(rota)).andExpect(status().isUnauthorized());
  mvc.perform(put(rota).with(user("aluno@example.test").roles("ESTUDANTE")).contentType("application/json").content("{\"nota\":5}")).andExpect(status().isForbidden());
 }
 @Test void semAvaliacaoRetorna204SemBloquearCatalogo() throws Exception {
  mvc.perform(get(rota).with(user("aluno@example.test").roles("ESTUDANTE"))).andExpect(status().isNoContent());
  mvc.perform(get("/api/v1/periodos").with(user("aluno@example.test").roles("ESTUDANTE"))).andExpect(status().isOk());
 }
 @Test void salvaNaContaAutenticadaEReabreAposLimparContexto() throws Exception {
  mvc.perform(put(rota).with(user("aluno@example.test").roles("ESTUDANTE")).with(csrf()).contentType("application/json").content("{\"nota\":5,\"comentario\":\"  Ajudou nos estudos.  \",\"usuarioId\":999}"))
   .andExpect(status().isOk()).andExpect(jsonPath("$.nota").value(5)).andExpect(jsonPath("$.comentario").value("Ajudou nos estudos.")).andExpect(jsonPath("$.usuarioId").doesNotExist());
  entityManager.flush();entityManager.clear();
  mvc.perform(get(rota).with(user("aluno@example.test").roles("ESTUDANTE"))).andExpect(status().isOk()).andExpect(jsonPath("$.nota").value(5));
  mvc.perform(get(rota).with(user("outro@example.test").roles("ESTUDANTE"))).andExpect(status().isNoContent());
 }
 @Test void permiteAtualizarSemDuplicarAvaliacaoESemComentario() throws Exception {
  mvc.perform(put(rota).with(user("aluno@example.test").roles("ESTUDANTE")).with(csrf()).contentType("application/json").content("{\"nota\":3,\"comentario\":\"Bom\"}")).andExpect(status().isOk());
  mvc.perform(put(rota).with(user("aluno@example.test").roles("ESTUDANTE")).with(csrf()).contentType("application/json").content("{\"nota\":4}"))
   .andExpect(status().isOk()).andExpect(jsonPath("$.nota").value(4)).andExpect(jsonPath("$.comentario").isEmpty());
  assertEquals(1,avaliacoes.count());
 }
 @Test void validaNotasEComprimentoDoComentario() throws Exception {
  for(String entrada:new String[]{"{\"nota\":0}","{\"nota\":6}","{}","{\"nota\":4,\"comentario\":\""+"x".repeat(2001)+"\"}"}){
   mvc.perform(put(rota).with(user("aluno@example.test").roles("ESTUDANTE")).with(csrf()).contentType("application/json").content(entrada)).andExpect(status().isBadRequest());
  }
  assertEquals(0,avaliacoes.count());
 }
 @Test void administradorNaoEnviaAvaliacaoDeEstudante() throws Exception {
  mvc.perform(put(rota).with(user("admin@example.test").roles("ADMINISTRADOR")).with(csrf()).contentType("application/json").content("{\"nota\":5}"))
   .andExpect(status().isForbidden()).andExpect(jsonPath("$.codigo").value("ACESSO_NEGADO"));
 }
 @Test void consultaPublicaResumeAvaliacoesSemExporEmail() throws Exception {
  String admin="/api/v1/avaliacoes";
  mvc.perform(get(admin)).andExpect(status().isOk());
  mvc.perform(get(admin).with(user("aluno@example.test").roles("ESTUDANTE"))).andExpect(status().isOk());
  mvc.perform(get(admin))
   .andExpect(status().isOk()).andExpect(jsonPath("$.total").value(0)).andExpect(jsonPath("$.media").isEmpty());
  mvc.perform(put(rota).with(user("aluno@example.test").roles("ESTUDANTE")).with(csrf()).contentType("application/json").content("{\"nota\":5,\"comentario\":\"Ajudou\"}"));
  mvc.perform(put(rota).with(user("outro@example.test").roles("ESTUDANTE")).with(csrf()).contentType("application/json").content("{\"nota\":4}"));
  entityManager.flush();entityManager.clear();
  mvc.perform(get(admin))
   .andExpect(status().isOk()).andExpect(jsonPath("$.total").value(2)).andExpect(jsonPath("$.media").value(4.5))
   .andExpect(jsonPath("$.comComentario").value(1)).andExpect(jsonPath("$.avaliacoes[0].nota").value(4))
   .andExpect(jsonPath("$.avaliacoes[0].aluno").value("Conta de teste")).andExpect(jsonPath("$.avaliacoes[0].email").doesNotExist());
  mvc.perform(get(admin+"?pagina=-1").with(user("admin@example.test").roles("ADMINISTRADOR"))).andExpect(status().isBadRequest());
 }
}
