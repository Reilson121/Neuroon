package com.Neuron.demo.usuario;
import org.springframework.data.jpa.repository.JpaRepository;
public interface UsuarioRepository extends JpaRepository<Usuario,Long> {
 java.util.Optional<Usuario> findByEmailAndAtivoTrue(String email);
 boolean existsByEmail(String email);
 boolean existsByEmailAndIdNot(String email,Long id);
 org.springframework.data.domain.Page<Usuario> findByAtivoTrueAndPerfilNot(Perfil perfil,org.springframework.data.domain.Pageable pageable);
}
