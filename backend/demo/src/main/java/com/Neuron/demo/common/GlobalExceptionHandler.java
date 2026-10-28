package com.Neuron.demo.common;
import java.time.Instant;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.dao.DataIntegrityViolationException;
@RestControllerAdvice
public class GlobalExceptionHandler {
 public record ErroResponse(int status,String codigo,String mensagem,Instant timestamp){}
 @ExceptionHandler(org.springframework.security.core.AuthenticationException.class)
 ResponseEntity<ErroResponse> autenticacao(Exception e){return resposta(401,"CREDENCIAIS_INVALIDAS","Email ou senha inválidos.");}
 @ExceptionHandler(org.springframework.security.access.AccessDeniedException.class)
 ResponseEntity<ErroResponse> permissao(Exception e){return resposta(403,"ACESSO_NEGADO","Operação não autorizada.");}
 @ExceptionHandler(ErroNegocio.class)
 ResponseEntity<ErroResponse> negocio(ErroNegocio e){return resposta(e.getStatus(),e.getCodigo(),e.getMessage());}
 @ExceptionHandler({MethodArgumentNotValidException.class, org.springframework.http.converter.HttpMessageNotReadableException.class})
 ResponseEntity<ErroResponse> entrada(Exception e){return resposta(400,"DADOS_INVALIDOS","Confira os campos informados.");}
 @ExceptionHandler(DataIntegrityViolationException.class)
 ResponseEntity<ErroResponse> conflito(Exception e){return resposta(409,"CONFLITO_DADOS","A operação viola uma regra de consistência ou unicidade.");}
 @ExceptionHandler(Exception.class)
 ResponseEntity<ErroResponse> interno(Exception e){return resposta(500,"ERRO_INTERNO","Não foi possível concluir a operação.");}
 private ResponseEntity<ErroResponse> resposta(int status,String codigo,String mensagem){return ResponseEntity.status(status).body(new ErroResponse(status,codigo,mensagem,Instant.now()));}
}
