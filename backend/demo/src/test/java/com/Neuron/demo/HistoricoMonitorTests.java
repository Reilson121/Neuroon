package com.Neuron.demo;

import com.Neuron.demo.monitorvirtual.*;
import com.Neuron.demo.usuario.*;
import com.Neuron.demo.disciplina.*;
import com.Neuron.demo.periodo.*;
import com.Neuron.demo.assunto.*;
import com.Neuron.demo.common.ErroNegocio;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.springSecurity;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest @Transactional
class HistoricoMonitorTests {
 @Autowired HistoricoMonitorService historico;
 @Autowired MonitorVirtualService monitor;
 @Autowired UsuarioRepository usuarios;
 @Autowired PeriodoRepository periodos;
 @Autowired DisciplinaRepository disciplinas;
 @Autowired AssuntoRepository assuntos;
 @Autowired WebApplicationContext context;
 Usuario dono,outro;Disciplina disciplina;Assunto assunto;Authentication auth,outroAuth;MockMvc mvc;
 @BeforeEach void preparar(){
  dono=criarUsuario("dono@example.test");outro=criarUsuario("outro@example.test");
  auth=UsernamePasswordAuthenticationToken.authenticated(dono.getEmail(),null,List.of());
  outroAuth=UsernamePasswordAuthenticationToken.authenticated(outro.getEmail(),null,List.of());
  Periodo p=new Periodo();p.setNumero(3);p.setNome("3º período");periodos.save(p);
  disciplina=new Disciplina();disciplina.setPeriodo(p);disciplina.setNome("Estatística");disciplina.setSlug("estatistica");disciplinas.save(disciplina);
  assunto=new Assunto();assunto.setDisciplina(disciplina);assunto.setNome("Probabilidade");assunto.setSlug("probabilidade");assuntos.save(assunto);
  mvc=MockMvcBuilders.webAppContextSetup(context).apply(springSecurity()).build();
 }
 Usuario criarUsuario(String email){Usuario u=new Usuario();u.setEmail(email);u.setNome("Estudante");u.setSenhaHash("hash-de-teste");u.setPerfil(Perfil.ESTUDANTE);return usuarios.save(u);}
 Map<String,Object> resposta(){return Map.of("resposta","A probabilidade varia de 0 a 1. [F1]","fontes",List.of(Map.of("referencia","F1","arquivo","Aula 1.pdf","pagina",12,"paginas_mescladas",List.of(12,13))),"fallback",false);}
 UUID criar(){return historico.registrar(null,dono.getId(),disciplina.getId(),null,"Como funciona a probabilidade?",resposta());}
 @Test void enviaSomenteOitoMensagensRecentesEmOrdemSemFontesAntigas(){
  UUID id=criar();
  for(int i=1;i<=5;i++)historico.registrar(id,dono.getId(),disciplina.getId(),null,"Pergunta "+i,resposta());
  var req=monitor.preparar(new MonitorVirtualService.ChatRequest(disciplina.getId(),null,"Explique melhor",id),auth).requisicao();
  @SuppressWarnings("unchecked") var contexto=(List<Map<String,String>>)req.get("historico");
  assertEquals(8,contexto.size());assertEquals("Pergunta 2",contexto.get(0).get("conteudo"));
  assertEquals("MONITOR",contexto.get(7).get("papel"));
  assertTrue(contexto.stream().allMatch(m -> m.keySet().equals(Set.of("papel","conteudo"))));
  assertTrue(historico.contexto(null,dono.getId(),disciplina.getId(),null).isEmpty());
 }
 @Test void contextoNuncaAcessaOutraContaOuOutroAssuntoELimitaTexto(){
  UUID id=historico.registrar(null,dono.getId(),disciplina.getId(),null,"Pergunta longa",Map.of("resposta","x".repeat(5000),"fontes",List.of()));
  assertEquals(2000,historico.contexto(id,dono.getId(),disciplina.getId(),null).get(1).get("conteudo").length());
  assertEquals(404,assertThrows(ErroNegocio.class,()->historico.contexto(id,outro.getId(),disciplina.getId(),null)).getStatus());
  assertEquals("CONTEXTO_DIFERENTE",assertThrows(ErroNegocio.class,()->historico.contexto(id,dono.getId(),disciplina.getId(),assunto.getId())).getCodigo());
 }
 @Test void reabreHistoricoComFontesEPreservaOrdemDeVariasPerguntas(){
  UUID id=criar();historico.registrar(id,dono.getId(),disciplina.getId(),null,"Explique a fórmula.",resposta());
  var detalhe=historico.detalhar(id,auth);assertEquals(4,detalhe.mensagens().size());
  assertEquals("USUARIO",detalhe.mensagens().get(0).papel());assertEquals("MONITOR",detalhe.mensagens().get(1).papel());
  assertEquals("Explique a fórmula.",detalhe.mensagens().get(2).conteudo());
  assertEquals("Aula 1.pdf",detalhe.mensagens().get(1).fontes().get(0).get("arquivo"));
  assertEquals(List.of(12,13),detalhe.mensagens().get(1).fontes().get(0).get("paginas_mescladas"));
  assertEquals(id,historico.listar(disciplina.getId(),null,auth).get(0).id());
 }
 @Test void outroAlunoNaoListaNaoAbreNemContinuaConversa(){
  UUID id=criar();assertTrue(historico.listar(disciplina.getId(),null,outroAuth).isEmpty());
  assertEquals(404,assertThrows(ErroNegocio.class,()->historico.detalhar(id,outroAuth)).getStatus());
  assertEquals(404,assertThrows(ErroNegocio.class,()->historico.validar(id,outro.getId(),disciplina.getId(),null)).getStatus());
 }
 @Test void separaConversasPorAssuntoEBloqueiaTrocaDeContexto(){
  UUID geral=criar();UUID especifica=historico.registrar(null,dono.getId(),disciplina.getId(),assunto.getId(),"O que é um evento?",resposta());
  assertEquals(geral,historico.listar(disciplina.getId(),null,auth).get(0).id());
  assertEquals(especifica,historico.listar(disciplina.getId(),assunto.getId(),auth).get(0).id());
  assertEquals("CONTEXTO_DIFERENTE",assertThrows(ErroNegocio.class,()->historico.validar(geral,dono.getId(),disciplina.getId(),assunto.getId())).getCodigo());
 }
 @Test void apiExigeContaEProtegeHistoricoDeOutrosAlunos() throws Exception {
  UUID id=criar();mvc.perform(get("/api/v1/monitor/conversas").param("disciplinaId",disciplina.getId().toString())).andExpect(status().isUnauthorized());
  mvc.perform(get("/api/v1/monitor/conversas/"+id).with(user(outro.getEmail()))).andExpect(status().isNotFound());
  mvc.perform(get("/api/v1/monitor/conversas/"+id).with(user(dono.getEmail()))).andExpect(status().isOk()).andExpect(jsonPath("$.mensagens[1].fontes[0].arquivo").value("Aula 1.pdf"));
 }
}
