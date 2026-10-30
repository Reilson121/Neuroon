package com.Neuron.demo.avaliacao;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.Query;

public interface AvaliacaoPlataformaRepository extends JpaRepository<AvaliacaoPlataforma,Long> {
 Optional<AvaliacaoPlataforma> findFirstByUsuarioIdOrderByIdDesc(Long usuarioId);
 @EntityGraph(attributePaths="usuario")
 Page<AvaliacaoPlataforma> findAll(Pageable pagina);
 @Query("select avg(a.nota) from AvaliacaoPlataforma a")
 Double media();
 @Query("select count(a) from AvaliacaoPlataforma a where a.comentario is not null and trim(a.comentario) <> ''")
 long comComentario();
}
