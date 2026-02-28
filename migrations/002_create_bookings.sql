CREATE TABLE IF NOT EXISTS bookings (
    id            UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_name VARCHAR(255)  NOT NULL,
    email         VARCHAR(255)  NOT NULL,
    phone         VARCHAR(20)   NOT NULL,
    address       TEXT          NOT NULL,
    postcode      VARCHAR(4)    NOT NULL,
    service_date  DATE          NOT NULL,
    service_type  VARCHAR(20)   NOT NULL,
    bedrooms      SMALLINT      NOT NULL CHECK (bedrooms BETWEEN 1 AND 5),
    bathrooms     SMALLINT      NOT NULL CHECK (bathrooms BETWEEN 1 AND 4),
    total_price   NUMERIC(10,2) NOT NULL,
    status        VARCHAR(30)   NOT NULL DEFAULT 'pending_payment',
    created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
