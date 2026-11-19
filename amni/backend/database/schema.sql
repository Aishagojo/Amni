BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 0001_accounts_categories_cases

CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    display_name VARCHAR(120) NOT NULL,
    email VARCHAR(320) NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(16) DEFAULT 'requester' NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_users PRIMARY KEY (id),
    CONSTRAINT ck_users_role_valid CHECK (role IN ('requester', 'engineer', 'admin')),
    CONSTRAINT ck_users_name_not_blank CHECK (char_length(btrim(display_name)) > 0),
    CONSTRAINT ck_users_email_not_blank CHECK (char_length(btrim(email)) > 0),
    CONSTRAINT ck_users_password_hash_not_blank CHECK (char_length(btrim(password_hash)) > 0)
);

CREATE UNIQUE INDEX uq_users_email_ci ON users (lower(email));

CREATE TABLE issue_categories (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    slug VARCHAR(64) NOT NULL,
    name VARCHAR(80) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_issue_categories PRIMARY KEY (id),
    CONSTRAINT uq_issue_categories_slug UNIQUE (slug),
    CONSTRAINT ck_issue_categories_slug_format CHECK (slug ~ '^[a-z][a-z0-9-]{0,63}$'),
    CONSTRAINT ck_issue_categories_name_not_blank CHECK (char_length(btrim(name)) > 0)
);

CREATE TABLE sessions (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    user_id UUID NOT NULL,
    token_hash VARCHAR(64) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_sessions PRIMARY KEY (id),
    CONSTRAINT fk_sessions_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT uq_sessions_token_hash UNIQUE (token_hash),
    CONSTRAINT ck_sessions_token_hash_format CHECK (token_hash ~ '^[0-9a-f]{64}$'),
    CONSTRAINT ck_sessions_expiry_after_creation CHECK (expires_at > created_at),
    CONSTRAINT ck_sessions_revocation_after_creation CHECK (revoked_at IS NULL OR revoked_at >= created_at)
);

CREATE INDEX ix_sessions_user_id ON sessions (user_id);

CREATE TABLE cases (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    case_number BIGINT GENERATED ALWAYS AS IDENTITY,
    customer_id UUID NOT NULL,
    category_id UUID NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    affected_target VARCHAR(512),
    priority VARCHAR(12) DEFAULT 'medium' NOT NULL,
    status VARCHAR(24) DEFAULT 'open' NOT NULL,
    related_case_id UUID,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_cases PRIMARY KEY (id),
    CONSTRAINT uq_cases_case_number UNIQUE (case_number),
    CONSTRAINT fk_cases_customer_id_users FOREIGN KEY(customer_id) REFERENCES users (id) ON DELETE RESTRICT,
    CONSTRAINT fk_cases_category_id_issue_categories FOREIGN KEY(category_id) REFERENCES issue_categories (id) ON DELETE RESTRICT,
    CONSTRAINT fk_cases_related_case_id_cases FOREIGN KEY(related_case_id) REFERENCES cases (id) ON DELETE SET NULL,
    CONSTRAINT ck_cases_priority_valid CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    CONSTRAINT ck_cases_status_valid CHECK (status IN ('open', 'assigned', 'in_progress', 'resolved')),
    CONSTRAINT ck_cases_title_not_blank CHECK (char_length(btrim(title)) > 0),
    CONSTRAINT ck_cases_description_not_blank CHECK (char_length(btrim(description)) > 0),
    CONSTRAINT ck_cases_related_case_not_self CHECK (related_case_id IS NULL OR related_case_id <> id),
    CONSTRAINT ck_cases_resolution_time_matches_status CHECK ((status = 'resolved' AND resolved_at IS NOT NULL) OR (status <> 'resolved' AND resolved_at IS NULL)),
    CONSTRAINT ck_cases_resolution_after_creation CHECK (resolved_at IS NULL OR resolved_at >= created_at)
);

CREATE INDEX ix_cases_customer_id ON cases (customer_id);

