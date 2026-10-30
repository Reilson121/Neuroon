package com.Neuron.demo;

import com.Neuron.demo.material.*;
import com.Neuron.demo.pratica.PraticaService;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class EdBasicaPraticaTests extends PraticaRulesTests {
 void prepararBasica(){
  disciplina.setSlug("estrutura_de_dados");disciplina.getPeriodo().setNumero(2);
  Material m=new Material();m.setId(9L);m.setDisciplina(disciplina);m.setTipo(TipoMaterial.SLIDE_AULA);m.setFonteMonitorVirtual(true);
  when(materiais.findByDisciplinaIdAndAtivoTrueOrderByTituloAsc(7L)).thenReturn(List.of(m));
  when(ai.montarQuestoes(anyMap())).thenReturn(Map.of("questoes",List.of()));
 }
 PraticaService.PraticaRequest geradas(){return new PraticaService.PraticaRequest(7L,null,PraticaService.Origem.MISTO,PraticaService.Modo.GERADAS_IA,5,false,PraticaService.TipoQuestao.TESTE_MESA,PraticaService.NivelContexto.DETALHADO);}
 @Test void transmitePreferenciasEFontesTeoricas(){
  prepararBasica();service.iniciarSessao(geradas(),auth);
  var c=ArgumentCaptor.forClass(Map.class);verify(ai).montarQuestoes(c.capture());
  assertEquals(Set.of(9L),c.getValue().get("material_ids"));
  assertEquals("TESTE_MESA",c.getValue().get("tipo_questao"));assertEquals("DETALHADO",c.getValue().get("nivel_contexto"));
 }
 @Test void teoriaNaoViraQuestaoOriginal(){
  prepararBasica();assertTrue(service.iniciarSessao(req(),auth).questoes().isEmpty());verify(ai,never()).montarQuestoes(anyMap());
 }
 @Test void basicaExigeSegundoPeriodo(){
  prepararBasica();disciplina.getPeriodo().setNumero(3);assertTrue(service.iniciarSessao(geradas(),auth).questoes().isEmpty());verify(ai,never()).montarQuestoes(anyMap());
 }
 @Test void avancadaNaoRecebePermissaoDaBasica(){
  prepararBasica();disciplina.setSlug("estrutura_de_dados_avancada");assertTrue(service.iniciarSessao(geradas(),auth).questoes().isEmpty());verify(ai,never()).montarQuestoes(anyMap());
 }
}
