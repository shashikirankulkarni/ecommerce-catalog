package com.shashi.catalog.service;

import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.shashi.catalog.domain.Product;
import com.shashi.catalog.domain.ProductRepository;
import com.shashi.catalog.web.dto.ProductRequest;
import com.shashi.catalog.web.dto.ProductResponse;

@Service
@Transactional(readOnly = true)
public class ProductService {

    private final ProductRepository repository;

    /*
     * Constructor injection rather than @Autowired on fields: the dependency
     * is visible in the signature, the field can be final, and the class can
     * be unit tested without a Spring context.
     */
    public ProductService(ProductRepository repository) {
        this.repository = repository;
    }

    public List<ProductResponse> findAll(boolean includeInactive) {
        List<Product> products = includeInactive
                ? repository.findAll()
                : repository.findByActiveTrue();
        return products.stream().map(ProductResponse::from).toList();
    }

    public List<ProductResponse> findByCategory(String category, boolean includeInactive) {
        List<Product> products = includeInactive
                ? repository.findByCategory(category)
                : repository.findByCategoryAndActiveTrue(category);
        return products.stream().map(ProductResponse::from).toList();
    }

    public ProductResponse findById(Long id) {
        return ProductResponse.from(getOrThrow(id));
    }

    public ProductResponse findBySku(String sku) {
        return repository.findBySku(sku)
                .map(ProductResponse::from)
                .orElseThrow(() -> new ProductNotFoundException("No product with sku '" + sku + "'"));
    }

    @Transactional
    public ProductResponse create(ProductRequest request) {
        if (repository.existsBySku(request.sku())) {
            throw new DuplicateSkuException(request.sku());
        }
        Product product = new Product();
        apply(request, product);
        return ProductResponse.from(repository.save(product));
    }

    @Transactional
    public ProductResponse update(Long id, ProductRequest request) {
        Product product = getOrThrow(id);

        // The sku is allowed to change, but only to one nobody else holds.
        if (!product.getSku().equals(request.sku()) && repository.existsBySku(request.sku())) {
            throw new DuplicateSkuException(request.sku());
        }
        apply(request, product);
        return ProductResponse.from(repository.save(product));
    }

    /*
     * Soft delete. An order line referring to a hard-deleted product would
     * leave the order history broken, so products are deactivated instead
     * and simply stop appearing in customer-facing queries.
     */
    @Transactional
    public ProductResponse deactivate(Long id) {
        Product product = getOrThrow(id);
        product.setActive(false);
        return ProductResponse.from(repository.save(product));
    }

    @Transactional
    public ProductResponse activate(Long id) {
        Product product = getOrThrow(id);
        product.setActive(true);
        return ProductResponse.from(repository.save(product));
    }

    private Product getOrThrow(Long id) {
        return repository.findById(id)
                .orElseThrow(() -> new ProductNotFoundException("No product with id " + id));
    }

    private void apply(ProductRequest request, Product product) {
        product.setSku(request.sku());
        product.setName(request.name());
        product.setDescription(request.description());
        product.setPrice(request.price());
        product.setCategory(request.category());
        product.setStockQuantity(request.stockQuantity());
    }
}