CREATE INDEX ix_cases_category_id ON cases (category_id);

CREATE INDEX ix_cases_status ON cases (status);

CREATE INDEX ix_cases_related_case_id ON cases (related_case_id);

INSERT INTO issue_categories (id, slug, name) VALUES ('2e1b1d00-d373-578b-aa73-37d08884894d', 'networking', 'Networking');

INSERT INTO issue_categories (id, slug, name) VALUES ('264e3644-44b3-5954-b265-8b4c43166239', 'linux-docker', 'Linux & Docker');

INSERT INTO issue_categories (id, slug, name) VALUES ('0e4729fe-021f-52f8-a5e8-6c3b8289943f', 'application', 'Application errors');

INSERT INTO issue_categories (id, slug, name) VALUES ('1a39356f-2243-54b8-b9b9-06a12bcf356e', 'security', 'Security');

INSERT INTO issue_categories (id, slug, name) VALUES ('bf0e9a0b-180c-5df6-b86f-aba53d171eee', 'other', 'Other');

INSERT INTO alembic_version (version_num) VALUES ('0001_accounts_categories_cases') RETURNING alembic_version.version_num;

-- Running upgrade 0001_accounts_categories_cases -> 0002_case_assignments

CREATE TABLE case_assignments (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    case_id UUID NOT NULL,
    engineer_id UUID NOT NULL,
    assigned_by_id UUID NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    ended_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    CONSTRAINT pk_case_assignments PRIMARY KEY (id),
    CONSTRAINT fk_case_assignments_case_id_cases FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE RESTRICT,
    CONSTRAINT fk_case_assignments_engineer_id_users FOREIGN KEY(engineer_id) REFERENCES users (id) ON DELETE RESTRICT,
    CONSTRAINT fk_case_assignments_assigned_by_id_users FOREIGN KEY(assigned_by_id) REFERENCES users (id) ON DELETE RESTRICT,
    CONSTRAINT uq_case_assignments_resolution_reference UNIQUE (id, case_id, engineer_id),
    CONSTRAINT ck_case_assignments_end_after_start CHECK (ended_at IS NULL OR ended_at >= assigned_at),
    CONSTRAINT ck_case_assignments_notes_not_blank CHECK (notes IS NULL OR char_length(btrim(notes)) > 0)
);

CREATE UNIQUE INDEX uq_case_assignments_active_case ON case_assignments (case_id) WHERE ended_at IS NULL;

CREATE INDEX ix_case_assignments_engineer_active ON case_assignments (engineer_id, case_id) WHERE ended_at IS NULL;

CREATE INDEX ix_case_assignments_case_history ON case_assignments (case_id, assigned_at);

UPDATE alembic_version SET version_num='0002_case_assignments' WHERE alembic_version.version_num = '0001_accounts_categories_cases';

-- Running upgrade 0002_case_assignments -> 0003_case_resolutions

CREATE TABLE case_resolutions (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    case_id UUID NOT NULL,
    assignment_id UUID NOT NULL,
    resolved_by_id UUID NOT NULL,
    root_cause TEXT NOT NULL,
    fix_summary TEXT NOT NULL,
    customer_summary TEXT NOT NULL,
    prevention_notes TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    search_document TSVECTOR GENERATED ALWAYS AS (to_tsvector('english'::regconfig, root_cause || ' ' || fix_summary || ' ' || coalesce(prevention_notes, ''))) STORED NOT NULL,
    CONSTRAINT pk_case_resolutions PRIMARY KEY (id),
    CONSTRAINT fk_case_resolutions_case_id_cases FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE RESTRICT,
    CONSTRAINT fk_case_resolutions_resolved_by_id_users FOREIGN KEY(resolved_by_id) REFERENCES users (id) ON DELETE RESTRICT,
    CONSTRAINT fk_case_resolutions_assignment_engineer FOREIGN KEY(assignment_id, case_id, resolved_by_id) REFERENCES case_assignments (id, case_id, engineer_id) ON DELETE RESTRICT,
    CONSTRAINT ck_case_resolutions_root_cause_not_blank CHECK (char_length(btrim(root_cause)) > 0),
    CONSTRAINT ck_case_resolutions_fix_not_blank CHECK (char_length(btrim(fix_summary)) > 0),
    CONSTRAINT ck_case_resolutions_customer_summary_not_blank CHECK (char_length(btrim(customer_summary)) > 0),
    CONSTRAINT ck_case_resolutions_prevention_not_blank CHECK (prevention_notes IS NULL OR char_length(btrim(prevention_notes)) > 0)
);

