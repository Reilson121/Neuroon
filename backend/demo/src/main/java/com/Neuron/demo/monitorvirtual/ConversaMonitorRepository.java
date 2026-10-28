package com.Neuron.demo.monitorvirtual;

import org.springframework.data.jpa.repository.*;
import org.springframework.data.domain.Pageable;
import jakarta.persistence.LockModeType;
import java.util.*;

public interface ConversaMonitorRepository extends JpaRepository<ConversaMonitor,UUID> {
 @Query("select c from ConversaMonitor c where c.usuario.id=:usuarioId and c.disciplina.id=:disciplinaId and ((:assuntoId is null and c.assunto is null) or c.assunto.id=:assuntoId) order by c.atualizadoEm desc, c.id desc")
 List<ConversaMonitor> listar(Long usuarioId,Long disciplinaId,Long assuntoId,Pageable page);
 Optional<ConversaMonitor> findByIdAndUsuarioId(UUID id,Long usuarioId);
 @Lock(LockModeType.PESSIMISTIC_WRITE)
 @Query("select c from ConversaMonitor c where c.id=:id and c.usuario.id=:usuarioId")
 Optional<ConversaMonitor> bloquear(UUID id,Long usuarioId);
}
