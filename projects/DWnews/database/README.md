# Database Setup

This directory contains database schema, models, and initialization scripts.

## Quick Start

```bash
# 1. Initialize database
python init_db.py

# 2. Seed with credible sources and categories
python seed_data.py

# 3. Generate test articles
python test_data.py
```

## Files

- `schema.sql` - Raw SQL schema definition
- `models.py` - SQLAlchemy ORM models
- `init_db.py` - Database initialization script
- `seed_data.py` - Seeds credible sources, categories, regions
- `test_data.py` - Generates test articles for development

## Database Schema

### Tables

**sources** - Credible news sources
- 15 sources including AP, Reuters, ProPublica, Labor Notes
- Credibility scores (1-5)
- Source types: news_wire, investigative, academic, local, social
- Political lean tracking

**categories** - Article categories
- Labor, Tech, Politics, Economics, Current Affairs, Art & Culture, Sport, Good News, Environment

**regions** - Geographic regions
- National, state-level, metro areas
- Population data for prioritization

**articles** - Published and draft articles
- Full article content with metadata
- Regional flags (national/local)
- Story type flags (ongoing/new)
- Reading level tracking (target: 7.5-8.5)
- Status workflow: draft → pending_review → approved → published
- NEW: Automated journalism columns (bias_scan_report, self_audit_passed, editorial_notes, assigned_editor, review_deadline)

**article_sources** - Many-to-many relationship between articles and sources
- Citation URLs and text
- Supports multi-source verification

**topics** - Content discovery pipeline
- Discovered topics from RSS/social media
- Viability scoring
- Status tracking: discovered → filtered → approved/rejected → generated
- NEW: Verification workflow columns (verified_facts, source_plan, verification_status)

**event_candidates** - Automated journalism event discovery (NEW in Migration 001)
- Events discovered by Signal Intake Agent
- Newsworthiness scoring (worker_impact, timeliness, verifiability, regional_relevance)
- Status tracking: discovered → evaluated → approved/rejected → converted
- Links to topics and articles when converted

**article_revisions** - Article revision history (NEW in Migration 001)
- Tracks all changes to articles
- Revision types: draft, ai_edit, human_edit, fact_check, bias_correction, copy_edit
- Before/after snapshots of title, body, summary
- Verification status tracking

**corrections** - Post-publication corrections (NEW in Migration 001)
- Transparent correction tracking
- Correction types: factual_error, source_error, clarification, update, retraction
- Severity levels: minor, moderate, major, critical
- Public notice management

**source_reliability_log** - Source credibility learning loop (NEW in Migration 001)
- Tracks credibility score changes over time
- Event types: article_published, correction_issued, fact_check_pass/fail, retraction
- Automated and manual adjustments
- Supports continuous learning from corrections

### Indexes

Optimized indexes for:
- Published articles by date
- Regional filtering (national/local)
- Story type filtering (ongoing/new)
- Category browsing
- Topic discovery workflow

### Views

- `published_articles` - Denormalized view of published content
- `article_source_count` - Articles with source count
- `approved_event_candidates` - High-priority events ready for article generation (NEW)
- `articles_pending_review` - Articles awaiting editorial review with deadline tracking (NEW)
- `article_revision_history` - Complete revision history for all articles (NEW)
- `published_corrections` - Public-facing corrections for transparency page (NEW)
- `source_reliability_trends` - Source credibility trends over time (NEW)

## Usage Examples

### Query Published Articles

```python
from database.models import Article
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///dwnews.db")
Session = sessionmaker(bind=engine)
session = Session()

# Get all published articles
articles = session.query(Article).filter_by(status='published').all()

# Get national articles
national = session.query(Article).filter_by(
    status='published',
    is_national=True
).order_by(Article.published_at.desc()).all()

# Get ongoing stories
ongoing = session.query(Article).filter_by(
    status='published',
    is_ongoing=True
).all()
```

### Add a New Article

```python
from database.models import Article, Category
from datetime import datetime

# Find category
category = session.query(Category).filter_by(slug='labor').first()

# Create article
article = Article(
    title="New Labor Victory",
    slug="new-labor-victory",
    body="Article content here...",
    category_id=category.id,
    is_national=True,
    reading_level=8.0,
    status='draft'
)

session.add(article)
session.commit()
```

## Database Migrations

This project uses custom migration scripts compatible with both SQLite and PostgreSQL.

### Running Migrations

```bash
# Run a specific migration
python3 database/migrations/run_migration_001.py

# Test migration was successful
python3 database/migrations/test_migration_001.py
```

### Migration History

**Migration 001: Automated Journalism Pipeline** (2026-01-01)
- Added `event_candidates` table for automated event discovery
- Added `article_revisions` table for revision tracking
- Added `corrections` table for post-publication corrections
- Added `source_reliability_log` table for source credibility learning
- Extended `articles` table with automated journalism columns
- Extended `topics` table with verification workflow columns
- Created 5 new views for common queries

### Future: Alembic Integration

For production deployment, the project may migrate to Alembic:

```bash
# Initialize Alembic (future)
alembic init migrations

# Create migration
alembic revision -m "description"

# Apply migrations
alembic upgrade head
```

## Switching from SQLite to PostgreSQL

For production deployment, update `.env`:

```env
# Change from:
DATABASE_URL=sqlite:///./dwnews.db

# To:
DATABASE_URL=postgresql://username:password@localhost:5432/dwnews
```

Then run migrations:
```bash
python init_db.py
python seed_data.py
```

## Notes

- SQLite is recommended for local development
- PostgreSQL recommended for production
- All timestamps are in UTC
- Reading level target: 7.5-8.5 (8th grade)
- Minimum 3 credible sources per article (or 2 academic citations)
