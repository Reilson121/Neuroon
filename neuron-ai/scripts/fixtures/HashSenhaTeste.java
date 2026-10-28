import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import org.springframework.security.crypto.bcrypt.BCrypt;

/** Usado somente pelo teste HTTP; a senha aleatória chega por stdin. */
public class HashSenhaTeste {
 public static void main(String[] args) throws Exception {
  var entrada=new BufferedReader(new InputStreamReader(System.in,StandardCharsets.UTF_8));
  String senha=entrada.readLine();
  if(senha==null || senha.length()<20)throw new IllegalArgumentException("Senha de teste inválida.");
  System.out.println(BCrypt.hashpw(senha,BCrypt.gensalt(12)));
 }
}
