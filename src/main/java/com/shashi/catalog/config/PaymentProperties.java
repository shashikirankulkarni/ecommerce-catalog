package com.shashi.catalog.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import jakarta.validation.constraints.NotBlank;

/*
 * Payment configuration, bound from app.payment.* at startup.
 *
 * This replaces the static final String constants that used to live in
 * PaymentConfig. Three things change as a result:
 *
 *   1. The values are no longer compile-time constants, so the compiler
 *      cannot inline them into the bytecode of referencing classes.
 *   2. They come from the environment, so the same artifact runs in
 *      local, dev, qa and prod with different credentials.
 *   3. @Validated + @NotBlank makes a missing value fail at startup with
 *      the property name in the message, instead of surfacing later as
 *      some unrelated error.
 */
@Validated
@ConfigurationProperties(prefix = "app.payment")
public record PaymentProperties(

        @NotBlank(message = "app.payment.stripe-key must be set")
        String stripeKey,

        @NotBlank(message = "app.payment.webhook-secret must be set")
        String webhookSecret,

        @NotBlank(message = "app.payment.merchant-id must be set")
        String merchantId,

        @NotBlank(message = "app.payment.base-url must be set")
        String baseUrl
) {
}
