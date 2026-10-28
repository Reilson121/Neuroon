package com.Neuron.demo.periodo;
import org.springframework.data.jpa.repository.JpaRepository;
public interface PeriodoRepository extends JpaRepository<Periodo,Long> { java.util.List<Periodo> findByAtivoTrueOrderByOrdemAsc(); }
