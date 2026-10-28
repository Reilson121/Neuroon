package com.Neuron.demo.usuario;
import org.springframework.data.jpa.repository.JpaRepository;
public interface UsuarioRepository extends JpaRepository<Usuario,Long> { java.util.Optional<Usuario> findByEmailAndAtivoTrue(String email); boolean existsByEmail(String email); }
