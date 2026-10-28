package com.Neuron.demo.assunto;
import org.springframework.data.jpa.repository.JpaRepository;
public interface AssuntoRepository extends JpaRepository<Assunto,Long> { java.util.List<Assunto> findByDisciplinaIdAndAtivoTrueOrderByOrdemAsc(Long disciplinaId); java.util.Optional<Assunto> findByIdAndAtivoTrue(Long id); }
