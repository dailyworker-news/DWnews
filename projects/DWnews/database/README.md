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

**article_sources** - Many-to-many relationship between articles and sources
- Citation URLs and text
- Supports multi-source verification

**topics** - Content discovery pipeline
- Discovered topics from RSS/social media
- Viability scoring
- Status tracking: discovered → filtered → approved/rejected → generated

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

## Database Migrations (Future)

This project will use Alembic for database migrations when moving to production.

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
