package com.Neuron.demo;

import com.Neuron.demo.academico.CatalogoService;
import com.Neuron.demo.common.*;
import com.Neuron.demo.disciplina.Disciplina;
import com.Neuron.demo.periodo.Periodo;
import com.Neuron.demo.material.*;
import com.Neuron.demo.pratica.PraticaService;
import com.Neuron.demo.integration.ai.AiClient;
import com.Neuron.demo.usuario.*;
import org.junit.jupiter.api.*;
import org.springframework.security.core.Authentication;
import org.springframework.transaction.*;
import org.springframework.transaction.support.SimpleTransactionStatus;
import java.util.List;
import java.util.Map;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class PraticaRulesTests {
 CatalogoService catalogo; MaterialRepository materiais; UsuarioAtual usuarios; AiClient ai; Authentication auth;
 Disciplina disciplina; Usuario usuario; PraticaService service;PlatformTransactionManager tx;
 @BeforeEach void preparar(){
  catalogo=mock(CatalogoService.class);materiais=mock(MaterialRepository.class);usuarios=mock(UsuarioAtual.class);ai=mock(AiClient.class);auth=mock(Authentication.class);
  Periodo p=new Periodo();p.setId(3L);disciplina=new Disciplina();disciplina.setId(7L);disciplina.setPeriodo(p);disciplina.setPossuiProva(true);
  usuario=new Usuario();usuario.setId(1L);usuario.setPerfil(Perfil.ESTUDANTE);
  when(usuarios.exigir(auth)).thenReturn(usuario);when(catalogo.exigirDisciplina(7L)).thenReturn(disciplina);
  when(materiais.findByDisciplinaIdAndAtivoTrueOrderByTituloAsc(7L)).thenReturn(List.of());
  tx=new PlatformTransactionManager(){public TransactionStatus getTransaction(TransactionDefinition d){return new SimpleTransactionStatus();}public void commit(TransactionStatus s){}public void rollback(TransactionStatus s){}};
  service=new PraticaService(catalogo,materiais,usuarios,new LimiteRequisicoes(30),ai,tx,60,100);
 }
 PraticaService.PraticaRequest req(){return new PraticaService.PraticaRequest(7L,null,PraticaService.Origem.MISTO,PraticaService.Modo.CADASTRADAS,5,false);}
 @Test void disciplinaSemProvaBloqueiaAntesDaIa(){
  disciplina.setPossuiProva(false);
  ErroNegocio e=assertThrows(ErroNegocio.class,()->service.iniciarSessao(req(),auth));assertEquals(409,e.getStatus());assertEquals("DISCIPLINA_SEM_PROVA",e.getCodigo());verifyNoInteractions(ai);
 }
 @Test void semMaterialElegivelRetornaVazioSemInventar(){var r=service.iniciarSessao(req(),auth);assertTrue(r.questoes().isEmpty());assertEquals("SEM_QUESTOES",r.estado());verifyNoInteractions(ai);}
 @Test void exigeAutorizacaoTipoDisponibilidadeEDisciplina(){
  Material m=new Material();m.setId(9L);m.setDisciplina(disciplina);m.setTipo(TipoMaterial.LISTA_EXERCICIOS);m.setDisponivelParaPratica(true);
  when(materiais.findByDisciplinaIdAndAtivoTrueOrderByTituloAsc(7L)).thenReturn(List.of(m));
  assertTrue(service.iniciarSessao(req(),auth).questoes().isEmpty());verifyNoInteractions(ai);
  m.setAutorizacaoProfessor(true);assertTrue(m.podeSerPratica());
  m.setTipo(TipoMaterial.SLIDE_AULA);assertFalse(m.podeSerPratica());
  m.setTipo(TipoMaterial.PROVA_ANTIGA);m.desativar();assertFalse(m.podeSerPratica());
 }
 @Test void assuntoDeOutraDisciplinaNaoChamaIa(){
  when(catalogo.exigirAssunto(90L,7L)).thenThrow(new ErroNegocio(400,"ASSUNTO_DE_OUTRA_DISCIPLINA","Assunto inválido."));
  var r=new PraticaService.PraticaRequest(7L,90L,PraticaService.Origem.MISTO,PraticaService.Modo.GERADAS_IA,5,false);
  assertEquals(400,assertThrows(ErroNegocio.class,()->service.iniciarSessao(r,auth)).getStatus());verifyNoInteractions(ai);
 }
 Material prepararQuestao(){
  Material m=new Material();m.setId(9L);m.setDisciplina(disciplina);m.setTipo(TipoMaterial.LISTA_EXERCICIOS);m.setDisponivelParaPratica(true);m.setAutorizacaoProfessor(true);
  when(materiais.findByDisciplinaIdAndAtivoTrueOrderByTituloAsc(7L)).thenReturn(List.of(m));
  var fonte=Map.of("material_id",9,"titulo_material","Lista","arquivo","lista.docx","numero_questao","1");
  var q=Map.of("id","q1","disciplina_id",7,"origem","MATERIAL_ACADEMICO","fontes",List.of(fonte),"alternativas",Map.of("A","1","B","2","C","3","D","4","E","5"),"enunciado","Calcule a média.","conceito","Média","fingerprint","questao1");
  when(ai.montarQuestoes(anyMap())).thenReturn(Map.of("questoes",List.of(q)));return m;
 }
 @Test void sessaoExpiradaNaoChamaCorrecaoDaIa(){
  prepararQuestao();service=new PraticaService(catalogo,materiais,usuarios,new LimiteRequisicoes(30),ai,tx,-1,100);
  var s=service.iniciarSessao(req(),auth);
  var e=assertThrows(ErroNegocio.class,()->service.corrigir(s.sessaoId(),new PraticaService.RespostaRequest("q1",PraticaService.Alternativa.A),auth));
  assertEquals(404,e.getStatus());verify(ai,never()).corrigir(anyMap());
 }
 @Test void revogarAutorizacaoBloqueiaCorrecaoDeSessaoExistente(){
  Material m=prepararQuestao();var s=service.iniciarSessao(req(),auth);m.setAutorizacaoProfessor(false);
  var e=assertThrows(ErroNegocio.class,()->service.corrigir(s.sessaoId(),new PraticaService.RespostaRequest("q1",PraticaService.Alternativa.A),auth));
  assertEquals("MATERIAL_INDISPONIVEL",e.getCodigo());verify(ai,never()).corrigir(anyMap());
 }
}
