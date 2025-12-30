-- The Daily Worker - Database Schema
-- Supports local and cloud deployment (SQLite or PostgreSQL)

-- News Sources Table
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    rss_feed TEXT,
    credibility_score INTEGER DEFAULT 5 CHECK(credibility_score BETWEEN 1 AND 5),
    source_type TEXT NOT NULL CHECK(source_type IN ('news_wire', 'investigative', 'academic', 'local', 'social')),
    political_lean TEXT DEFAULT 'center' CHECK(political_lean IN ('left', 'center-left', 'center', 'center-right', 'right')),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regions Table
CREATE TABLE IF NOT EXISTS regions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    region_type TEXT NOT NULL CHECK(region_type IN ('national', 'state', 'city', 'metro')),
    state_code TEXT,
    population INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1
);

-- Articles Table
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
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

    -- Status
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'pending_review', 'approved', 'published', 'archived')),

    -- Publishing
    published_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Relationships
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (region_id) REFERENCES regions(id)
);

-- Article Sources Junction Table (many-to-many)
CREATE TABLE IF NOT EXISTS article_sources (
    article_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    citation_url TEXT,
    citation_text TEXT,
    PRIMARY KEY (article_id, source_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- Topics Table (for content discovery)
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    keywords TEXT,

    -- Discovery metadata
    discovered_from TEXT,
    discovery_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Viability checks
    source_count INTEGER DEFAULT 0,
    academic_citation_count INTEGER DEFAULT 0,
    worker_relevance_score REAL,
    engagement_score REAL,

    -- Categorization
    category_id INTEGER,
    is_national BOOLEAN DEFAULT 0,
    is_local BOOLEAN DEFAULT 0,
    region_id INTEGER,

    -- Processing status
    status TEXT DEFAULT 'discovered' CHECK(status IN ('discovered', 'filtered', 'approved', 'rejected', 'generated')),
    rejection_reason TEXT,

    -- Relationships
    article_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (region_id) REFERENCES regions(id),
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category_id);
CREATE INDEX IF NOT EXISTS idx_articles_region ON articles(region_id);
CREATE INDEX IF NOT EXISTS idx_articles_national ON articles(is_national) WHERE is_national = 1;
CREATE INDEX IF NOT EXISTS idx_articles_local ON articles(is_local) WHERE is_local = 1;
CREATE INDEX IF NOT EXISTS idx_articles_ongoing ON articles(is_ongoing) WHERE is_ongoing = 1;
CREATE INDEX IF NOT EXISTS idx_articles_new ON articles(is_new) WHERE is_new = 1;
CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug);

CREATE INDEX IF NOT EXISTS idx_topics_status ON topics(status);
CREATE INDEX IF NOT EXISTS idx_topics_category ON topics(category_id);
CREATE INDEX IF NOT EXISTS idx_topics_discovery_date ON topics(discovery_date DESC);

CREATE INDEX IF NOT EXISTS idx_sources_active ON sources(is_active) WHERE is_active = 1;
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(source_type);

-- Triggers for updated_at (SQLite compatible)
CREATE TRIGGER IF NOT EXISTS update_articles_timestamp
AFTER UPDATE ON articles
BEGIN
    UPDATE articles SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_sources_timestamp
AFTER UPDATE ON sources
BEGIN
    UPDATE sources SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Views for common queries
CREATE VIEW IF NOT EXISTS published_articles AS
SELECT
    a.*,
    c.name as category_name,
    c.slug as category_slug,
    r.name as region_name
FROM articles a
LEFT JOIN categories c ON a.category_id = c.id
LEFT JOIN regions r ON a.region_id = r.id
WHERE a.status = 'published'
ORDER BY a.published_at DESC;

CREATE VIEW IF NOT EXISTS article_source_count AS
SELECT
    a.id,
    a.title,
    COUNT(ast.source_id) as source_count
FROM articles a
LEFT JOIN article_sources ast ON a.id = ast.article_id
GROUP BY a.id;
