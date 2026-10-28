package com.Neuron.demo.monitorvirtual;

import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController @RequestMapping("/api/v1/monitor/conversas") @RequiredArgsConstructor
public class HistoricoMonitorController {
 private final HistoricoMonitorService historico;
 @GetMapping List<HistoricoMonitorService.Resumo> listar(@RequestParam Long disciplinaId,@RequestParam(required=false) Long assuntoId,Authentication auth){return historico.listar(disciplinaId,assuntoId,auth);}
 @GetMapping("/{id}") HistoricoMonitorService.Detalhe detalhar(@PathVariable UUID id,Authentication auth){return historico.detalhar(id,auth);}
}
