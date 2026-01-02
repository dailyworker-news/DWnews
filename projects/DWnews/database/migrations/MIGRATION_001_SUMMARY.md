# Migration 001: Automated Journalism Pipeline Schema Extensions

**Date:** 2026-01-01
**Version:** 001
**Batch:** 6 - Automated Journalism Pipeline
**Phase:** 6.1 - Database Schema Extensions
**Status:** ✅ COMPLETE

## Overview

This migration adds database schema support for the automated journalism workflow, enabling the DWnews platform to discover, evaluate, verify, draft, and publish articles through a combination of AI agents and human editorial oversight.

## Changes Made

### New Tables (4)

#### 1. event_candidates
Stores events discovered by the Signal Intake Agent for newsworthiness evaluation.

**Key Columns:**
- `title`, `description`, `source_url` - Event details
- `discovered_from` - Source (RSS, Twitter, Reddit, government feed)
- `worker_impact_score`, `timeliness_score`, `verifiability_score`, `regional_relevance_score` - Scoring dimensions (0-10)
- `final_newsworthiness_score` - Weighted average score
- `status` - Workflow: discovered → evaluated → approved/rejected → converted

**Purpose:** Enables automated event discovery and prioritization

#### 2. article_revisions
Tracks all changes made to articles by AI agents and human editors.

**Key Columns:**
- `revision_number` - Sequential revision count
- `revised_by` - Agent name or editor username
- `revision_type` - draft, ai_edit, human_edit, fact_check, bias_correction, copy_edit
- `title_before/after`, `body_before/after`, `summary_before/after` - Change tracking
- `change_summary`, `change_reason` - Explanation of changes
- `sources_verified`, `bias_check_passed` - Quality gates

**Purpose:** Provides complete audit trail and revision history

#### 3. corrections
Manages post-publication corrections with full transparency.

**Key Columns:**
- `correction_type` - factual_error, source_error, clarification, update, retraction
- `incorrect_text`, `correct_text` - What was wrong and correction
- `severity` - minor, moderate, major, critical
- `public_notice` - Public-facing correction statement
- `is_published` - Whether correction is publicly visible

**Purpose:** Enables transparent error correction and builds reader trust

#### 4. source_reliability_log
Learning loop for source credibility tracking.

**Key Columns:**
- `event_type` - article_published, correction_issued, fact_check_pass/fail, retraction
- `reliability_delta` - Change to credibility score
- `previous_score`, `new_score` - Score tracking
- `automated_adjustment` - Was this auto-adjusted by agent?
- `manual_override` - Was this manually set by human?

**Purpose:** Continuous learning from corrections to improve source selection

### Extended Tables (2)

#### articles table - 5 new columns
- `bias_scan_report` (TEXT) - JSON report from bias detection scan
- `self_audit_passed` (BOOLEAN) - Did article pass self-audit?
- `editorial_notes` (TEXT) - Notes from human editors
- `assigned_editor` (TEXT) - Editor assigned to review
- `review_deadline` (TIMESTAMP) - When review must be completed

**Purpose:** Editorial workflow management and quality control

#### topics table - 3 new columns
- `verified_facts` (TEXT) - JSON array of verified facts
- `source_plan` (TEXT) - JSON: planned sources for verification
- `verification_status` (TEXT) - pending, in_progress, verified, partial, failed

**Purpose:** Fact verification workflow tracking

### New Views (5)

1. **approved_event_candidates** - High-priority events ready for article generation
2. **articles_pending_review** - Articles awaiting review with deadline tracking
3. **article_revision_history** - Complete revision history for all articles
4. **published_corrections** - Public corrections for transparency page
5. **source_reliability_trends** - Source credibility trends and statistics

### New Indexes (14)

Performance optimizations for:
- Event candidate queries by status, discovery date, newsworthiness score
- Article revision queries by article, date, type
- Correction queries by article, status, severity
- Source reliability queries by source, date, event type
- Article queries by assigned editor, review deadline, audit status
- Topic queries by verification status

## Files Created

```
database/migrations/
├── 001_automated_journalism_schema.sql    # Migration SQL (SQLite + PostgreSQL compatible)
├── run_migration_001.py                   # Migration execution script
├── test_migration_001.py                  # Migration verification tests
└── MIGRATION_001_SUMMARY.md              # This file
```

## Files Modified

```
database/
├── models.py                              # Added 4 new model classes, extended Article and Topic
└── README.md                              # Updated schema documentation
```

## Migration Execution

```bash
# 1. Run migration
cd /Users/home/sandbox/daily_worker/projects/DWnews
python3 database/migrations/run_migration_001.py

# 2. Verify migration
python3 database/migrations/test_migration_001.py
```

## Test Results

```
✅ All 4 new tables created successfully
✅ All 5 new columns added to articles table
✅ All 3 new columns added to topics table
✅ All 5 new views created successfully
✅ All 14 new indexes created successfully
✅ SQLAlchemy ORM models working correctly
✅ All test inserts successful
```

## Database Compatibility

**SQLite (Local Development):**
- ✅ Fully tested and working
- Uses AUTOINCREMENT, BOOLEAN 0/1, TEXT, REAL
- Triggers for updated_at columns
- Partial indexes with WHERE clauses

**PostgreSQL (Cloud Production):**
- ✅ Compatible with minor syntax changes
- SQL comments include PostgreSQL conversion notes
- Ready for SERIAL PRIMARY KEY, BOOLEAN true/false, JSONB columns
- Supports full-text search and materialized views

## Next Steps

Phase 6.1 is now **COMPLETE**. The database schema is ready for:

1. **Phase 6.2:** Signal Intake Agent (RSS/Twitter/Reddit/Gov feeds)
2. **Phase 6.3:** Evaluation Agent (Newsworthiness scoring)
3. **Phase 6.4:** Verification Agent (Fact checking)
4. **Phase 6.5:** Enhanced Journalist Agent (Article drafting)
5. **Phase 6.6:** Editorial Coordinator (Human review workflow)

## Impact

This migration enables:
- 🤖 Automated event discovery from multiple sources
- 📊 Data-driven newsworthiness scoring
- ✅ Comprehensive fact verification workflow
- 📝 Complete article revision history
- 🔄 Transparent post-publication corrections
- 📈 Continuous learning from source reliability data
- 👥 Human editorial oversight with deadline tracking

## Cost Impact

- **Zero cost increase** - Local SQLite database
- Schema ready for GCP Cloud SQL (PostgreSQL) in later phases
- No cloud costs until Batch 8 (GCP Deployment)

---

**Migration 001: SUCCESSFUL** ✅
**Phase 6.1: COMPLETE** ✅
**Ready for Phase 6.2** ⚪
