package com.Neuron.demo.pratica;

import com.Neuron.demo.academico.CatalogoService;
import com.Neuron.demo.common.*;
import com.Neuron.demo.integration.ai.AiClient;
import com.Neuron.demo.material.*;
import com.Neuron.demo.usuario.UsuarioAtual;
import jakarta.validation.constraints.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.transaction.PlatformTransactionManager;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class PraticaService {
 public enum Origem { LISTA, PROVA, MISTO }
 public enum Modo { CADASTRADAS, GERADAS_IA }
 public enum Alternativa { A, B, C, D, E }
 public enum TipoQuestao { MISTO, CONCEITUAL, TESTE_MESA, LOGICA, ESTILO_PROFESSOR }
 public enum NivelContexto { DIRETO, COTIDIANO, DETALHADO }
 public record PraticaRequest(@NotNull @Positive Long disciplinaId,@Positive Long assuntoId,Origem origem,Modo modo,@NotNull @Min(1) @Max(10) Integer quantidade,Boolean revisarVistas,TipoQuestao tipoQuestao,NivelContexto nivelContexto,@Min(0) @Max(2) Integer unidadeCalculo,@Pattern(regexp="^[a-z_]{1,40}$|^MISTO$") String topicoCalculo,@Pattern(regexp="MISTO|AFIM|POLINOMIAL|RACIONAL|RADICAL|POR_PARTES|TRIGONOMETRICA|EXPONENCIAL|LOGARITMICA|HIPERBOLICA|IMPLICITA") String tipoFuncao,@Size(max=20) List<@NotNull @Positive Long> assuntoIds){
  public PraticaRequest(Long disciplinaId,Long assuntoId,Origem origem,Modo modo,Integer quantidade,Boolean revisarVistas,TipoQuestao tipoQuestao,NivelContexto nivelContexto,Integer unidadeCalculo,String topicoCalculo,String tipoFuncao){this(disciplinaId,assuntoId,origem,modo,quantidade,revisarVistas,tipoQuestao,nivelContexto,unidadeCalculo,topicoCalculo,tipoFuncao,List.of());}
  public PraticaRequest(Long disciplinaId,Long assuntoId,Origem origem,Modo modo,Integer quantidade,Boolean revisarVistas,TipoQuestao tipoQuestao,NivelContexto nivelContexto){this(disciplinaId,assuntoId,origem,modo,quantidade,revisarVistas,tipoQuestao,nivelContexto,0,"MISTO","MISTO");}
  public PraticaRequest(Long disciplinaId,Long assuntoId,Origem origem,Modo modo,Integer quantidade,Boolean revisarVistas){this(disciplinaId,assuntoId,origem,modo,quantidade,revisarVistas,TipoQuestao.MISTO,NivelContexto.COTIDIANO);}
  public PraticaRequest {if(origem==null)origem=Origem.MISTO;if(modo==null)modo=Modo.CADASTRADAS;if(revisarVistas==null)revisarVistas=false;if(tipoQuestao==null)tipoQuestao=TipoQuestao.MISTO;if(nivelContexto==null)nivelContexto=NivelContexto.COTIDIANO;if(unidadeCalculo==null)unidadeCalculo=0;if(topicoCalculo==null)topicoCalculo="MISTO";if(tipoFuncao==null)tipoFuncao="MISTO";assuntoIds=assuntoIds==null?List.of():List.copyOf(assuntoIds);}
 }
 public record RespostaRequest(@NotBlank @Size(max=80) String questaoId,@NotNull Alternativa alternativa){}
 public record FonteResponse(Long materialId,String tituloMaterial,String arquivo,Integer pagina,String numeroQuestao){}
 public record QuestaoResponse(String id,String enunciado,Map<String,String> alternativas,String conceito,String origem,List<FonteResponse> fontes,String aviso,String fingerprint,Map<?,?> visualizacao){}
 public record SessaoResponse(UUID sessaoId,List<QuestaoResponse> questoes,String estado,String mensagem){}
 public record CorrecaoResponse(Boolean correto,String alternativaCorreta,String conceito,String formula,String substituicao,List<String> calculos,String resolucao,List<String> errosComuns,String dica,boolean resolucaoGeradaPorIa,String origemGabarito,String aviso,List<FonteResponse> fontes){}
 private record Contexto(Long usuarioId,Long disciplinaId,Long assuntoId,Modo modo,Set<Long> materiais,Set<String> questoes,long expira){}
 private final Map<UUID,Contexto> sessoes=new ConcurrentHashMap<>();
 private final Map<Long,Deque<String>> recentes=new ConcurrentHashMap<>();
 private final CatalogoService catalogo;
 private final MaterialRepository materiais;
 private final UsuarioAtual usuarios;
 private final LimiteRequisicoes limite;
 private final AiClient ai;
 private final TransactionTemplate leitura;
 private final long ttl;
 private final int capacidade;
 public PraticaService(CatalogoService catalogo,MaterialRepository materiais,UsuarioAtual usuarios,LimiteRequisicoes limite,AiClient ai,PlatformTransactionManager tx,@Value("${neuron.practice.session-ttl-minutes:60}") int minutos,@Value("${neuron.practice.max-sessions:1000}") int capacidade){
  this.catalogo=catalogo;this.materiais=materiais;this.usuarios=usuarios;this.limite=limite;this.ai=ai;this.ttl=minutos*60000L;this.capacidade=capacidade;
  this.leitura=new TransactionTemplate(tx);this.leitura.setReadOnly(true);
 }
 private record Entrada(Long usuario,Set<Long> materiais){}
 private Entrada validar(Long disciplinaId,Long assuntoId,Origem origem,Modo modo,Authentication auth){
  return leitura.execute(status -> {
   var usuario=usuarios.exigir(auth);var d=catalogo.exigirDisciplina(disciplinaId);
   if(!d.oferecePratica())throw new ErroNegocio(409,"DISCIPLINA_SEM_PROVA","Esta disciplina não está habilitada para prática com questões.");
   catalogo.exigirAssunto(assuntoId,d.getId());
   var ids=new HashSet<Long>();
   for(var m:materiais.findByDisciplinaIdAndAtivoTrueOrderByTituloAsc(d.getId())){
    if(m.getAssunto()!=null && !m.getAssunto().isAtivo())continue;
    boolean calculo="calculo_para_computacao_1".equals(d.getSlug()) && d.getPeriodo().getNumero()==2;
    boolean tipoTeoria=calculo ? Set.of(TipoMaterial.TRECHO_LIVRO,TipoMaterial.RESUMO).contains(m.getTipo()) : m.getTipo()==TipoMaterial.SLIDE_AULA;
    boolean avancadaOuDesign=("estrutura_de_dados_avancada".equals(d.getSlug()) || "design_de_artefatos_digitais".equals(d.getSlug())) && d.getPeriodo().getNumero()==3;
    boolean teoria=modo==Modo.GERADAS_IA && origem==Origem.MISTO && (calculo || avancadaOuDesign || "sistemas_digitais".equals(d.getSlug()) || "estrutura_de_dados".equals(d.getSlug()) && d.getPeriodo().getNumero()==2) && m.isAtivo() && tipoTeoria && m.isFonteMonitorVirtual();
    if((m.podeSerPratica() || teoria) && m.assuntoPertenceADisciplina() && (assuntoId==null || m.getAssunto()==null || assuntoId.equals(m.getAssunto().getId())) &&
       (origem==Origem.MISTO || origem==Origem.LISTA && m.getTipo()==TipoMaterial.LISTA_EXERCICIOS || origem==Origem.PROVA && m.getTipo()==TipoMaterial.PROVA_ANTIGA))ids.add(m.getId());
   }
   return new Entrada(usuario.getId(),ids);
  });
 }
 public SessaoResponse iniciarSessao(PraticaRequest r,Authentication auth){
  if(!r.assuntoIds().isEmpty())leitura.execute(status -> {
   var d=catalogo.exigirDisciplina(r.disciplinaId());
   if(!"design_de_artefatos_digitais".equals(d.getSlug()) || d.getPeriodo().getNumero()!=3 || r.modo()!=Modo.GERADAS_IA || r.origem()!=Origem.MISTO || r.assuntoId()!=null)
    throw new ErroNegocio(400,"SELECAO_INVALIDA","A seleção de vários conteúdos está disponível na prática autoral de Design.");
   if(new HashSet<>(r.assuntoIds()).size()!=r.assuntoIds().size() || r.quantidade()<r.assuntoIds().size())
    throw new ErroNegocio(400,"QUANTIDADE_INSUFICIENTE","Selecione conteúdos distintos e ao menos uma questão por conteúdo.");
   r.assuntoIds().forEach(a -> catalogo.exigirAssunto(a,r.disciplinaId()));return null;
  });
  var entrada=validar(r.disciplinaId(),r.assuntoId(),r.origem(),r.modo(),auth);limite.exigir(entrada.usuario(),"pratica_iniciar");
  UUID id=UUID.randomUUID();
  if(entrada.materiais().isEmpty())return new SessaoResponse(id,List.of(),"SEM_QUESTOES","Não há materiais autorizados e disponíveis para prática nesta seleção.");
  limparExpiradas();if(sessoes.size()>=capacidade)throw new ErroNegocio(429,"LIMITE_SESSOES","Aguarde antes de iniciar outra prática.");
  Map<String,Object> req=new HashMap<>();req.put("sessao_id",id.toString());req.put("usuario_id",entrada.usuario());req.put("disciplina_id",r.disciplinaId());req.put("assunto_id",r.assuntoId());req.put("origem",r.origem().name());req.put("modo",r.modo().name());req.put("quantidade",r.quantidade());req.put("material_ids",entrada.materiais());
  req.put("tipo_questao",r.tipoQuestao().name());req.put("nivel_contexto",r.nivelContexto().name());
  req.put("assunto_ids",r.assuntoIds());
  req.put("unidade_calculo",r.unidadeCalculo());req.put("topico_calculo",r.topicoCalculo());req.put("tipo_funcao",r.tipoFuncao());
  Deque<String> vistas=recentes.computeIfAbsent(entrada.usuario(),k -> new ArrayDeque<>());
  synchronized(vistas){req.put("excluir_fingerprints",r.revisarVistas()?List.of():List.copyOf(vistas));}
  var resultado=ai.montarQuestoes(req);Object lista=resultado.get("questoes");
  if(!(lista instanceof List<?> itens) || itens.size()>r.quantidade())throw invalida();
  List<QuestaoResponse> questoes=new ArrayList<>();Set<String> ids=new HashSet<>();Set<Long> fontesUsadas=new HashSet<>();
  for(Object item:itens){
   Map<?,?> q=mapa(item);
   if(numero(q.get("disciplina_id"))!=r.disciplinaId().longValue())throw invalida();
   if(r.assuntoId()!=null && numero(q.get("assunto_id"))!=r.assuntoId().longValue())throw invalida();
   String origem=texto(q.get("origem"));
   if(!origem.equals(r.modo()==Modo.CADASTRADAS?"MATERIAL_ACADEMICO":"GERADA_IA"))throw invalida();
   List<FonteResponse> fontes=fontes(q.get("fontes"));
   if(fontes.isEmpty() || fontes.stream().anyMatch(f -> !entrada.materiais().contains(f.materialId())))throw invalida();
   fontes.forEach(f -> fontesUsadas.add(f.materialId()));
   Map<String,String> alternativas=new LinkedHashMap<>();mapa(q.get("alternativas")).forEach((k,v)->alternativas.put(texto(k),texto(v)));
   if(!alternativas.keySet().equals(Set.of("A","B","C","D","E")) || new HashSet<>(alternativas.values()).size()!=5)throw invalida();
   var questao=new QuestaoResponse(texto(q.get("id")),texto(q.get("enunciado")),alternativas,texto(q.get("conceito")),origem,fontes,opcional(q.get("aviso")),texto(q.get("fingerprint")),q.get("visualizacao")==null?null:mapa(q.get("visualizacao")));
   if(!ids.add(questao.id()))throw invalida();questoes.add(questao);
  }
  if(!questoes.isEmpty())sessoes.put(id,new Contexto(entrada.usuario(),r.disciplinaId(),r.assuntoId(),r.modo(),fontesUsadas,ids,System.currentTimeMillis()+ttl));
  synchronized(vistas){for(var q:questoes){vistas.remove(q.fingerprint());vistas.addLast(q.fingerprint());}while(vistas.size()>200)vistas.removeFirst();}
  String estado=questoes.isEmpty()?"SEM_QUESTOES":"DISPONIVEL";
  return new SessaoResponse(id,questoes,estado,questoes.isEmpty()?"Não há novas questões de múltipla escolha disponíveis nesta seleção. Você pode revisar as cadastradas.":"Questões prontas para praticar.");
 }
 public CorrecaoResponse corrigir(UUID id,RespostaRequest r,Authentication auth){
  Contexto s=sessoes.get(id);Long usuario=usuarios.exigir(auth).getId();
  if(s==null || s.expira()<System.currentTimeMillis() || !s.usuarioId().equals(usuario))throw new ErroNegocio(404,"SESSAO_NAO_ENCONTRADA","A sessão expirou ou não está disponível.");
  if(!s.questoes().contains(r.questaoId()))throw new ErroNegocio(400,"QUESTAO_FORA_DA_SESSAO","A questão não pertence à sessão.");
  var atual=validar(s.disciplinaId(),s.assuntoId(),Origem.MISTO,s.modo(),auth);
  if(!atual.materiais().containsAll(s.materiais()))throw new ErroNegocio(409,"MATERIAL_INDISPONIVEL","Os materiais desta prática não estão mais disponíveis.");
  limite.exigir(usuario,"pratica_responder");
  var body=new HashMap<String,Object>();body.put("sessao_id",id.toString());body.put("usuario_id",usuario);body.put("questao_id",r.questaoId());body.put("alternativa",r.alternativa().name());body.put("material_ids",atual.materiais());
  var c=ai.corrigir(body);Object correto=c.get("correto");if(!(correto instanceof Boolean))throw invalida();
  String alternativa=texto(c.get("alternativa_correta"));
  List<FonteResponse> fontes=fontes(c.get("fontes"));
  if(!Set.of("A","B","C","D","E").contains(alternativa) || fontes.isEmpty() || fontes.stream().anyMatch(f -> !s.materiais().contains(f.materialId())))throw invalida();
  return new CorrecaoResponse((Boolean)correto,alternativa,texto(c.get("conceito")),opcional(c.get("formula")),opcional(c.get("substituicao")),textos(c.get("calculos")),texto(c.get("resolucao")),textos(c.get("erros_comuns")),texto(c.get("dica")),Boolean.TRUE.equals(c.get("resolucao_gerada_por_ia")),texto(c.get("origem_gabarito")),opcional(c.get("aviso")),fontes);
 }
 private void limparExpiradas(){long agora=System.currentTimeMillis();sessoes.entrySet().removeIf(e -> e.getValue().expira()<agora);if(recentes.size()>capacidade*2)recentes.keySet().removeIf(u -> sessoes.values().stream().noneMatch(s -> s.usuarioId().equals(u)));}
 private static ErroNegocio invalida(){return new ErroNegocio(503,"IA_RESPOSTA_INVALIDA","O serviço de IA retornou dados que precisam ser revisados.");}
 private static Map<?,?> mapa(Object v){if(v instanceof Map<?,?> m)return m;throw invalida();}
 private static String texto(Object v){if(v instanceof String s && !s.isBlank())return s;throw invalida();}
 private static String opcional(Object v){return v==null?null:texto(v);}
 private static long numero(Object v){if(v instanceof Number n && n.longValue()>0 && Double.isFinite(n.doubleValue()) && n.doubleValue()==n.longValue())return n.longValue();throw invalida();}
 private static List<String> textos(Object v){if(!(v instanceof List<?> l))throw invalida();return l.stream().map(PraticaService::texto).toList();}
 private static List<FonteResponse> fontes(Object v){
  if(!(v instanceof List<?> l))throw invalida();return l.stream().map(x -> {var f=mapa(x);Object p=f.get("pagina");return new FonteResponse(numero(f.get("material_id")),texto(f.get("titulo_material")),opcional(f.get("arquivo")),p==null?null:(int)numero(p),opcional(f.get("numero_questao")));}).toList();
 }
}
