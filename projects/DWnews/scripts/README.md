# Content Generation Scripts

This directory contains scripts for automated content generation.

## Quick Start

### Option 1: Run Full Pipeline (Recommended)

```bash
cd scripts/content
python run_pipeline.py --max-articles 10
```

This runs all four phases:
1. Topic discovery (RSS + social media)
2. Viability filtering
3. Article generation (LLM)
4. Image sourcing

### Option 2: Run Individual Phases

```bash
# 1. Discover topics
python discover_topics.py

# 2. Filter for viability
python filter_topics.py

# 3. Generate articles
python generate_articles.py

# 4. Source images
python source_images.py
```

## Scripts

### Content Pipeline

**run_pipeline.py** - Master script that runs full pipeline
```bash
python run_pipeline.py [options]

Options:
  --max-topics N         Max topics to discover (default: 50)
  --max-articles N       Max articles to generate (default: 10)
  --skip-discovery       Skip topic discovery phase
  --skip-filtering       Skip filtering phase
  --skip-generation      Skip article generation
  --skip-images          Skip image sourcing
  --quiet                Reduce output verbosity
```

### Discovery

**discover_topics.py** - Unified topic discovery (RSS + social media)
- Discovers topics from all configured sources
- Saves to database with status='discovered'

**rss_discovery.py** - RSS feed discovery only
- Fetches from credible news sources
- Auto-categorizes topics

**social_discovery.py** - Social media discovery only
- Twitter/X trending topics
- Reddit hot posts from relevant subreddits

### Filtering

**filter_topics.py** - Viability filtering
- Credibility check (≥3 sources or ≥2 academic)
- Worker relevance scoring
- Engagement potential
- Updates status to 'filtered' or 'rejected'

### Generation

**generate_articles.py** - LLM article generation
- Generates articles from filtered topics
- Uses Claude, OpenAI, or Gemini
- Checks reading level (target: 7.5-8.5)
- Creates drafts for human review

### Images

**source_images.py** - Image sourcing
- Searches Unsplash/Pexels for relevant images
- Downloads and optimizes
- Saves to local storage
- Adds attribution

## Utilities

**text_utils.py** - Text processing helpers
- Keyword extraction
- Similarity detection
- Deduplication
- Category classification

## Workflow

```
1. DISCOVERY
   RSS Feeds + Social Media → Topics (status: discovered)
   ↓

2. FILTERING
   Viability Checks → Topics (status: filtered or rejected)
   ↓

3. GENERATION
   LLM APIs → Articles (status: draft)
   ↓

4. IMAGES
   Image APIs → Articles with images (status: draft)
   ↓

5. HUMAN REVIEW (Admin Dashboard)
   Review & Approve → Articles (status: published)
```

## Requirements

### Required
- Python 3.9+
- Database initialized (run database/init_db.py)
- Seed data loaded (run database/seed_data.py)

### API Keys (at least one LLM required)
```env
# LLM APIs (need at least one)
CLAUDE_API_KEY=your_key
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key

# Social Media (optional, for discovery)
TWITTER_BEARER_TOKEN=your_token
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret

# Images (optional, for sourcing)
UNSPLASH_ACCESS_KEY=your_key
PEXELS_API_KEY=your_key
```

## Example Usage

### Generate 5 articles with full pipeline
```bash
python run_pipeline.py --max-articles 5
```

### Re-run generation only (if topics already filtered)
```bash
python run_pipeline.py --skip-discovery --skip-filtering --max-articles 10
```

### Discovery only (to build up topic queue)
```bash
python discover_topics.py
```

### Check what needs filtering
```bash
python -c "
from database.models import Topic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///dwnews.db')
Session = sessionmaker(bind=engine)
session = Session()

discovered = session.query(Topic).filter_by(status='discovered').count()
filtered = session.query(Topic).filter_by(status='filtered').count()
rejected = session.query(Topic).filter_by(status='rejected').count()

print(f'Discovered (pending): {discovered}')
print(f'Filtered (ready): {filtered}')
print(f'Rejected: {rejected}')
"
```

## Output

Articles are saved to the database with:
- `status='draft'` - Needs human review
- Reading level checked (7.5-8.5 target)
- Word count tracked
- Images attached (if sourced)

## Troubleshooting

### No topics discovered
- Check RSS feeds are accessible
- Verify social media API credentials
- Check internet connection

### No topics pass filtering
- Review filter criteria in filter_topics.py
- Adjust worker_relevance thresholds
- Run discovery with more diverse sources

### Article generation fails
- Verify LLM API key is valid
- Check API quota/rate limits
- Ensure filtered topics exist

### Image sourcing fails
- Configure Unsplash or Pexels API keys
- Check internet connection
- Verify storage directory exists

## Logs

Logs are written to:
- Console (formatted for readability)
- `logs/dwnews.log` (JSON format)

Check logs for detailed error information.

## Cost Tracking

- **RSS/Reddit**: Free
- **Twitter API v2**: Free tier (500K tweets/month)
- **LLM APIs**: Varies by provider (usage-based)
- **Unsplash/Pexels**: Free with attribution
- **Storage**: Local (free)

Estimate: $0-$50/month depending on article volume and LLM choice.
