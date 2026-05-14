CREATE TABLE IF NOT EXISTS topics (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'developing',
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    schedule_frequency TEXT NOT NULL DEFAULT 'manual',
    schedule_time_utc TEXT,
    schedule_day_of_week TEXT,
    schedule_day_of_month INTEGER,
    last_run_date DATE,
    next_scheduled_run DATE,
    strategy_rotation JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    topic_path TEXT,
    source_path TEXT,
    brief_path TEXT,
    topic_data_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_topics_category ON topics (category);
CREATE INDEX IF NOT EXISTS idx_topics_status ON topics (status);

CREATE TABLE IF NOT EXISTS topic_documents (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT NOT NULL REFERENCES topics (id) ON DELETE CASCADE,
    document_type TEXT NOT NULL,
    path TEXT,
    content TEXT NOT NULL DEFAULT '',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (topic_id, document_type, path)
);

CREATE INDEX IF NOT EXISTS idx_topic_documents_topic_id ON topic_documents (topic_id);

CREATE TABLE IF NOT EXISTS briefs (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT NOT NULL UNIQUE REFERENCES topics (id) ON DELETE CASCADE,
    title TEXT,
    bottom_line TEXT,
    key_takeaways TEXT,
    content TEXT NOT NULL DEFAULT '',
    path TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS source_logs (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT NOT NULL UNIQUE REFERENCES topics (id) ON DELETE CASCADE,
    path TEXT,
    content TEXT NOT NULL DEFAULT '',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS source_entries (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT NOT NULL REFERENCES topics (id) ON DELETE CASCADE,
    source_type TEXT,
    title TEXT,
    url TEXT,
    source_date TEXT,
    accessed_on DATE,
    notes TEXT,
    confidence TEXT,
    raw_entry TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_source_entries_topic_id ON source_entries (topic_id);
CREATE INDEX IF NOT EXISTS idx_source_entries_url ON source_entries (url);

CREATE TABLE IF NOT EXISTS research_runs (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT REFERENCES topics (id) ON DELETE SET NULL,
    slug TEXT NOT NULL,
    run_key TEXT NOT NULL UNIQUE,
    run_type TEXT NOT NULL DEFAULT 'deep',
    strategy TEXT,
    model TEXT,
    generated_at TIMESTAMPTZ,
    api_cost_usd NUMERIC(10, 4) NOT NULL DEFAULT 0,
    skipped_api_call BOOLEAN NOT NULL DEFAULT FALSE,
    summary TEXT,
    path TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_research_runs_slug ON research_runs (slug);
CREATE INDEX IF NOT EXISTS idx_research_runs_generated_at ON research_runs (generated_at);

CREATE TABLE IF NOT EXISTS topic_metrics (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT NOT NULL REFERENCES topics (id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    value_text TEXT,
    numeric_value NUMERIC,
    unit TEXT,
    date_label TEXT,
    context TEXT,
    source TEXT,
    confidence TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (topic_id, label, date_label, source)
);

CREATE INDEX IF NOT EXISTS idx_topic_metrics_topic_id ON topic_metrics (topic_id);

CREATE TABLE IF NOT EXISTS topic_comparisons (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT NOT NULL REFERENCES topics (id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    unit TEXT,
    source TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (topic_id, title, source)
);

CREATE TABLE IF NOT EXISTS comparison_items (
    id BIGSERIAL PRIMARY KEY,
    comparison_id BIGINT NOT NULL REFERENCES topic_comparisons (id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    value_text TEXT,
    numeric_value NUMERIC,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (comparison_id, label)
);

CREATE TABLE IF NOT EXISTS timeline_events (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT NOT NULL REFERENCES topics (id) ON DELETE CASCADE,
    event_date TEXT,
    event TEXT NOT NULL,
    significance TEXT,
    source TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (topic_id, event_date, event)
);

CREATE INDEX IF NOT EXISTS idx_timeline_events_topic_id ON timeline_events (topic_id);

CREATE TABLE IF NOT EXISTS topic_tables (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT NOT NULL REFERENCES topics (id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    columns JSONB NOT NULL DEFAULT '[]'::jsonb,
    rows JSONB NOT NULL DEFAULT '[]'::jsonb,
    source TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (topic_id, title, source)
);

CREATE TABLE IF NOT EXISTS data_gaps (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT NOT NULL REFERENCES topics (id) ON DELETE CASCADE,
    gap TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    source TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (topic_id, gap)
);

CREATE INDEX IF NOT EXISTS idx_data_gaps_topic_id ON data_gaps (topic_id);

CREATE TABLE IF NOT EXISTS research_artifacts (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT REFERENCES topics (id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    path TEXT,
    content_hash TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (slug, artifact_type, path)
);
