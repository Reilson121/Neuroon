package com.Neuron.demo.monitorvirtual;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.*;

public interface MensagemMonitorRepository extends JpaRepository<MensagemMonitor,Long> {
 List<MensagemMonitor> findByConversaIdOrderByIdAsc(UUID conversaId);
 List<MensagemMonitor> findByConversaIdOrderByIdDesc(UUID conversaId,org.springframework.data.domain.Pageable pagina);
 long countByConversaId(UUID conversaId);
}
