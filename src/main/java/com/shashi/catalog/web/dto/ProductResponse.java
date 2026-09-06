package com.shashi.catalog.web.dto;

import java.math.BigDecimal;
import java.time.Instant;

import com.shashi.catalog.domain.Product;

public record ProductResponse(
        Long id,
        String sku,
        String name,
        String description,
        BigDecimal price,
        String category,
        int stockQuantity,
        boolean active,
        Instant createdAt,
        Instant updatedAt
) {

    public static ProductResponse from(Product product) {
        return new ProductResponse(
                product.getId(),
                product.getSku(),
                product.getName(),
                product.getDescription(),
                product.getPrice(),
                product.getCategory(),
                product.getStockQuantity(),
                product.isActive(),
                product.getCreatedAt(),
                product.getUpdatedAt());
    }
}
