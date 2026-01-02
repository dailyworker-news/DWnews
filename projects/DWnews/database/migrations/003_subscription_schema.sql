-- Migration 003: Subscription System Schema
-- Phase 7.1: Database Schema for Subscriptions
-- Date: 2026-01-01
-- Description: Adds subscription, payment, invoicing, and sports configuration tables

-- ============================================================
-- SUBSCRIPTION TABLES
-- ============================================================

-- Subscription Plans Table
CREATE TABLE IF NOT EXISTS subscription_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_name TEXT NOT NULL UNIQUE,
    price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
    billing_interval TEXT NOT NULL CHECK(billing_interval IN ('monthly', 'yearly')),
    features_json TEXT, -- JSON object with plan features (sports access, article limits, etc.)
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    stripe_subscription_id TEXT UNIQUE, -- Stripe's subscription ID
    plan_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('active', 'canceled', 'past_due', 'trialing', 'incomplete', 'incomplete_expired', 'unpaid')),
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT 0,
    canceled_at TIMESTAMP,
    trial_start TIMESTAMP,
    trial_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id)
);

-- Payment Methods Table
CREATE TABLE IF NOT EXISTS payment_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    stripe_payment_method_id TEXT NOT NULL UNIQUE,
    card_brand TEXT, -- visa, mastercard, amex, etc.
    last4 TEXT, -- last 4 digits of card
    exp_month INTEGER,
    exp_year INTEGER,
    is_default BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Invoices Table
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subscription_id INTEGER,
    stripe_invoice_id TEXT UNIQUE,
    amount_cents INTEGER NOT NULL,
    amount_paid_cents INTEGER DEFAULT 0,
    status TEXT NOT NULL CHECK(status IN ('draft', 'open', 'paid', 'void', 'uncollectible')),
    paid_at TIMESTAMP,
    invoice_url TEXT, -- Stripe-hosted invoice URL
    invoice_pdf TEXT, -- Stripe-hosted PDF URL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
);

-- Subscription Events Table (Audit Log)
CREATE TABLE IF NOT EXISTS subscription_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscription_id INTEGER,
    user_id INTEGER NOT NULL,
    event_type TEXT NOT NULL, -- subscription_created, subscription_updated, payment_succeeded, payment_failed, etc.
    event_data_json TEXT, -- JSON payload from Stripe webhook or internal event
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- USER TABLE
-- ============================================================

-- Create users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'subscriber' CHECK(role IN ('admin', 'editor', 'subscriber')),
    subscription_status TEXT DEFAULT 'free' CHECK(subscription_status IN ('free', 'active', 'canceled', 'past_due', 'trialing')),
    subscriber_since TIMESTAMP,
    free_article_count INTEGER DEFAULT 0,
    last_article_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferred_state_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Note: If users table already exists, the above CREATE will be skipped.
-- For existing deployments with a users table, manually add these columns:
-- ALTER TABLE users ADD COLUMN subscription_status TEXT DEFAULT 'free';
-- ALTER TABLE users ADD COLUMN subscriber_since TIMESTAMP;
-- ALTER TABLE users ADD COLUMN free_article_count INTEGER DEFAULT 0;
-- ALTER TABLE users ADD COLUMN last_article_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- ============================================================
-- ARTICLE TABLE UPDATES
-- ============================================================

-- Add premium flag to articles table
ALTER TABLE articles ADD COLUMN is_premium BOOLEAN DEFAULT 0;
ALTER TABLE articles ADD COLUMN sports_league_id INTEGER REFERENCES sports_leagues(id);

-- ============================================================
-- SPORTS CONFIGURATION TABLES
-- ============================================================

-- Sports Leagues Table
CREATE TABLE IF NOT EXISTS sports_leagues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_code TEXT NOT NULL UNIQUE, -- EPL, NBA, NFL, MLB, etc.
    name TEXT NOT NULL,
    country TEXT,
    tier_requirement TEXT NOT NULL CHECK(tier_requirement IN ('free', 'basic', 'premium')),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Sports Preferences Table
CREATE TABLE IF NOT EXISTS user_sports_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    league_id INTEGER NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, league_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (league_id) REFERENCES sports_leagues(id)
);

-- Sports Results Table
CREATE TABLE IF NOT EXISTS sports_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    match_date DATE NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    score TEXT, -- e.g., "2-1", "104-98"
    summary TEXT, -- Brief match summary
    article_id INTEGER, -- Link to generated article
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (league_id) REFERENCES sports_leagues(id),
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_id ON subscriptions(stripe_subscription_id);

CREATE INDEX IF NOT EXISTS idx_payment_methods_user_id ON payment_methods(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_methods_default ON payment_methods(user_id, is_default);

CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_subscription_id ON invoices(subscription_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);

CREATE INDEX IF NOT EXISTS idx_subscription_events_subscription_id ON subscription_events(subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscription_events_user_id ON subscription_events(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_events_type ON subscription_events(event_type);

CREATE INDEX IF NOT EXISTS idx_user_sports_prefs_user_id ON user_sports_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sports_prefs_league_id ON user_sports_preferences(league_id);

CREATE INDEX IF NOT EXISTS idx_sports_results_league_date ON sports_results(league_id, match_date);
CREATE INDEX IF NOT EXISTS idx_articles_premium ON articles(is_premium);
CREATE INDEX IF NOT EXISTS idx_articles_sports_league ON articles(sports_league_id);

-- ============================================================
-- SEED DATA - DEFAULT SUBSCRIPTION PLANS
-- ============================================================

INSERT INTO subscription_plans (plan_name, price_cents, billing_interval, features_json) VALUES
    ('Free Tier', 0, 'monthly', '{"article_limit": 3, "sports_access": "none", "archive_access": false}'),
    ('Basic Subscriber', 1500, 'monthly', '{"article_limit": -1, "sports_access": "one_league", "archive_access": true}'),
    ('Premium Subscriber', 2500, 'monthly', '{"article_limit": -1, "sports_access": "unlimited", "archive_access": true, "exclusive_analysis": true}');

-- ============================================================
-- SEED DATA - SPORTS LEAGUES (INITIAL SET)
-- ============================================================

INSERT INTO sports_leagues (league_code, name, country, tier_requirement) VALUES
    ('EPL', 'English Premier League', 'England', 'basic'),
    ('NBA', 'National Basketball Association', 'USA', 'basic'),
    ('NFL', 'National Football League', 'USA', 'basic'),
    ('MLB', 'Major League Baseball', 'USA', 'basic'),
    ('NHL', 'National Hockey League', 'USA/Canada', 'basic'),
    ('MLS', 'Major League Soccer', 'USA/Canada', 'basic'),
    ('LA_LIGA', 'La Liga', 'Spain', 'premium'),
    ('BUNDESLIGA', 'Bundesliga', 'Germany', 'premium'),
    ('SERIE_A', 'Serie A', 'Italy', 'premium'),
    ('CHAMPIONS_LEAGUE', 'UEFA Champions League', 'Europe', 'premium');

-- ============================================================
-- MIGRATION COMPLETE
-- ============================================================
