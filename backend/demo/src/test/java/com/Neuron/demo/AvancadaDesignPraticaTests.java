package com.Neuron.demo;

import com.Neuron.demo.material.*;
import com.Neuron.demo.pratica.PraticaService;
import com.Neuron.demo.common.ErroNegocio;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class AvancadaDesignPraticaTests extends PraticaRulesTests {
 void preparar(String slug){
  disciplina.setSlug(slug);disciplina.getPeriodo().setNumero(3);
  Material m=new Material();m.setId(9L);m.setDisciplina(disciplina);m.setTipo(TipoMaterial.SLIDE_AULA);m.setFonteMonitorVirtual(true);
  when(materiais.findByDisciplinaIdAndAtivoTrueOrderByTituloAsc(7L)).thenReturn(List.of(m));
  when(ai.montarQuestoes(anyMap())).thenReturn(Map.of("questoes",List.of()));
 }
 PraticaService.PraticaRequest geradas(List<Long> ids){return new PraticaService.PraticaRequest(7L,null,PraticaService.Origem.MISTO,PraticaService.Modo.GERADAS_IA,5,false,PraticaService.TipoQuestao.TESTE_MESA,PraticaService.NivelContexto.DIRETO,0,"MISTO","MISTO",ids);}
 @Test void avancadaUsaAulasDoTerceiroPeriodo(){
  preparar("estrutura_de_dados_avancada");service.iniciarSessao(geradas(List.of()),auth);
  var c=ArgumentCaptor.forClass(Map.class);verify(ai).montarQuestoes(c.capture());
  assertEquals(Set.of(9L),c.getValue().get("material_ids"));assertEquals("TESTE_MESA",c.getValue().get("tipo_questao"));assertEquals("DIRETO",c.getValue().get("nivel_contexto"));
 }
 @Test void designValidaETransmiteCadaConteudoSelecionado(){
  preparar("design_de_artefatos_digitais");service.iniciarSessao(geradas(List.of(11L,12L)),auth);
  verify(catalogo).exigirAssunto(11L,7L);verify(catalogo).exigirAssunto(12L,7L);
  var c=ArgumentCaptor.forClass(Map.class);verify(ai).montarQuestoes(c.capture());assertEquals(List.of(11L,12L),c.getValue().get("assunto_ids"));
 }
 @Test void rejeitaAssuntoDeOutraDisciplinaAntesDeGerar(){
  preparar("design_de_artefatos_digitais");when(catalogo.exigirAssunto(12L,7L)).thenThrow(new ErroNegocio(400,"ASSUNTO_DE_OUTRA_DISCIPLINA","Inválido"));
  assertThrows(ErroNegocio.class,()->service.iniciarSessao(geradas(List.of(12L)),auth));verify(ai,never()).montarQuestoes(anyMap());
 }
 @Test void teoriaContinuaSemSerProvaOriginal(){
  preparar("design_de_artefatos_digitais");assertTrue(service.iniciarSessao(req(),auth).questoes().isEmpty());verify(ai,never()).montarQuestoes(anyMap());
 }
 @Test void exigeTerceiroPeriodoEContinuaRespeitandoFonteDesativada(){
  preparar("estrutura_de_dados_avancada");disciplina.getPeriodo().setNumero(2);
  assertTrue(service.iniciarSessao(geradas(List.of()),auth).questoes().isEmpty());verify(ai,never()).montarQuestoes(anyMap());
 }
}
