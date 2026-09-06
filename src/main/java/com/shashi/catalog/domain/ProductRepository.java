package com.shashi.catalog.domain;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ProductRepository extends JpaRepository<Product, Long> {

    Optional<Product> findBySku(String sku);

    boolean existsBySku(String sku);

    List<Product> findByCategory(String category);

    /*
     * Products are deactivated rather than deleted, so anything customer
     * facing has to filter on active explicitly.
     */
    List<Product> findByActiveTrue();

    List<Product> findByCategoryAndActiveTrue(String category);
}
