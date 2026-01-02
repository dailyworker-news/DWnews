-- Migration: Automated Journalism Pipeline Schema Extensions
-- Version: 001
-- Date: 2026-01-01
-- Description: Adds tables and columns for automated journalism workflow (Batch 6)
-- Compatible with: SQLite (local) and PostgreSQL (cloud)

-- ============================================================================
-- NEW TABLES
-- ============================================================================

-- Event Candidates Table
-- Stores discovered events from Signal Intake Agent for newsworthiness evaluation
CREATE TABLE IF NOT EXISTS event_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Event details
    title TEXT NOT NULL,
    description TEXT,
    source_url TEXT,
    discovered_from TEXT, -- RSS feed, Twitter, Reddit, etc.

    -- Event metadata
    event_date TIMESTAMP,
    discovery_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Newsworthiness scoring (evaluated by Evaluation Agent)
    worker_impact_score REAL, -- 0-10: Impact on working-class people
    timeliness_score REAL, -- 0-10: How timely/urgent is this
    verifiability_score REAL, -- 0-10: How verifiable with credible sources
    regional_relevance_score REAL, -- 0-10: Regional importance
    final_newsworthiness_score REAL, -- Weighted average

    -- Topic categorization
    suggested_category TEXT,
    keywords TEXT, -- JSON array or comma-separated

    -- Regional classification
    is_national BOOLEAN DEFAULT 0,
    is_local BOOLEAN DEFAULT 0,
    region_id INTEGER,

    -- Processing status
    status TEXT DEFAULT 'discovered' CHECK(status IN (
        'discovered',      -- Just found
        'evaluated',       -- Scored by Evaluation Agent
        'approved',        -- Passed threshold, ready for article generation
        'rejected',        -- Below threshold
        'converted'        -- Converted to article
    )),
    rejection_reason TEXT,

    -- Links to generated content
    topic_id INTEGER, -- Link to topics table if converted
    article_id INTEGER, -- Link to articles table if generated

    -- Timestamps
    evaluated_at TIMESTAMP,
    converted_at TIMESTAMP,

    -- Relationships
    FOREIGN KEY (region_id) REFERENCES regions(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id),
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

-- Article Revisions Table
-- Tracks all revisions made to articles (by AI agents and human editors)
CREATE TABLE IF NOT EXISTS article_revisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,

    -- Revision metadata
    revision_number INTEGER NOT NULL, -- Sequential revision count
    revised_by TEXT NOT NULL, -- Agent name or editor username
    revision_type TEXT NOT NULL CHECK(revision_type IN (
        'draft',           -- Initial draft
        'ai_edit',         -- AI agent edit
        'human_edit',      -- Human editor edit
        'fact_check',      -- Fact-checking revision
        'bias_correction', -- Bias scan correction
        'copy_edit'        -- Copy editing
    )),

    -- Changed fields (NULL if not changed in this revision)
    title_before TEXT,
    title_after TEXT,
    body_before TEXT,
    body_after TEXT,
    summary_before TEXT,
    summary_after TEXT,

    -- Revision notes
    change_summary TEXT, -- Brief description of changes
    change_reason TEXT, -- Why changes were made

    -- Verification data
    sources_verified BOOLEAN DEFAULT 0,
    bias_check_passed BOOLEAN,
    reading_level_before REAL,
    reading_level_after REAL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Relationships
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- Corrections Table
-- Post-publication corrections with transparency tracking
CREATE TABLE IF NOT EXISTS corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,

    -- Correction details
    correction_type TEXT NOT NULL CHECK(correction_type IN (
        'factual_error',      -- Incorrect fact
        'source_error',       -- Source misattribution
        'clarification',      -- Needs clarification
        'update',             -- New information available
        'retraction'          -- Full or partial retraction
    )),

    -- What was wrong
    incorrect_text TEXT NOT NULL,
    correct_text TEXT NOT NULL,
    section_affected TEXT, -- headline, body, summary, etc.

    -- Correction metadata
    severity TEXT DEFAULT 'minor' CHECK(severity IN ('minor', 'moderate', 'major', 'critical')),
    description TEXT NOT NULL, -- Explanation of what was wrong

    -- Discovery
    reported_by TEXT, -- Who found the error (reader, editor, agent)
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Resolution
    corrected_by TEXT, -- Editor who made the correction
    corrected_at TIMESTAMP,

    -- Transparency
    public_notice TEXT, -- Public correction notice shown to readers
    is_published BOOLEAN DEFAULT 0, -- Is correction notice published
    published_at TIMESTAMP,

    -- Status
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'verified', 'corrected', 'published')),

    -- Relationships
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- Source Reliability Log Table
-- Learning loop for source credibility tracking
CREATE TABLE IF NOT EXISTS source_reliability_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,

    -- Event details
    event_type TEXT NOT NULL CHECK(event_type IN (
        'article_published',   -- Article using this source published
        'correction_issued',   -- Correction needed for article citing this source
        'fact_check_pass',     -- Source information verified
        'fact_check_fail',     -- Source information contradicted
        'retraction',          -- Article retracted due to source issue
        'citation_added'       -- Source cited in new article
    )),

    -- Impact on reliability
    reliability_delta REAL, -- +/- change to credibility score
    previous_score INTEGER,
    new_score INTEGER,

    -- Context
    article_id INTEGER, -- Related article if applicable
    correction_id INTEGER, -- Related correction if applicable
    notes TEXT,

    -- Automated learning
    automated_adjustment BOOLEAN DEFAULT 0, -- Was this auto-adjusted by agent?
    manual_override BOOLEAN DEFAULT 0, -- Was this manually set by human?
    reviewed_by TEXT, -- Human reviewer if manual

    -- Timestamps
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Relationships
    FOREIGN KEY (source_id) REFERENCES sources(id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE SET NULL,
    FOREIGN KEY (correction_id) REFERENCES corrections(id) ON DELETE SET NULL
);