CREATE INDEX ix_case_resolutions_case_history ON case_resolutions (case_id, resolved_at);

CREATE INDEX ix_case_resolutions_search ON case_resolutions USING gin (search_document);

UPDATE alembic_version SET version_num='0003_case_resolutions' WHERE alembic_version.version_num = '0002_case_assignments';

-- Running upgrade 0003_case_resolutions -> 0004_case_events

CREATE TABLE case_events (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    case_id UUID NOT NULL,
    actor_id UUID NOT NULL,
    event_type VARCHAR(24) NOT NULL,
    visibility VARCHAR(16) DEFAULT 'internal' NOT NULL,
    details JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_case_events PRIMARY KEY (id),
    CONSTRAINT fk_case_events_case_id_cases FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE RESTRICT,
    CONSTRAINT fk_case_events_actor_id_users FOREIGN KEY(actor_id) REFERENCES users (id) ON DELETE RESTRICT,
    CONSTRAINT uq_case_events_notification_reference UNIQUE (id, case_id),
    CONSTRAINT ck_case_events_type_valid CHECK (event_type IN ('created', 'assigned', 'reassigned', 'started', 'resolved', 'reopened')),
    CONSTRAINT ck_case_events_visibility_valid CHECK (visibility IN ('internal', 'customer')),
    CONSTRAINT ck_case_events_details_object CHECK (jsonb_typeof(details) = 'object')
);

CREATE INDEX ix_case_events_timeline ON case_events (case_id, created_at);

CREATE FUNCTION prevent_case_event_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'Case events are append-only' USING ERRCODE = '23514';
            RETURN NULL;
        END;
        $$;;

CREATE TRIGGER case_events_append_only
        BEFORE UPDATE OR DELETE ON case_events
        FOR EACH ROW EXECUTE FUNCTION prevent_case_event_mutation();;

UPDATE alembic_version SET version_num='0004_case_events' WHERE alembic_version.version_num = '0003_case_resolutions';

-- Running upgrade 0004_case_events -> 0005_case_notifications

CREATE TABLE notifications (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    recipient_id UUID NOT NULL,
    case_id UUID NOT NULL,
    event_id UUID NOT NULL,
    kind VARCHAR(24) NOT NULL,
    message TEXT NOT NULL,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_notifications PRIMARY KEY (id),
    CONSTRAINT fk_notifications_recipient_id_users FOREIGN KEY(recipient_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_notifications_case_id_cases FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE RESTRICT,
    CONSTRAINT fk_notifications_event_case FOREIGN KEY(event_id, case_id) REFERENCES case_events (id, case_id) ON DELETE RESTRICT,
    CONSTRAINT uq_notifications_recipient_event UNIQUE (recipient_id, event_id),
    CONSTRAINT ck_notifications_kind_valid CHECK (kind IN ('case_created', 'case_assigned', 'case_resolved', 'case_reopened')),
    CONSTRAINT ck_notifications_message_not_blank CHECK (char_length(btrim(message)) > 0),
    CONSTRAINT ck_notifications_read_after_creation CHECK (read_at IS NULL OR read_at >= created_at)
);

CREATE INDEX ix_notifications_unread ON notifications (recipient_id, created_at) WHERE read_at IS NULL;

CREATE INDEX ix_notifications_case_id ON notifications (case_id);

UPDATE alembic_version SET version_num='0005_case_notifications' WHERE alembic_version.version_num = '0004_case_events';

COMMIT;
