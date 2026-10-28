package com.Neuron.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

// Embeddings e pgvector são operados pelo serviço Python; o Spring concentra
// domínio, permissões e integração, sem inicializar um segundo pipeline de IA.
@SpringBootApplication(excludeName = "org.springframework.ai.vectorstore.pgvector.autoconfigure.PgVectorStoreAutoConfiguration")
public class DemoApplication {

	public static void main(String[] args) {
		SpringApplication.run(DemoApplication.class, args);
	}

}
