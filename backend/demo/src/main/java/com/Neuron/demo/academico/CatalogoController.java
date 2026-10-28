package com.Neuron.demo.academico;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;
@RestController @RequestMapping("/api/v1") @RequiredArgsConstructor
public class CatalogoController {
 private final CatalogoService catalogo;
 @GetMapping("/periodos") List<CatalogoService.PeriodoResponse> periodos(){return catalogo.periodos();}
 @GetMapping("/periodos/{id}/disciplinas") List<CatalogoService.DisciplinaResponse> disciplinas(@PathVariable Long id){return catalogo.disciplinas(id);}
 @GetMapping("/disciplinas/{id}") CatalogoService.DisciplinaResponse disciplina(@PathVariable Long id){return catalogo.detalhar(id);}
 @GetMapping("/disciplinas/{id}/assuntos") List<CatalogoService.AssuntoResponse> assuntos(@PathVariable Long id){return catalogo.assuntos(id);}
 @GetMapping("/disciplinas/{id}/materiais") List<CatalogoService.MaterialResponse> materiais(@PathVariable Long id,@RequestParam(required=false) Long assuntoId){return catalogo.materiais(id,assuntoId);}
}
