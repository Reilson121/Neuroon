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
class IdeacaoApiTests {
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
  aluno=new Usuario();aluno.setNome("Aluno Ideação");aluno.setEmail("ideacao@example.test");aluno.setSenhaHash("hash-teste");aluno.setPerfil(Perfil.ESTUDANTE);usuarios.save(aluno);
  Periodo p=new Periodo();p.setNumero(3);p.setNome("3º período");periodos.save(p);
  ed=new Disciplina();ed.setPeriodo(p);ed.setNome("Projeto de Ideação de Software");ed.setSlug("projeto_de_ideacao_de_software");disciplinas.save(ed);
  avl=new Assunto();avl.setDisciplina(ed);avl.setNome("Introdução");avl.setSlug("introducao");assuntos.save(avl);
  aula=new Material();aula.setDisciplina(ed);aula.setTitulo("Aula 1 — Introdução");aula.setAssunto(avl);aula.setTipo(TipoMaterial.SLIDE_AULA);aula.setFonteMonitorVirtual(true);
  aula.setReferenciaExterna("local:materiais_academicos/periodo_03/projeto_de_ideacao_de_software/aula_01_introducao/Aula 01 - Projeto de Ideao de Software.pdf");materiais.save(aula);
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
  var p=monitor.preparar(new MonitorVirtualService.ChatRequest(ed.getId(),avl.getId(),"O que é ideacao?",null),auth);
  assertEquals("projeto_de_ideacao_de_software",p.requisicao().get("disciplina"));
  assertEquals("introducao",p.requisicao().get("assunto"));
  Disciplina outra=new Disciplina();outra.setPeriodo(ed.getPeriodo());outra.setNome("Outra");outra.setSlug("outra");disciplinas.save(outra);
  assertThrows(com.Neuron.demo.common.ErroNegocio.class,()->monitor.preparar(new MonitorVirtualService.ChatRequest(outra.getId(),avl.getId(),"Ideação?",null),auth));
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
 @Test void reabreFontesDeIdeaçãoEContinuaNoMesmoAssuntoSemChamarProvedor() throws Exception {
  var auth=UsernamePasswordAuthenticationToken.authenticated(aluno.getEmail(),null,List.of());
  var entrada=monitor.preparar(new MonitorVirtualService.ChatRequest(ed.getId(),avl.getId(),"O que é ideacao?",null),auth);
  var id=monitor.salvar(entrada,Map.of("resposta","Resposta de teste local. [F1]","fallback",false,
   "fontes",List.of(Map.of("referencia","F1","arquivo","Aula 1.pdf","pagina",1,"material_id",aula.getId()))));
  mvc.perform(get("/api/v1/monitor/conversas/"+id).with(user(aluno.getEmail()).roles("ESTUDANTE")))
   .andExpect(status().isOk()).andExpect(jsonPath("$.mensagens[1].fontes[0].material_id").value(aula.getId()));
  var continuacao=monitor.preparar(new MonitorVirtualService.ChatRequest(ed.getId(),avl.getId(),"Explique melhor",id),auth);
  assertEquals("projeto_de_ideacao_de_software",continuacao.requisicao().get("disciplina"));
  assertEquals("introducao",continuacao.requisicao().get("assunto"));
  assertEquals(2,((List<?>)continuacao.requisicao().get("historico")).size());
 }
 @Test void praticaRetornaConflitoSemInventarQuestoes() throws Exception {
  mvc.perform(post("/api/v1/pratica/sessoes").with(user(aluno.getEmail()).roles("ESTUDANTE")).with(csrf()).contentType("application/json")
   .content("{\"disciplinaId\":"+ed.getId()+",\"quantidade\":5}"))
   .andExpect(status().isConflict()).andExpect(jsonPath("$.codigo").value("DISCIPLINA_SEM_PROVA"));
 }
}
