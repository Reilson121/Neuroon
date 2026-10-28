package com.Neuron.demo;

import com.Neuron.demo.material.*;
import com.Neuron.demo.pratica.PraticaService;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class SistemasDigitaisPraticaTests extends PraticaRulesTests {
 Material teoria(){
  disciplina.setSlug("sistemas_digitais");
  Material m=new Material();m.setId(9L);m.setDisciplina(disciplina);m.setTipo(TipoMaterial.SLIDE_AULA);m.setFonteMonitorVirtual(true);
  when(materiais.findByDisciplinaIdAndAtivoTrueOrderByTituloAsc(7L)).thenReturn(List.of(m));
  when(ai.montarQuestoes(anyMap())).thenReturn(Map.of("questoes",List.of()));
  return m;
 }
 PraticaService.PraticaRequest geradas(PraticaService.Origem origem){return new PraticaService.PraticaRequest(7L,null,origem,PraticaService.Modo.GERADAS_IA,5,false);}
 @Test void teoriaGeraSomenteNoModoIaComMateriaisDisponiveis(){
  teoria();service.iniciarSessao(geradas(PraticaService.Origem.MISTO),auth);
  var captor=ArgumentCaptor.forClass(Map.class);verify(ai).montarQuestoes(captor.capture());
  assertEquals(Set.of(9L),captor.getValue().get("material_ids"));
 }
 @Test void teoriaNaoViraQuestaoOficialNemProvaOuLista(){
  teoria();assertTrue(service.iniciarSessao(req(),auth).questoes().isEmpty());
  assertTrue(service.iniciarSessao(geradas(PraticaService.Origem.LISTA),auth).questoes().isEmpty());
  assertTrue(service.iniciarSessao(geradas(PraticaService.Origem.PROVA),auth).questoes().isEmpty());
  verify(ai,never()).montarQuestoes(anyMap());
 }
 @Test void outraDisciplinaNaoRecebePermissaoDeUsarTeoria(){
  teoria();disciplina.setSlug("estatistica");
  assertTrue(service.iniciarSessao(geradas(PraticaService.Origem.MISTO),auth).questoes().isEmpty());
  verify(ai,never()).montarQuestoes(anyMap());
 }
 @Test void revogarFonteBloqueiaTeoria(){
  var m=teoria();m.setFonteMonitorVirtual(false);
  assertTrue(service.iniciarSessao(geradas(PraticaService.Origem.MISTO),auth).questoes().isEmpty());
  verify(ai,never()).montarQuestoes(anyMap());
 }
}
