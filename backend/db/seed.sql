BEGIN;
--==============================================
-- insert sample data for all tables

-- users
INSERT INTO users (
    id, email, password_hash, created_at, updated_at
) VALUES
(
    '11111111-1111-1111-1111-111111111111',
    'alice@example.com',
    '$2b$12$aliceFakeHash',
    NOW(),
    NOW()
),
(
    '22222222-2222-2222-2222-222222222222',
    'bob@example.com',
    '$2b$12$bobFakeHash',
    NOW(),
    NOW()
),
(
    '33333333-3333-3333-3333-333333333333',
    'carol@example.com',
    '$2b$12$carolFakeHash',
    NOW(),
    NOW()
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
    id, project_id, submitted_by_user_id, submitted_at, image_id, status,
    pass_fail, anomaly_count, error_message
) VALUES
(
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
    '11111111-1111-1111-1111-111111111111',
    NOW() - INTERVAL '2 days',
    'dddddddd-dddd-dddd-dddd-ddddddddd001',
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
    'dddddddd-dddd-dddd-dddd-ddddddddd002',
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
    'dddddddd-dddd-dddd-dddd-ddddddddd003',
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
    'dddddddd-dddd-dddd-dddd-ddddddddd004',
    'queued',
    'unknown',
    NULL,
    NULL
);

-- anomolies
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