package com.shashi.catalog.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import jakarta.validation.constraints.NotBlank;

/*
 * Payment configuration, bound from app.payment.* at startup.
 *
 * @NotBlank alone is not enough. When Spring cannot resolve a placeholder
 * such as ${STRIPE_KEY} it does not fail - it leaves the literal text
 * "${STRIPE_KEY}" as the value. That is a perfectly non-blank string, so
 * validation passes and the application starts happily holding nonsense,
 * failing much later at the first call that uses it.
 *
 * The compact constructor closes that gap: it runs during binding, so an
 * unresolved placeholder aborts startup naming the property that is
 * missing.
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

    public PaymentProperties {
        ConfigGuard.requireResolved("app.payment.stripe-key", "STRIPE_KEY", stripeKey);
        ConfigGuard.requireResolved("app.payment.webhook-secret", "STRIPE_WEBHOOK_SECRET", webhookSecret);
        ConfigGuard.requireResolved("app.payment.merchant-id", "STRIPE_MERCHANT_ID", merchantId);
        ConfigGuard.requireResolved("app.payment.base-url", "STRIPE_BASE_URL", baseUrl);
    }
}
