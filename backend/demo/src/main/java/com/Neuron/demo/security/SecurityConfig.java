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
 @Bean SecurityFilterChain filterChain(HttpSecurity http, SecurityContextRepository contexts,CsrfTokenRepository csrf,VisitanteCleanup visitantes,UsuarioRepository usuarios) throws Exception {
  http.csrf(c -> c.csrfTokenRepository(csrf))
   .securityContext(c -> c.securityContextRepository(contexts))
   .authorizeHttpRequests(a -> a.requestMatchers("/api/v1/auth/login","/api/v1/auth/cadastro","/api/v1/auth/visitante","/api/v1/auth/csrf").permitAll()
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
  // Revalida a conta em cada requisição para bloquear também sessões já abertas após exclusão.
  http.addFilterBefore(new org.springframework.web.filter.OncePerRequestFilter(){
   @Override protected void doFilterInternal(jakarta.servlet.http.HttpServletRequest req,jakarta.servlet.http.HttpServletResponse res,jakarta.servlet.FilterChain chain)
     throws jakarta.servlet.ServletException,java.io.IOException {
    var auth=org.springframework.security.core.context.SecurityContextHolder.getContext().getAuthentication();
    if(auth!=null&&auth.isAuthenticated()&&!(auth instanceof org.springframework.security.authentication.AnonymousAuthenticationToken)){
     var conta=usuarios.findByEmailAndAtivoTrue(auth.getName());
     if(conta.isEmpty()||(auth.getDetails() instanceof Long id&&!id.equals(conta.get().getId()))){
      org.springframework.security.core.context.SecurityContextHolder.clearContext();
      var session=req.getSession(false);if(session!=null)session.invalidate();
     }
    }
    chain.doFilter(req,res);
   }
  },org.springframework.security.web.access.intercept.AuthorizationFilter.class);
  return http.build();
 }
}
