-- Migration 005: Add Local Region Preference
-- Phase 7.4: Subscriber Dashboard & User Preferences
-- Date: 2026-01-02
-- Description: Adds local_region column to users table for local news personalization

-- Add local_region column to users table
ALTER TABLE users ADD COLUMN local_region TEXT;

-- Create index for efficient local region queries
CREATE INDEX IF NOT EXISTS idx_users_local_region ON users(local_region);

-- Migration complete
