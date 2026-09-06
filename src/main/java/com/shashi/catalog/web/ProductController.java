package com.shashi.catalog.web;

import java.net.URI;
import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.shashi.catalog.service.ProductService;
import com.shashi.catalog.web.dto.ProductRequest;
import com.shashi.catalog.web.dto.ProductResponse;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/v1/products")
@Tag(name = "Products", description = "Product catalog operations")
public class ProductController {

    private final ProductService service;

    public ProductController(ProductService service) {
        this.service = service;
    }

    @GetMapping
    @Operation(summary = "List products, optionally filtered by category")
    public List<ProductResponse> list(
            @RequestParam(required = false) String category,
            @RequestParam(defaultValue = "false") boolean includeInactive) {

        return category == null
                ? service.findAll(includeInactive)
                : service.findByCategory(category, includeInactive);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Fetch a single product by id")
    public ProductResponse getById(@PathVariable Long id) {
        return service.findById(id);
    }

    @GetMapping("/sku/{sku}")
    @Operation(summary = "Fetch a single product by sku")
    public ProductResponse getBySku(@PathVariable String sku) {
        return service.findBySku(sku);
    }

    @PostMapping
    @Operation(summary = "Create a product")
    public ResponseEntity<ProductResponse> create(@Valid @RequestBody ProductRequest request) {
        ProductResponse created = service.create(request);
        // 201 with a Location header pointing at the new resource.
        return ResponseEntity
                .created(URI.create("/api/v1/products/" + created.id()))
                .body(created);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Replace a product")
    public ProductResponse update(@PathVariable Long id, @Valid @RequestBody ProductRequest request) {
        return service.update(id, request);
    }

    /*
     * DELETE deactivates rather than removing the row. The response body
     * makes that explicit - a caller expecting a hard delete can see that
     * the product still exists with active=false.
     */
    @DeleteMapping("/{id}")
    @Operation(summary = "Deactivate a product (soft delete)")
    public ProductResponse deactivate(@PathVariable Long id) {
        return service.deactivate(id);
    }

    @PutMapping("/{id}/activate")
    @Operation(summary = "Reactivate a previously deactivated product")
    public ProductResponse activate(@PathVariable Long id) {
        return service.activate(id);
    }
}
