
-- SJSC Finance Report Tables
-- These tables store financial data separately
-- to prevent double-counting.

CREATE TABLE workshop_finance_summary (
    id SERIAL PRIMARY KEY,
    import_id INTEGER NOT NULL REFERENCES data_imports(id),
    early_bird_revenue NUMERIC(12,2),
    regular_revenue NUMERIC(12,2),
    walk_in_revenue NUMERIC(12,2),
    reported_total NUMERIC(12,2) NOT NULL,
    UNIQUE(import_id)
);

CREATE TABLE workshop_instructor_allocations (
    id SERIAL PRIMARY KEY,
    import_id INTEGER NOT NULL REFERENCES data_imports(id),
    instructor_name VARCHAR(150) NOT NULL,
    early_bird_revenue NUMERIC(12,2),
    regular_revenue NUMERIC(12,2),
    walk_in_revenue NUMERIC(12,2),
    reported_total NUMERIC(12,2)
);

CREATE TABLE workshop_package_prices (
    id SERIAL PRIMARY KEY,
    import_id INTEGER NOT NULL REFERENCES data_imports(id),
    package_name VARCHAR(150) NOT NULL,
    early_bird_price NUMERIC(12,2),
    regular_price NUMERIC(12,2),
    walk_in_price NUMERIC(12,2),
    UNIQUE(import_id, package_name)
);

CREATE TABLE workshop_merchandise (
    id SERIAL PRIMARY KEY,
    import_id INTEGER NOT NULL REFERENCES data_imports(id),
    item_or_instructor VARCHAR(150) NOT NULL,
    revenue_amount NUMERIC(12,2)
);

CREATE TABLE workshop_discounts (
    id SERIAL PRIMARY KEY,
    import_id INTEGER NOT NULL REFERENCES data_imports(id),
    package_name VARCHAR(150) NOT NULL,
    recorded_amount NUMERIC(12,2)
);

CREATE TABLE workshop_sales_breakdown (
    id SERIAL PRIMARY KEY,
    import_id INTEGER NOT NULL REFERENCES data_imports(id),
    description VARCHAR(150) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL,
    total_amount NUMERIC(12,2) NOT NULL
);
