package com.shashi.catalog;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

/*
 * @ConfigurationPropertiesScan registers every @ConfigurationProperties
 * type in this package tree as a bean. Without it PaymentProperties is
 * just an unregistered record and injecting it fails.
 */
@SpringBootApplication
@ConfigurationPropertiesScan
public class CatalogApplication {

	public static void main(String[] args) {
		SpringApplication.run(CatalogApplication.class, args);
	}

}
