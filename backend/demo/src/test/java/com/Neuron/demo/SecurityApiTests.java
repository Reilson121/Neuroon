package com.Neuron.demo;

import com.Neuron.demo.periodo.*;
import com.Neuron.demo.disciplina.*;
import com.Neuron.demo.usuario.*;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;
import org.springframework.transaction.annotation.Transactional;
import static org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.springSecurity;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest @Transactional
class SecurityApiTests {
 @Autowired WebApplicationContext context;
 @Autowired UsuarioRepository usuarios;
 @Autowired PeriodoRepository periodos;
 @Autowired DisciplinaRepository disciplinas;
 @Autowired PasswordEncoder encoder;
 MockMvc mvc;Disciplina disciplina;
 @BeforeEach void preparar(){
  mvc=MockMvcBuilders.webAppContextSetup(context).apply(springSecurity()).build();
  Usuario u=new Usuario();u.setNome("Estudante de teste");u.setEmail("estudante@example.test");u.setSenhaHash(encoder.encode("senha-de-teste-123"));u.setPerfil(Perfil.ESTUDANTE);usuarios.save(u);
  Periodo p=new Periodo();p.setNumero(3);p.setNome("Terceiro período");periodos.save(p);
  disciplina=new Disciplina();disciplina.setPeriodo(p);disciplina.setNome("Estatística");disciplina.setSlug("estatistica");disciplina.setPossuiProva(false);disciplinas.save(disciplina);
 }
 @Test void consultaExigeAutenticacao() throws Exception {mvc.perform(get("/api/v1/periodos")).andExpect(status().isUnauthorized());}
 @Test void estudanteNaoAlteraPermissoes() throws Exception {
  mvc.perform(put("/api/v1/admin/materiais/1").with(user("estudante@example.test").roles("ESTUDANTE")).with(csrf()).contentType("application/json").content("{\"ativo\":true,\"fonteMonitorVirtual\":false,\"disponivelParaPratica\":true,\"autorizacaoProfessor\":true}")).andExpect(status().isForbidden()).andExpect(jsonPath("$.mensagem").value("Operação não autorizada."));
 }
 @Test void postExigeCsrf() throws Exception {
  mvc.perform(post("/api/v1/pratica/sessoes").with(user("estudante@example.test")).contentType("application/json").content("{}")).andExpect(status().isForbidden());
 }
 @Test void disciplinaSemProvaRetorna409() throws Exception {
  mvc.perform(post("/api/v1/pratica/sessoes").with(user("estudante@example.test")).with(csrf()).contentType("application/json").content("{\"disciplinaId\":"+disciplina.getId()+",\"quantidade\":5}")).andDo(org.springframework.test.web.servlet.result.MockMvcResultHandlers.print()).andExpect(status().isConflict()).andExpect(jsonPath("$.codigo").value("DISCIPLINA_SEM_PROVA"));
 }
 @Test void ausenciaDeMateriaisRetornaEstadoVazio() throws Exception {
  disciplina.setPossuiProva(true);disciplinas.saveAndFlush(disciplina);
  mvc.perform(post("/api/v1/pratica/sessoes").with(user("estudante@example.test")).with(csrf()).contentType("application/json").content("{\"disciplinaId\":"+disciplina.getId()+",\"quantidade\":5,\"modo\":\"GERADAS_IA\"}")).andDo(org.springframework.test.web.servlet.result.MockMvcResultHandlers.print()).andExpect(status().isOk()).andExpect(jsonPath("$.questoes").isEmpty()).andExpect(jsonPath("$.estado").value("SEM_QUESTOES"));
 }
 @Test void loginNaoExibeHashDaSenha() throws Exception {
  mvc.perform(post("/api/v1/auth/login").with(csrf()).contentType("application/json").content("{\"email\":\"estudante@example.test\",\"senha\":\"senha-de-teste-123\"}")).andExpect(status().isOk()).andExpect(jsonPath("$.perfil").value("ESTUDANTE")).andExpect(jsonPath("$.senhaHash").doesNotExist());
 }
}

