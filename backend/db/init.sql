BEGIN;

-- users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name VARCHAR NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    theme VARCHAR NOT NULL,
    CONSTRAINT users_theme_check
        CHECK (theme IN ('light', 'dark', 'system'))
);

-- projects (depends on users via created_by_user_id)
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    bucket_name VARCHAR,
    object_key UUID, -- design spec key
    created_by_user_id UUID NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    archived_at TIMESTAMPTZ,
    detector_version VARCHAR,

    CONSTRAINT fk_projects_created_by_user
        FOREIGN KEY (created_by_user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

-- project_members (join table depends on projects + users)
CREATE TABLE project_members (
    project_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role VARCHAR NOT NULL,
    joined_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT pk_project_members PRIMARY KEY (project_id, user_id),

    CONSTRAINT fk_project_members_project
        FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_project_members_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT project_members_role_check
        CHECK (role IN ('owner', 'editor', 'viewer'))
);

-- submissions (depends on projects + users)
CREATE TABLE submissions (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL,
    submitted_by_user_id UUID NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL,
    status VARCHAR NOT NULL,
    pass_fail VARCHAR NOT NULL,
    anomaly_count INT NOT NULL DEFAULT 0,
    error_message TEXT,

    CONSTRAINT fk_submissions_project
        FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_submissions_submitted_by_user
        FOREIGN KEY (submitted_by_user_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT submissions_status_check
        CHECK (status IN ('queued', 'running', 'complete', 'complete_with_errors', 'failed')),

    CONSTRAINT submissions_pass_fail_check
        CHECK (pass_fail IN ('pass', 'fail', 'unknown')),

    CONSTRAINT submissions_anomaly_count_check
        CHECK (anomaly_count >= 0)
);

-- anomalies (depends on submissions)
CREATE TABLE anomolies (
    id UUID PRIMARY KEY,
    submission_id UUID NOT NULL,
    label VARCHAR NOT NULL,
    description TEXT,
    severity VARCHAR,
    confidence DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT fk_anomolies_submission
        FOREIGN KEY (submission_id)
        REFERENCES submissions(id)
        ON DELETE CASCADE,

    CONSTRAINT anomolies_severity_check
        CHECK (severity IS NULL OR severity IN ('low', 'med', 'high')),

    CONSTRAINT anomolies_confidence_check
        CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1))
);




--==============================================
-- insert sample data for all tables

-- users
INSERT INTO users (
    id, email, password_hash, display_name, created_at, updated_at, theme
) VALUES
(
    '11111111-1111-1111-1111-111111111111',
    'alice@example.com',
    '$2b$12$aliceFakeHash',
    'Alice Kim',
    NOW(),
    NOW(),
    'dark'
),
(
    '22222222-2222-2222-2222-222222222222',
    'bob@example.com',
    '$2b$12$bobFakeHash',
    'Bob Lee',
    NOW(),
    NOW(),
    'light'
),
(
    '33333333-3333-3333-3333-333333333333',
    'carol@example.com',
    '$2b$12$carolFakeHash',
    'Carol Park',
    NOW(),
    NOW(),
    'system'
);


-- projects
INSERT INTO projects (
    id, name, description, bucket_name, object_key, created_by_user_id,
    created_at, updated_at, archived_at, detector_version
) VALUES
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
    'Valve Housing Inspection',
    'Project for detecting surface defects on valve housing images.',
    'proj-valve-housing-inspection',
    'aaaaaaaa-0000-0000-0000-000000000001',
    '11111111-1111-1111-1111-111111111111',
    NOW(),
    NOW(),
    NULL,
    'detector-v1.2.0'
),
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2',
    'PCB Solder Check',
    'Detect solder bridge and missing solder anomalies on PCB images.',
    'proj-pcb-solder-check',
    'aaaaaaaa-0000-0000-0000-000000000002',
    '22222222-2222-2222-2222-222222222222',
    NOW(),
    NOW(),
    NULL,
    'detector-v2.0.1'
);


-- project_members
INSERT INTO project_members (
    project_id, user_id, role, joined_at
) VALUES
-- Project 1 members
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
    '11111111-1111-1111-1111-111111111111',
    'owner',
    NOW()
),
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
    '22222222-2222-2222-2222-222222222222',
    'editor',
    NOW()
),
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
    '33333333-3333-3333-3333-333333333333',
    'viewer',
    NOW()
),

-- Project 2 members
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2',
    '22222222-2222-2222-2222-222222222222',
    'owner',
    NOW()
),
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2',
    '11111111-1111-1111-1111-111111111111',
    'editor',
    NOW()
);


-- submissions
INSERT INTO submissions (
    id, project_id, submitted_by_user_id, submitted_at, status,
    pass_fail, anomaly_count, error_message
) VALUES
(
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
    '11111111-1111-1111-1111-111111111111',
    NOW() - INTERVAL '2 days',
    'complete',
    'fail',
    2,
    NULL
),
(
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
    '22222222-2222-2222-2222-222222222222',
    NOW() - INTERVAL '1 day',
    'complete',
    'pass',
    0,
    NULL
),
(
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2',
    '22222222-2222-2222-2222-222222222222',
    NOW() - INTERVAL '12 hours',
    'complete_with_errors',
    'fail',
    1,
    'Processed image, but one optional post-processing step failed.'
),
(
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2',
    '11111111-1111-1111-1111-111111111111',
    NOW() - INTERVAL '2 hours',
    'queued',
    'unknown',
    0,
    NULL
);


-- anomalies
INSERT INTO anomolies (
    id, submission_id, label, description, severity, confidence, created_at
) VALUES
(
    'cccccccc-cccc-cccc-cccc-ccccccccc001',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001',
    'scratch',
    'Visible linear scratch on outer rim.',
    'med',
    0.93,
    NOW() - INTERVAL '2 days'
),
(
    'cccccccc-cccc-cccc-cccc-ccccccccc002',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001',
    'dent',
    'Small dent near bolt hole region.',
    'high',
    0.88,
    NOW() - INTERVAL '2 days'
),
(
    'cccccccc-cccc-cccc-cccc-ccccccccc003',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003',
    'solder_bridge',
    'Potential solder bridge between adjacent pads.',
    'high',
    0.97,
    NOW() - INTERVAL '12 hours'
);

COMMIT;