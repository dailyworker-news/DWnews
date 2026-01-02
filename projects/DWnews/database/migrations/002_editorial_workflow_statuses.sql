-- Migration 002: Editorial Workflow Statuses
-- Add new status values for editorial workflow integration
-- Phase 6.6: Editorial Workflow Integration
-- Date: 2026-01-01

-- SQLite doesn't support ALTER TABLE to modify constraints
-- We need to recreate the table with the updated constraint

BEGIN TRANSACTION;

-- Create temporary table with new schema
CREATE TABLE articles_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    body TEXT NOT NULL,
    summary TEXT,

    -- Article metadata
    category_id INTEGER NOT NULL,
    author TEXT DEFAULT 'The Daily Worker Editorial Team',

    -- Regional flags
    is_national BOOLEAN DEFAULT 0,
    is_local BOOLEAN DEFAULT 0,
    region_id INTEGER,

    -- Story type flags
    is_ongoing BOOLEAN DEFAULT 0,
    is_new BOOLEAN DEFAULT 1,

    -- Content quality
    reading_level REAL,
    word_count INTEGER,

    -- Images
    image_url TEXT,
    image_attribution TEXT,
    image_source TEXT,

    -- Special sections
    why_this_matters TEXT,
    what_you_can_do TEXT,

    -- Status (UPDATED CONSTRAINT)
    status TEXT DEFAULT 'draft' CHECK (
        status IN (
            'draft',
            'pending_review',
            'under_review',
            'revision_requested',
            'approved',
            'published',
            'archived',
            'needs_senior_review'
        )
    ),

    -- Publishing
    published_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Automated journalism workflow (from migration 001)
    bias_scan_report TEXT,
    self_audit_passed BOOLEAN DEFAULT 0,
    editorial_notes TEXT,
    assigned_editor TEXT,
    review_deadline DATETIME,

    -- Foreign keys
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (region_id) REFERENCES regions(id)
);

-- Copy data from old table
INSERT INTO articles_new (
    id, title, slug, body, summary,
    category_id, author,
    is_national, is_local, region_id,
    is_ongoing, is_new,
    reading_level, word_count,
    image_url, image_attribution, image_source,
    why_this_matters, what_you_can_do,
    status,
    published_at, updated_at, created_at,
    bias_scan_report, self_audit_passed, editorial_notes,
    assigned_editor, review_deadline
)
SELECT
    id, title, slug, body, summary,
    category_id, author,
    is_national, is_local, region_id,
    is_ongoing, is_new,
    reading_level, word_count,
    image_url, image_attribution, image_source,
    why_this_matters, what_you_can_do,
    status,
    published_at, updated_at, created_at,
    bias_scan_report, self_audit_passed, editorial_notes,
    assigned_editor, review_deadline
FROM articles;

-- Drop old table
DROP TABLE articles;

-- Rename new table
ALTER TABLE articles_new RENAME TO articles;

-- Recreate indexes
CREATE INDEX idx_articles_category ON articles(category_id);
CREATE INDEX idx_articles_region ON articles(region_id);
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_published_at ON articles(published_at);
CREATE INDEX idx_articles_created_at ON articles(created_at);
CREATE INDEX idx_articles_slug ON articles(slug);

-- Recreate article_sources junction table if it doesn't exist
CREATE TABLE IF NOT EXISTS article_sources (
    article_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    citation_url TEXT,
    citation_text TEXT,
    PRIMARY KEY (article_id, source_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

COMMIT;

-- Verify migration
SELECT 'Migration 002 completed successfully' AS status;
SELECT COUNT(*) AS article_count FROM articles;
