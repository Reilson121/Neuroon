package com.Neuron.demo.material;
import org.springframework.data.jpa.repository.JpaRepository;
public interface MaterialRepository extends JpaRepository<Material,Long> { java.util.List<Material> findByDisciplinaIdAndAtivoTrueOrderByTituloAsc(Long disciplinaId); java.util.Optional<Material> findByIdAndAtivoTrue(Long id); }
