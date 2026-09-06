package com.shashi.catalog.web;

import java.net.URI;
import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import com.shashi.catalog.service.DuplicateSkuException;
import com.shashi.catalog.service.ProductNotFoundException;

/*
 * Errors are returned as RFC 7807 problem details rather than ad-hoc JSON,
 * so every failure has the same shape: type, title, status, detail.
 * Spring supports ProblemDetail natively, so no custom error model is needed.
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ProductNotFoundException.class)
    ProblemDetail handleNotFound(ProductNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setTitle("Product not found");
        problem.setType(URI.create("https://catalog.shashi.com/errors/product-not-found"));
        return problem;
    }

    @ExceptionHandler(DuplicateSkuException.class)
    ProblemDetail handleDuplicateSku(DuplicateSkuException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, ex.getMessage());
        problem.setTitle("Duplicate sku");
        problem.setType(URI.create("https://catalog.shashi.com/errors/duplicate-sku"));
        return problem;
    }

    /*
     * Bean validation failures. The per-field errors are attached as an
     * extension property so a client can highlight the offending inputs
     * instead of parsing a prose message.
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new LinkedHashMap<>();
        for (FieldError fieldError : ex.getBindingResult().getFieldErrors()) {
            errors.put(fieldError.getField(), fieldError.getDefaultMessage());
        }

        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.BAD_REQUEST, "One or more fields are invalid");
        problem.setTitle("Validation failed");
        problem.setType(URI.create("https://catalog.shashi.com/errors/validation-failed"));
        problem.setProperty("errors", errors);
        return problem;
    }
}
