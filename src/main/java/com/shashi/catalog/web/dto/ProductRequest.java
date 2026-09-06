package com.shashi.catalog.web.dto;

import java.math.BigDecimal;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;

/*
 * Input is a separate type from the entity on purpose. Binding requests
 * straight onto Product would let a caller set id, active, createdAt or
 * any column added later simply by naming it in the JSON.
 */
public record ProductRequest(

        @NotBlank(message = "sku is required")
        @Size(max = 64, message = "sku must be at most 64 characters")
        String sku,

        @NotBlank(message = "name is required")
        @Size(max = 255, message = "name must be at most 255 characters")
        String name,

        @Size(max = 5000, message = "description must be at most 5000 characters")
        String description,

        @NotNull(message = "price is required")
        @DecimalMin(value = "0.00", message = "price must not be negative")
        BigDecimal price,

        @NotBlank(message = "category is required")
        @Size(max = 100, message = "category must be at most 100 characters")
        String category,

        @PositiveOrZero(message = "stockQuantity must not be negative")
        int stockQuantity
) {
}
