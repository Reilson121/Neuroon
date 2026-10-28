package com.Neuron.demo.config;

import java.sql.DriverManager;
import java.util.HashSet;
import java.util.Set;
import org.flywaydb.core.Flyway;

/** Comando explícito para migrar a base local do protótipo sem subir o servidor. */
public class MigrarBanco {
 public static void main(String[] args) throws Exception {
  String url=System.getenv().getOrDefault("DB_URL","jdbc:postgresql://localhost:5432/neuron");
  String usuario=System.getenv().getOrDefault("DB_USER","postgres");String senha=System.getenv("DB_PASSWORD");
  if(senha==null || senha.isBlank())throw new IllegalStateException("Configure o acesso ao banco local.");
  boolean baseline=false;
  try(var c=DriverManager.getConnection(url,usuario,senha)){
   var tabelas=new HashSet<String>();
   try(var r=c.getMetaData().getTables(null,"public","%",new String[]{"TABLE"})){while(r.next())tabelas.add(r.getString("TABLE_NAME"));}
   if(!tabelas.contains("flyway_schema_history") && !tabelas.isEmpty()){
    if(!Set.of("chunk_documento").containsAll(tabelas))throw new IllegalStateException("Base sem histórico contém tabelas não previstas; revisar antes de criar baseline.");
    baseline=true;
   }
  }
  Flyway.configure().dataSource(url,usuario,senha).baselineOnMigrate(baseline).baselineVersion("0").load().migrate();
  System.out.println("Migrations acadêmicas concluídas; índice do protótipo preservado.");
 }
}
