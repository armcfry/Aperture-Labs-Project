CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE fod_detections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    bucket_name TEXT NOT NULL,
    object_key TEXT NOT NULL,

    confidence_score NUMERIC,
    detection_result JSONB,

    status TEXT DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert test user
INSERT INTO users (email, password_hash, role)
VALUES ('test@example.com', 'fake_hash_123', 'admin');