-- ============================================================================
-- COLUMN ADDITIONS TO EXISTING TABLES
-- ============================================================================

-- Add new columns to articles table for automated journalism workflow
-- Note: SQLite doesn't support multiple columns in one ALTER TABLE, so we do them separately

ALTER TABLE articles ADD COLUMN bias_scan_report TEXT; -- JSON report from bias detection scan
ALTER TABLE articles ADD COLUMN self_audit_passed BOOLEAN DEFAULT 0; -- Did article pass self-audit?
ALTER TABLE articles ADD COLUMN editorial_notes TEXT; -- Notes from human editors
ALTER TABLE articles ADD COLUMN assigned_editor TEXT; -- Editor assigned to review this article
ALTER TABLE articles ADD COLUMN review_deadline TIMESTAMP; -- When review must be completed

-- Add new columns to topics table for verification workflow
ALTER TABLE topics ADD COLUMN verified_facts TEXT; -- JSON array of verified facts
ALTER TABLE topics ADD COLUMN source_plan TEXT; -- JSON: planned sources for verification
ALTER TABLE topics ADD COLUMN verification_status TEXT DEFAULT 'pending' CHECK(verification_status IN (
    'pending',        -- Not yet verified
    'in_progress',    -- Verification in progress
    'verified',       -- All facts verified
    'partial',        -- Some facts verified
    'failed'          -- Could not verify
));

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Event Candidates indexes
CREATE INDEX IF NOT EXISTS idx_event_candidates_status ON event_candidates(status);
CREATE INDEX IF NOT EXISTS idx_event_candidates_discovery_date ON event_candidates(discovery_date DESC);
CREATE INDEX IF NOT EXISTS idx_event_candidates_newsworthiness ON event_candidates(final_newsworthiness_score DESC);
CREATE INDEX IF NOT EXISTS idx_event_candidates_topic_id ON event_candidates(topic_id);
CREATE INDEX IF NOT EXISTS idx_event_candidates_article_id ON event_candidates(article_id);

-- Article Revisions indexes
CREATE INDEX IF NOT EXISTS idx_article_revisions_article ON article_revisions(article_id);
CREATE INDEX IF NOT EXISTS idx_article_revisions_created ON article_revisions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_article_revisions_type ON article_revisions(revision_type);

-- Corrections indexes
CREATE INDEX IF NOT EXISTS idx_corrections_article ON corrections(article_id);
CREATE INDEX IF NOT EXISTS idx_corrections_status ON corrections(status);
CREATE INDEX IF NOT EXISTS idx_corrections_severity ON corrections(severity);
CREATE INDEX IF NOT EXISTS idx_corrections_published ON corrections(is_published) WHERE is_published = 1;

