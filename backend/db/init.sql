CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE projects (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE design_specs (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE files (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    design_spec_id UUID REFERENCES design_specs(id) ON DELETE CASCADE,

    file_type VARCHAR(50) NOT NULL,
        -- 'design_doc'
        -- 'raw_image'
        -- 'annotated_image'
        -- 'report_pdf'

    bucket_name VARCHAR(255) NOT NULL,
    object_key TEXT NOT NULL,
    original_filename VARCHAR(255),
    content_type VARCHAR(100),
    file_size BIGINT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE detection_runs (
    id UUID PRIMARY KEY,
    design_spec_id UUID NOT NULL REFERENCES design_specs(id) ON DELETE CASCADE,
    raw_image_file_id UUID NOT NULL REFERENCES files(id),

    status VARCHAR(50) NOT NULL,
        -- NOT_STARTED
        -- IN_PROGRESS
        -- COMPLETE_ERRORS
        -- COMPLETE_SUCCESS

    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE detection_results (
    id UUID PRIMARY KEY,
    detection_run_id UUID NOT NULL REFERENCES detection_runs(id) ON DELETE CASCADE,

    label VARCHAR(255) NOT NULL,
    confidence_score DECIMAL(5,4),

    x_min INTEGER NOT NULL,
    y_min INTEGER NOT NULL,
    x_max INTEGER NOT NULL,
    y_max INTEGER NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reports (
    id UUID PRIMARY KEY,
    detection_run_id UUID NOT NULL REFERENCES detection_runs(id) ON DELETE CASCADE,
    report_file_id UUID NOT NULL REFERENCES files(id),

    generated_by UUID REFERENCES users(id),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert test user
INSERT INTO users (email, password_hash, role)
VALUES ('test@example.com', 'fake_hash_123', 'admin');