package com.shashi.catalog;

import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.context.annotation.Bean;
import org.testcontainers.postgresql.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;

/*
 * Pinned to postgres:17, the same version docker-compose runs. With
 * 'latest' the tests would silently drift onto whatever Postgres is
 * newest that day, while production stayed on 17 - a green build today
 * and a mystery failure tomorrow, with no code change in between.
 */
@TestConfiguration(proxyBeanMethods = false)
class TestcontainersConfiguration {

	@Bean
	@ServiceConnection
	PostgreSQLContainer postgresContainer() {
		return new PostgreSQLContainer(DockerImageName.parse("postgres:17"));
	}

}
