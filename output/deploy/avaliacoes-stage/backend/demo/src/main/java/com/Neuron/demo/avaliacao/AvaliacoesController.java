package com.Neuron.demo.avaliacao;

import com.Neuron.demo.common.ErroNegocio;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.List;

@RestController @RequestMapping("/api/v1/avaliacoes") @RequiredArgsConstructor
@Transactional(readOnly=true)
public class AvaliacoesController {
 private final AvaliacaoPlataformaRepository avaliacoes;
 public record Item(Long id,String aluno,int nota,String comentario,LocalDateTime enviadoEm){}
 public record Lista(List<Item> avaliacoes,int pagina,int totalPaginas,long total,Double media,long comComentario){}
 @GetMapping public Lista listar(@RequestParam(defaultValue="0") int pagina){
  if(pagina<0)throw new ErroNegocio(400,"PAGINA_INVALIDA","Informe uma página válida.");
  var resultado=avaliacoes.findAll(PageRequest.of(pagina,10,Sort.by("criadoEm").descending().and(Sort.by("id").descending())));
  var itens=resultado.map(a->new Item(a.getId(),a.getUsuario().getNome(),a.getNota(),a.getComentario(),a.getCriadoEm())).getContent();
  return new Lista(itens,pagina,resultado.getTotalPages(),resultado.getTotalElements(),avaliacoes.media(),avaliacoes.comComentario());
 }
}
