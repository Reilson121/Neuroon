package com.Neuron.demo.material;

import com.Neuron.demo.academico.CatalogoService;
import com.Neuron.demo.common.ErroNegocio;
import com.Neuron.demo.usuario.UsuarioAtual;
import java.io.IOException;
import java.nio.file.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ArquivoMaterialService {
 private final MaterialRepository materiais;
 private final CatalogoService catalogo;
 private final UsuarioAtual usuarios;
 private final Path raiz;
 public ArquivoMaterialService(MaterialRepository materiais,CatalogoService catalogo,UsuarioAtual usuarios,
   @Value("${neuron.materials.root:../../neuron-ai/materiais_academicos}") String raiz){
  this.materiais=materiais;this.catalogo=catalogo;this.usuarios=usuarios;this.raiz=Path.of(raiz).toAbsolutePath().normalize();
 }
 public static boolean possuiArquivo(String referencia){
  if(referencia==null || !referencia.startsWith("local:materiais_academicos/"))return false;
  String r=referencia.toLowerCase(java.util.Locale.ROOT);
  return r.endsWith(".pdf") || r.endsWith(".docx") || r.endsWith(".pptx");
 }
 @Transactional(readOnly=true)
 public ResponseEntity<FileSystemResource> abrir(Long id,Authentication auth){
  usuarios.exigir(auth);
  Material m=materiais.findById(id).filter(Material::isAtivo).orElseThrow(ArquivoMaterialService::indisponivel);
  catalogo.exigirDisciplina(m.getDisciplina().getId());
  if(!m.assuntoPertenceADisciplina() || m.getAssunto()!=null && !m.getAssunto().isAtivo() || !possuiArquivo(m.getReferenciaExterna()))throw indisponivel();
  try{
   Path base=raiz.toRealPath();
   Path arquivo=base.resolve(m.getReferenciaExterna().substring("local:materiais_academicos/".length())).normalize();
   if(!arquivo.startsWith(base))throw indisponivel();
   arquivo=arquivo.toRealPath();
   if(!arquivo.startsWith(base) || !Files.isRegularFile(arquivo))throw indisponivel();
   boolean pdf=arquivo.getFileName().toString().toLowerCase(java.util.Locale.ROOT).endsWith(".pdf");
   ContentDisposition.Builder disposition=pdf?ContentDisposition.inline():ContentDisposition.attachment();
   return ResponseEntity.ok().contentType(pdf?MediaType.APPLICATION_PDF:MediaType.APPLICATION_OCTET_STREAM)
    .cacheControl(CacheControl.noStore()).header(HttpHeaders.CONTENT_DISPOSITION,disposition.filename(arquivo.getFileName().toString(),java.nio.charset.StandardCharsets.UTF_8).build().toString())
    .body(new FileSystemResource(arquivo));
  }catch(IOException e){throw indisponivel();}
 }
 private static ErroNegocio indisponivel(){return new ErroNegocio(404,"ARQUIVO_INDISPONIVEL","O arquivo não está disponível.");}
}
