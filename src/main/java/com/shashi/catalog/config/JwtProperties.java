package com.shashi.catalog.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;

@Validated
@ConfigurationProperties(prefix = "app.jwt")
public record JwtProperties(

        @NotBlank(message = "app.jwt.secret must be set")
        String secret,

        @Positive(message = "app.jwt.expiry-minutes must be positive")
        int expiryMinutes
) {

    public JwtProperties {
        ConfigGuard.requireResolved("app.jwt.secret", "JWT_SECRET", secret);
    }
}
