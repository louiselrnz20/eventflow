
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(150) NOT NULL,
    event_date DATE,
    event_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE data_imports (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id),
    filename VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    import_status VARCHAR(30) DEFAULT 'pending'
);

CREATE TABLE ticket_sales_daily (
    id SERIAL PRIMARY KEY,
    import_id INTEGER REFERENCES data_imports(id),
    sales_date DATE NOT NULL,
    views INTEGER DEFAULT 0,
    visitors INTEGER DEFAULT 0,
    total_amount NUMERIC(12,2) DEFAULT 0,
    number_of_orders INTEGER DEFAULT 0,
    number_of_tickets INTEGER DEFAULT 0,

    UNIQUE(import_id, sales_date)
);

CREATE TABLE workshop_classes (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id),
    class_name VARCHAR(150) NOT NULL,
    start_time TIME,
    end_time TIME,
    instructor_name VARCHAR(150)
);

CREATE TABLE workshop_finance (
    id SERIAL PRIMARY KEY,
    import_id INTEGER REFERENCES data_imports(id),
    category VARCHAR(100) NOT NULL,
    revenue_amount NUMERIC(12,2) NOT NULL,
    category_type VARCHAR(50) NOT NULL
);

CREATE TABLE walkin_transactions (
    id SERIAL PRIMARY KEY,
    import_id INTEGER REFERENCES data_imports(id),
    class_name VARCHAR(150),
    ticket_type VARCHAR(100),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL,
    total_amount NUMERIC(12,2) NOT NULL,
    payment_method VARCHAR(50),
    payment_status VARCHAR(30)
);
