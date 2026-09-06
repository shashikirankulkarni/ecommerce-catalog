CREATE TABLE product (
    id             BIGSERIAL     PRIMARY KEY,
    sku            VARCHAR(64)   NOT NULL UNIQUE,
    name           VARCHAR(255)  NOT NULL,
    description    TEXT,
    price          NUMERIC(19,2) NOT NULL,
    category       VARCHAR(100)  NOT NULL,
    stock_quantity INTEGER       NOT NULL DEFAULT 0,
    active         BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ   NOT NULL,
    updated_at     TIMESTAMPTZ   NOT NULL
);

CREATE INDEX idx_product_category ON product (category);
CREATE INDEX idx_product_active   ON product (active);
