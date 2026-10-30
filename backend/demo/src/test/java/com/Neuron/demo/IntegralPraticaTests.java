package com.Neuron.demo;

import com.Neuron.demo.material.*;
import com.Neuron.demo.pratica.PraticaService;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class IntegralPraticaTests extends PraticaRulesTests {
 void prepararIntegral(){
  disciplina.setSlug("calculo_para_computacao_2");disciplina.getPeriodo().setNumero(3);
  Material guia=new Material();guia.setId(201L);guia.setDisciplina(disciplina);guia.setTipo(TipoMaterial.RESUMO);guia.setFonteMonitorVirtual(true);
  when(materiais.findByDisciplinaIdAndAtivoTrueOrderByTituloAsc(7L)).thenReturn(List.of(guia));
  when(ai.montarQuestoes(anyMap())).thenReturn(Map.of("questoes",List.of()));
 }
 PraticaService.PraticaRequest integral(List<Long> ids){return new PraticaService.PraticaRequest(7L,null,PraticaService.Origem.MISTO,PraticaService.Modo.GERADAS_IA,10,false,PraticaService.TipoQuestao.MISTO,PraticaService.NivelContexto.DIRETO,1,"integral_definida","POLINOMIAL",ids);}
 @Test void permiteApoioAutoralETransmiteFiltro(){
  prepararIntegral();service.iniciarSessao(integral(List.of()),auth);
  var c=ArgumentCaptor.forClass(Map.class);verify(ai).montarQuestoes(c.capture());
  assertEquals(Set.of(201L),c.getValue().get("material_ids"));assertEquals(1,c.getValue().get("unidade_calculo"));assertEquals("integral_definida",c.getValue().get("topico_calculo"));
 }
 @Test void permiteSimuladoPorAssuntos(){prepararIntegral();service.iniciarSessao(integral(List.of(11L,12L)),auth);verify(catalogo).exigirAssunto(11L,7L);verify(ai).montarQuestoes(anyMap());}
 @Test void naoPermiteOutroPeriodo(){prepararIntegral();disciplina.getPeriodo().setNumero(2);assertTrue(service.iniciarSessao(integral(List.of()),auth).questoes().isEmpty());verifyNoInteractions(ai);}
}

