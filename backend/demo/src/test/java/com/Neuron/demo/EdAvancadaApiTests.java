package com.Neuron.demo;

import com.Neuron.demo.academico.CatalogoService;
import com.Neuron.demo.assunto.*;
import com.Neuron.demo.disciplina.*;
import com.Neuron.demo.material.*;
import com.Neuron.demo.monitorvirtual.MonitorVirtualService;
import com.Neuron.demo.periodo.*;
import com.Neuron.demo.usuario.*;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
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
class EdAvancadaApiTests {
 @Autowired CatalogoService catalogo;
 @Autowired MonitorVirtualService monitor;
 @Autowired UsuarioRepository usuarios;
 @Autowired PeriodoRepository periodos;
 @Autowired DisciplinaRepository disciplinas;
 @Autowired AssuntoRepository assuntos;
 @Autowired MaterialRepository materiais;
 @Autowired WebApplicationContext contexto;
 MockMvc mvc;Usuario aluno;Disciplina ed;Assunto avl;Material aula;
 @BeforeEach void preparar(){
  mvc=MockMvcBuilders.webAppContextSetup(contexto).apply(springSecurity()).build();
  aluno=new Usuario();aluno.setNome("Aluno ED");aluno.setEmail("ed@example.test");aluno.setSenhaHash("hash-teste");aluno.setPerfil(Perfil.ESTUDANTE);usuarios.save(aluno);
  Periodo p=new Periodo();p.setNumero(3);p.setNome("3º período");periodos.save(p);
  ed=new Disciplina();ed.setPeriodo(p);ed.setNome("Estrutura de Dados Avançada");ed.setSlug("estrutura_de_dados_avancada");disciplinas.save(ed);
  avl=new Assunto();avl.setDisciplina(ed);avl.setNome("Árvores balanceadas e AVL");avl.setSlug("arvores_balanceadas_e_avl");assuntos.save(avl);
  aula=new Material();aula.setDisciplina(ed);aula.setTitulo("Aula 2");aula.setTipo(TipoMaterial.SLIDE_AULA);aula.setFonteMonitorVirtual(true);
  aula.setReferenciaExterna("local:materiais_academicos/periodo_03/estrutura_de_dados_avancada/Aula_2.pdf");materiais.save(aula);
 }
 @Test void catalogoEntregaDisciplinaAssuntosEMateriaisSemExporCaminhos() throws Exception {
  mvc.perform(get("/api/v1/periodos/"+ed.getPeriodo().getId()+"/disciplinas").with(user(aluno.getEmail()).roles("ESTUDANTE")))
   .andExpect(status().isOk()).andExpect(jsonPath("$[0].nome").value(ed.getNome())).andExpect(jsonPath("$[0].possuiProva").value(false));
  mvc.perform(get("/api/v1/disciplinas/"+ed.getId()+"/materiais").with(user(aluno.getEmail()).roles("ESTUDANTE")))
   .andExpect(status().isOk()).andExpect(jsonPath("$[0].arquivoDisponivel").value(true)).andExpect(jsonPath("$[0].referenciaExterna").doesNotExist());
  assertEquals(avl.getId(),catalogo.assuntos(ed.getId()).get(0).id());
 }
 @Test void monitorTraduzIdsParaSlugsERecusaAssuntoDeOutraDisciplina(){
  var auth=UsernamePasswordAuthenticationToken.authenticated(aluno.getEmail(),null,List.of());
  var p=monitor.preparar(new MonitorVirtualService.ChatRequest(ed.getId(),avl.getId(),"Como funciona AVL?",null),auth);
  assertEquals("estrutura_de_dados_avancada",p.requisicao().get("disciplina"));
  assertEquals("arvores_balanceadas_e_avl",p.requisicao().get("assunto"));
  Disciplina outra=new Disciplina();outra.setPeriodo(ed.getPeriodo());outra.setNome("Outra");outra.setSlug("outra");disciplinas.save(outra);
  assertThrows(com.Neuron.demo.common.ErroNegocio.class,()->monitor.preparar(new MonitorVirtualService.ChatRequest(outra.getId(),avl.getId(),"AVL?",null),auth));
 }
 @Test void arquivoExigeContaERevogacaoBloqueiaAcesso() throws Exception {
  String url="/api/v1/materiais/"+aula.getId()+"/arquivo";
  mvc.perform(get(url)).andExpect(status().isUnauthorized());
  mvc.perform(get(url).with(user(aluno.getEmail()).roles("ESTUDANTE"))).andExpect(status().isOk()).andExpect(content().contentType("application/pdf"))
   .andExpect(header().string("Cache-Control","no-store"));
  aula.desativar();materiais.save(aula);
  mvc.perform(get(url).with(user(aluno.getEmail()).roles("ESTUDANTE"))).andExpect(status().isNotFound());
 }
 @Test void arquivoNaoPermiteSairDaPastaDeMateriais() throws Exception {
  aula.setReferenciaExterna("local:materiais_academicos/../../docs/referencias/NEURON_Diagrama_de_Classes.pdf");materiais.save(aula);
  mvc.perform(get("/api/v1/materiais/"+aula.getId()+"/arquivo").with(user(aluno.getEmail()).roles("ESTUDANTE"))).andExpect(status().isNotFound());
 }
 @Test void praticaRetornaConflitoSemInventarQuestoes() throws Exception {
  mvc.perform(post("/api/v1/pratica/sessoes").with(user(aluno.getEmail()).roles("ESTUDANTE")).with(csrf()).contentType("application/json")
   .content("{\"disciplinaId\":"+ed.getId()+",\"quantidade\":5}"))
   .andExpect(status().isConflict()).andExpect(jsonPath("$.codigo").value("DISCIPLINA_SEM_PROVA"));
 }
}
