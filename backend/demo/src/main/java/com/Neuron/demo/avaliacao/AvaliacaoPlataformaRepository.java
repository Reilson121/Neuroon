package com.Neuron.demo.avaliacao;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface AvaliacaoPlataformaRepository extends JpaRepository<AvaliacaoPlataforma,Long> {
 Optional<AvaliacaoPlataforma> findFirstByUsuarioIdOrderByIdDesc(Long usuarioId);
}
