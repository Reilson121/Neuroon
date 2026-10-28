package com.Neuron.demo.disciplina;
import org.springframework.data.jpa.repository.JpaRepository;
public interface DisciplinaRepository extends JpaRepository<Disciplina,Long> { java.util.List<Disciplina> findByPeriodoIdAndAtivoTrueOrderByNomeAsc(Long periodoId); java.util.Optional<Disciplina> findByIdAndAtivoTrue(Long id); }
