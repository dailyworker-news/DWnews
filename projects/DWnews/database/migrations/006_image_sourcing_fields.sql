-- Migration 006: Image Sourcing & Generation Fields
-- Adds fields to support multi-tier image sourcing strategy
-- Phase 6.11: Image Sourcing & Generation Agent

-- Add new image-related columns to articles table
-- Note: SQLite doesn't support CHECK constraints in ALTER TABLE ADD COLUMN
-- Constraints will be enforced at application level

ALTER TABLE articles ADD COLUMN image_source_type TEXT DEFAULT 'placeholder';

ALTER TABLE articles ADD COLUMN gemini_prompt TEXT;

ALTER TABLE articles ADD COLUMN image_license TEXT;

ALTER TABLE articles ADD COLUMN generated_by_gemini INTEGER DEFAULT 0;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_articles_image_source_type ON articles(image_source_type);

CREATE INDEX IF NOT EXISTS idx_articles_generated_by_gemini ON articles(generated_by_gemini)
    WHERE generated_by_gemini = 1;

-- Update existing articles to have proper image_source_type
-- Based on their current image_source field
UPDATE articles
SET image_source_type = CASE
    WHEN image_source = 'Unsplash' OR image_source = 'Pexels' THEN 'stock'
    WHEN image_source IS NOT NULL AND image_source != '' THEN 'extracted'
    ELSE 'placeholder'
END
WHERE image_source_type = 'placeholder';

-- Migration metadata
-- Version: 006
-- Date: 2026-01-02
-- Phase: 6.11
-- Description: Add image sourcing and Gemini generation tracking fields
