CREATE TABLE IF NOT EXISTS service_areas (
    id         SERIAL PRIMARY KEY,
    postcode   VARCHAR(4)   NOT NULL UNIQUE,
    suburb     VARCHAR(100) NOT NULL,
    is_active  BOOLEAN      NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Seed: Sydney service areas
INSERT INTO service_areas (postcode, suburb) VALUES
    ('2000', 'Sydney CBD'),
    ('2010', 'Surry Hills'),
    ('2011', 'Darlinghurst'),
    ('2009', 'Pyrmont'),
    ('2017', 'Zetland'),
    ('2026', 'Bondi'),
    ('2034', 'Coogee'),
    ('2028', 'Double Bay'),
    ('2031', 'Randwick'),
    ('2042', 'Newtown'),
    ('2037', 'Glebe'),
    ('2041', 'Balmain'),
    ('2204', 'Marrickville'),
    ('2067', 'Chatswood'),
    ('2088', 'Mosman'),
    ('2066', 'Lane Cove'),
    ('2077', 'Hornsby')
ON CONFLICT (postcode) DO NOTHING;
