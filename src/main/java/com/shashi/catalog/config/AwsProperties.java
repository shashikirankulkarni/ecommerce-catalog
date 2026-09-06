package com.shashi.catalog.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import jakarta.validation.constraints.NotBlank;

@Validated
@ConfigurationProperties(prefix = "app.aws")
public record AwsProperties(

        @NotBlank(message = "app.aws.access-key must be set")
        String accessKey,

        @NotBlank(message = "app.aws.secret-key must be set")
        String secretKey,

        @NotBlank(message = "app.aws.region must be set")
        String region
) {

    public AwsProperties {
        ConfigGuard.requireResolved("app.aws.access-key", "AWS_ACCESS_KEY", accessKey);
        ConfigGuard.requireResolved("app.aws.secret-key", "AWS_SECRET_KEY", secretKey);
    }
}
