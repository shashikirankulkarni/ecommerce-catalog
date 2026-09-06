package com.shashi.catalog.payment;

import java.math.BigDecimal;

import org.springframework.stereotype.Service;

import com.shashi.catalog.config.PaymentProperties;

/*
 * Stub payment integration - makes no network calls.
 *
 * Credentials arrive by constructor injection. Nothing here is a
 * compile-time constant, so no credential can be inlined into this
 * class file. Compare the bytecode with the previous version: the
 * `ldc "Bearer sk_live_..."` instruction is replaced by a field read.
 */
@Service
public class PaymentService {

    private final PaymentProperties properties;

    public PaymentService(PaymentProperties properties) {
        this.properties = properties;
    }

    public String buildAuthorizationHeader() {
        return "Bearer " + properties.stripeKey();
    }

    public String describeCharge(String sku, BigDecimal amount) {
        return "POST " + properties.baseUrl() + "/charges"
                + " merchant=" + properties.merchantId()
                + " sku=" + sku
                + " amount=" + amount;
    }

    public boolean verifyWebhook(String receivedSignature) {
        return properties.webhookSecret().equals(receivedSignature);
    }
}
