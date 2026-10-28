package com.Neuron.demo.security;

import com.Neuron.demo.usuario.UsuarioRepository;
import com.Neuron.demo.usuario.VisitanteCleanup;
import org.springframework.context.annotation.*;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.userdetails.*;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.context.*;
import org.springframework.security.web.authentication.session.*;
import org.springframework.security.web.csrf.*;
import java.util.List;

@Configuration
public class SecurityConfig {
 @Bean PasswordEncoder passwordEncoder(){return new BCryptPasswordEncoder(12);}
 @Bean UserDetailsService userDetailsService(UsuarioRepository repo){
  return email -> repo.findByEmailAndAtivoTrue(email.toLowerCase(java.util.Locale.ROOT))
   .map(u -> User.withUsername(u.getEmail()).password(u.getSenhaHash()).roles(u.getPerfil().name()).build())
   .orElseThrow(() -> new UsernameNotFoundException("Usuário não encontrado."));
 }
 @Bean AuthenticationManager authenticationManager(AuthenticationConfiguration c) throws Exception {return c.getAuthenticationManager();}
 @Bean SecurityContextRepository contextRepository(){return new HttpSessionSecurityContextRepository();}
 @Bean CsrfTokenRepository csrfRepository(){return new HttpSessionCsrfTokenRepository();}
 @Bean SessionAuthenticationStrategy sessionStrategy(CsrfTokenRepository csrf){
  return new CompositeSessionAuthenticationStrategy(List.of(new ChangeSessionIdAuthenticationStrategy(),new CsrfAuthenticationStrategy(csrf)));
 }
 @Bean SecurityFilterChain filterChain(HttpSecurity http, SecurityContextRepository contexts,CsrfTokenRepository csrf,VisitanteCleanup visitantes) throws Exception {
  http.csrf(c -> c.csrfTokenRepository(csrf))
   .securityContext(c -> c.securityContextRepository(contexts))
   .authorizeHttpRequests(a -> a.requestMatchers("/api/v1/auth/login","/api/v1/auth/visitante","/api/v1/auth/csrf").permitAll()
    .requestMatchers("/api/v1/admin/**").hasRole("ADMINISTRADOR")
    .requestMatchers("/api/v1/pratica/**").hasAnyRole("ESTUDANTE","ADMINISTRADOR")
    .requestMatchers("/api/v1/avaliacao-plataforma/**").hasRole("ESTUDANTE")
    .anyRequest().authenticated())
   .exceptionHandling(e -> e.authenticationEntryPoint((req,res,error) -> {
     res.setStatus(401);res.setContentType("application/json");res.setCharacterEncoding("UTF-8");res.getWriter().write("{\"status\":401,\"codigo\":\"NAO_AUTENTICADO\",\"mensagem\":\"Entre na sua conta.\"}");
    }).accessDeniedHandler((req,res,error) -> {
     res.setStatus(403);res.setContentType("application/json");res.setCharacterEncoding("UTF-8");res.getWriter().write("{\"status\":403,\"codigo\":\"ACESSO_NEGADO\",\"mensagem\":\"Operação não autorizada.\"}");
    }))
   .logout(l -> l.logoutUrl("/api/v1/auth/logout").invalidateHttpSession(true).deleteCookies("JSESSIONID")
    .logoutSuccessHandler((req,res,auth) -> {
      if(auth!=null && auth.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_VISITANTE")))
       visitantes.remover(auth.getName());
      res.setStatus(204);
    }));
  return http.build();
 }
}
