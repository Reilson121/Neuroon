package com.Neuron.demo;

import com.Neuron.demo.material.*;
import com.Neuron.demo.pratica.PraticaService;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class CalculoPraticaTests extends PraticaRulesTests {
 void prepararCalculo(){
  disciplina.setSlug("calculo_para_computacao_1");disciplina.getPeriodo().setNumero(2);
  Material livro=new Material();livro.setId(91L);livro.setDisciplina(disciplina);livro.setTipo(TipoMaterial.TRECHO_LIVRO);livro.setFonteMonitorVirtual(true);
  Material tabela=new Material();tabela.setId(92L);tabela.setDisciplina(disciplina);tabela.setTipo(TipoMaterial.RESUMO);tabela.setFonteMonitorVirtual(true);
  when(materiais.findByDisciplinaIdAndAtivoTrueOrderByTituloAsc(7L)).thenReturn(List.of(livro,tabela));
  when(ai.montarQuestoes(anyMap())).thenReturn(Map.of("questoes",List.of()));
 }
 PraticaService.PraticaRequest calculo(){return new PraticaService.PraticaRequest(7L,null,PraticaService.Origem.MISTO,PraticaService.Modo.GERADAS_IA,5,false,PraticaService.TipoQuestao.MISTO,PraticaService.NivelContexto.DIRETO,2,"cadeia","RADICAL");}
 @Test void transmiteFiltrosEPermiteLivrosETabela(){
  prepararCalculo();service.iniciarSessao(calculo(),auth);
  var c=ArgumentCaptor.forClass(Map.class);verify(ai).montarQuestoes(c.capture());
  assertEquals(Set.of(91L,92L),c.getValue().get("material_ids"));
  assertEquals(2,c.getValue().get("unidade_calculo"));assertEquals("cadeia",c.getValue().get("topico_calculo"));assertEquals("RADICAL",c.getValue().get("tipo_funcao"));
 }
 @Test void livrosNaoSaoQuestoesOriginais(){prepararCalculo();assertTrue(service.iniciarSessao(req(),auth).questoes().isEmpty());verify(ai,never()).montarQuestoes(anyMap());}
 @Test void exigeSegundoPeriodo(){prepararCalculo();disciplina.getPeriodo().setNumero(3);assertTrue(service.iniciarSessao(calculo(),auth).questoes().isEmpty());verify(ai,never()).montarQuestoes(anyMap());}
 @Test void naoAutorizaLivrosDeOutraDisciplina(){prepararCalculo();disciplina.setSlug("estatistica");assertTrue(service.iniciarSessao(calculo(),auth).questoes().isEmpty());verify(ai,never()).montarQuestoes(anyMap());}
 PraticaService.PraticaRequest prova(List<Long> ids,int quantidade){return new PraticaService.PraticaRequest(7L,null,PraticaService.Origem.MISTO,PraticaService.Modo.GERADAS_IA,quantidade,false,PraticaService.TipoQuestao.MISTO,PraticaService.NivelContexto.DIRETO,0,"MISTO","MISTO",ids);}
 @Test void permiteProvaCalculoComVariosAssuntos(){
  prepararCalculo();service.iniciarSessao(prova(List.of(11L,12L),10),auth);
  var c=ArgumentCaptor.forClass(Map.class);verify(ai).montarQuestoes(c.capture());
  assertEquals(List.of(11L,12L),c.getValue().get("assunto_ids"));assertNull(c.getValue().get("assunto_id"));
  verify(catalogo).exigirAssunto(11L,7L);verify(catalogo).exigirAssunto(12L,7L);
 }
 @Test void rejeitaProvaComAssuntosRepetidosOuQuantidadeInsuficiente(){
  prepararCalculo();assertThrows(com.Neuron.demo.common.ErroNegocio.class,()->service.iniciarSessao(prova(List.of(11L,11L),10),auth));
  assertThrows(com.Neuron.demo.common.ErroNegocio.class,()->service.iniciarSessao(prova(List.of(11L,12L),1),auth));verifyNoInteractions(ai);
 }
 @Test void rejeitaAssuntoDeOutraDisciplinaNaProva(){
  prepararCalculo();when(catalogo.exigirAssunto(99L,7L)).thenThrow(new com.Neuron.demo.common.ErroNegocio(400,"ASSUNTO_DE_OUTRA_DISCIPLINA","Assunto inválido."));
  assertThrows(com.Neuron.demo.common.ErroNegocio.class,()->service.iniciarSessao(prova(List.of(11L,99L),10),auth));verifyNoInteractions(ai);
 }
}
