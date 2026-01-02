-- Migration 004: Authentication & Access Control
-- Phase 7.3: Subscriber Authentication & Access Control
-- Date: 2026-01-02
-- Description: Adds user article tracking, A/B test configuration, and auth-based access control

-- ============================================================
-- USER ARTICLE TRACKING (AUTH-BASED)
-- ============================================================

-- User Article Reads Table (replaces IP-based tracking)
CREATE TABLE IF NOT EXISTS user_article_reads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    article_id INTEGER NOT NULL,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT, -- Optional: track reading sessions
    read_duration_seconds INTEGER DEFAULT 0, -- Time spent reading
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    UNIQUE(user_id, article_id) -- Prevent duplicate reads (count each article once per user)
);

-- ============================================================
-- A/B TEST CONFIGURATION
-- ============================================================

-- A/B Test Groups Table
CREATE TABLE IF NOT EXISTS ab_test_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL UNIQUE, -- e.g., "control", "test_2_per_day", "test_5_per_day", "test_3_per_week"
    description TEXT,
    article_limit_daily INTEGER, -- Daily article limit (-1 for unlimited)
    article_limit_weekly INTEGER, -- Weekly article limit (-1 for unlimited)
    article_limit_monthly INTEGER, -- Monthly article limit (-1 for unlimited)
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User A/B Test Assignment Table
CREATE TABLE IF NOT EXISTS user_ab_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    test_group_id INTEGER NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    converted_to_paid BOOLEAN DEFAULT 0, -- Track conversion to paid subscription
    converted_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (test_group_id) REFERENCES ab_test_groups(id),
    UNIQUE(user_id) -- One test group per user
);

-- A/B Test Metrics Table (conversion tracking)
CREATE TABLE IF NOT EXISTS ab_test_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_group_id INTEGER NOT NULL,
    metric_date DATE NOT NULL,
    total_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0, -- Users who read at least 1 article
    converted_users INTEGER DEFAULT 0, -- Users who subscribed
    avg_articles_read REAL DEFAULT 0.0,
    conversion_rate REAL DEFAULT 0.0, -- Percentage of users who converted
    FOREIGN KEY (test_group_id) REFERENCES ab_test_groups(id),
    UNIQUE(test_group_id, metric_date) -- One metric row per group per day
);

-- ============================================================
-- USER TABLE CREATION/UPDATES
-- ============================================================

-- Create users table if it doesn't exist (may have been created in migration 003)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    username TEXT UNIQUE, -- Optional username
    role TEXT DEFAULT 'subscriber' CHECK(role IN ('admin', 'editor', 'subscriber')),
    subscription_status TEXT DEFAULT 'free' CHECK(subscription_status IN ('free', 'active', 'canceled', 'past_due', 'trialing')),
    subscriber_since TIMESTAMP,
    free_article_count INTEGER DEFAULT 0,
    last_article_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    article_limit_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferred_state_id INTEGER,
    ab_test_group_id INTEGER REFERENCES ab_test_groups(id),
    stripe_customer_id TEXT UNIQUE, -- Stripe customer ID for payment processing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_user_article_reads_user_id ON user_article_reads(user_id);
CREATE INDEX IF NOT EXISTS idx_user_article_reads_article_id ON user_article_reads(article_id);
CREATE INDEX IF NOT EXISTS idx_user_article_reads_read_at ON user_article_reads(read_at);
CREATE INDEX IF NOT EXISTS idx_user_article_reads_user_article ON user_article_reads(user_id, article_id);

CREATE INDEX IF NOT EXISTS idx_user_ab_tests_user_id ON user_ab_tests(user_id);
CREATE INDEX IF NOT EXISTS idx_user_ab_tests_group_id ON user_ab_tests(test_group_id);
CREATE INDEX IF NOT EXISTS idx_user_ab_tests_converted ON user_ab_tests(converted_to_paid);

CREATE INDEX IF NOT EXISTS idx_ab_test_metrics_group_date ON ab_test_metrics(test_group_id, metric_date);

CREATE INDEX IF NOT EXISTS idx_users_ab_test_group ON users(ab_test_group_id);
CREATE INDEX IF NOT EXISTS idx_users_subscription_status ON users(subscription_status);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================================
-- SEED DATA - A/B TEST GROUPS (Phase 7.3 Requirements)
-- ============================================================

-- Per Business Analyst recommendations: Test 2/day vs 5/day vs 3/week vs no limit
INSERT INTO ab_test_groups (group_name, description, article_limit_daily, article_limit_weekly, article_limit_monthly) VALUES
    ('control_no_limit', 'Control group - No article limits for testing baseline', -1, -1, -1),
    ('test_2_per_day', 'Test Group A - 2 articles per day limit', 2, -1, -1),
    ('test_5_per_day', 'Test Group B - 5 articles per day limit', 5, -1, -1),
    ('test_3_per_week', 'Test Group C - 3 articles per week limit', -1, 3, -1);

-- ============================================================
-- MIGRATION COMPLETE
-- ============================================================