-- Source Reliability Log indexes
CREATE INDEX IF NOT EXISTS idx_source_reliability_source ON source_reliability_log(source_id);
CREATE INDEX IF NOT EXISTS idx_source_reliability_logged ON source_reliability_log(logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_source_reliability_event ON source_reliability_log(event_type);

-- Updated articles indexes for new columns
CREATE INDEX IF NOT EXISTS idx_articles_assigned_editor ON articles(assigned_editor);
CREATE INDEX IF NOT EXISTS idx_articles_review_deadline ON articles(review_deadline);
CREATE INDEX IF NOT EXISTS idx_articles_self_audit ON articles(self_audit_passed);

-- Updated topics indexes
CREATE INDEX IF NOT EXISTS idx_topics_verification_status ON topics(verification_status);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: High-priority event candidates (approved for article generation)
CREATE VIEW IF NOT EXISTS approved_event_candidates AS
SELECT
    ec.*,
    c.name as category_name,
    r.name as region_name
FROM event_candidates ec
LEFT JOIN categories c ON ec.suggested_category = c.slug
LEFT JOIN regions r ON ec.region_id = r.id
WHERE ec.status = 'approved'
ORDER BY ec.final_newsworthiness_score DESC;

-- View: Articles pending review with deadlines
CREATE VIEW IF NOT EXISTS articles_pending_review AS
SELECT
    a.id,
    a.title,
    a.assigned_editor,
    a.review_deadline,
    a.self_audit_passed,
    c.name as category_name,
    a.created_at,
    CASE
        WHEN a.review_deadline < CURRENT_TIMESTAMP THEN 1
        ELSE 0
    END as is_overdue
FROM articles a
LEFT JOIN categories c ON a.category_id = c.id
WHERE a.status = 'pending_review'
ORDER BY a.review_deadline ASC;

-- View: Article revision history
CREATE VIEW IF NOT EXISTS article_revision_history AS
SELECT
    ar.*,
    a.title as article_title,
    a.status as article_status
FROM article_revisions ar
JOIN articles a ON ar.article_id = a.id
ORDER BY ar.article_id, ar.revision_number DESC;

-- View: Published corrections (for transparency page)
CREATE VIEW IF NOT EXISTS published_corrections AS
SELECT
    c.*,
    a.title as article_title,
    a.slug as article_slug,
    a.published_at as article_published_at
FROM corrections c
JOIN articles a ON c.article_id = a.id
WHERE c.is_published = 1
ORDER BY c.published_at DESC;

-- View: Source reliability trends
CREATE VIEW IF NOT EXISTS source_reliability_trends AS
SELECT
    s.id as source_id,
    s.name as source_name,
    s.credibility_score as current_score,
    COUNT(srl.id) as event_count,
    SUM(CASE WHEN srl.event_type = 'fact_check_pass' THEN 1 ELSE 0 END) as pass_count,
    SUM(CASE WHEN srl.event_type = 'fact_check_fail' THEN 1 ELSE 0 END) as fail_count,
    SUM(CASE WHEN srl.event_type = 'correction_issued' THEN 1 ELSE 0 END) as correction_count,
    AVG(srl.reliability_delta) as avg_delta
FROM sources s
LEFT JOIN source_reliability_log srl ON s.id = srl.source_id
GROUP BY s.id
ORDER BY s.credibility_score DESC;

-- ============================================================================
-- PostgreSQL Compatibility Notes
-- ============================================================================
-- When migrating to PostgreSQL, replace:
-- 1. INTEGER PRIMARY KEY AUTOINCREMENT → SERIAL PRIMARY KEY or BIGSERIAL PRIMARY KEY
-- 2. BOOLEAN 0/1 → BOOLEAN true/false
-- 3. TIMESTAMP → TIMESTAMP or TIMESTAMPTZ for timezone awareness
-- 4. TEXT → TEXT or VARCHAR(n) for size constraints
-- 5. REAL → REAL or NUMERIC(p,s) for precision
--
-- PostgreSQL benefits:
-- - JSONB columns for structured data (bias_scan_report, verified_facts, etc.)
-- - Full-text search indexes for title/description fields
-- - Partial indexes with WHERE clauses (already compatible)
-- - Materialized views for performance
-- ============================================================================
