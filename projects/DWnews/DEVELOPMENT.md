# The Daily Worker - Local Development Guide

This guide covers local development setup and workflow.

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd daily_worker/projects/DWnews
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required configuration:**
- At least one LLM API key (Claude, OpenAI, or Gemini)
- Database URL (defaults to SQLite)

**Optional configuration:**
- Twitter API (for content discovery)
- Reddit API (for content discovery)
- Image API keys (Gemini, Unsplash, Pexels)

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test configuration
python config.py

# Run backend server
python main.py
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/api/docs
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
# Frontend runs at http://localhost:3000
```

### 5. Database Setup

```bash
cd database

# Initialize database
python init_db.py

# Apply migrations
alembic upgrade head

# Load seed data (news sources)
python seed_data.py
```

## Development Workflow

### Starting Development

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Database (if needed)
cd database
# Run migrations or database scripts
```

### Directory Structure

```
DWnews/
├── backend/              # FastAPI backend
│   ├── main.py          # Main application
│   ├── config.py        # Configuration management
│   ├── logging_config.py # Logging setup
│   └── requirements.txt # Python dependencies
├── frontend/            # Web portal
│   ├── index.html      # Main page
│   ├── styles/         # CSS files
│   ├── scripts/        # JavaScript files
│   └── package.json    # Node dependencies
├── database/           # Database schema and migrations
│   ├── schema.sql      # Database schema
│   ├── migrations/     # Alembic migrations
│   └── seed_data.py    # Seed data script
├── scripts/            # Content generation scripts
│   ├── content/        # Article generation
│   └── utils/          # Utility scripts
├── static/             # Static files
│   └── images/         # Local image storage
├── logs/               # Application logs
└── .env                # Environment variables (not in git)
```

## Common Tasks

### Generate Articles

```bash
cd scripts/content
python discover_topics.py    # Discover topics from RSS/social
python filter_topics.py      # Filter for viability
python generate_articles.py  # Generate articles via LLM
```

### Check Reading Level

```bash
python -c "import textstat; print(textstat.flesch_kincaid_grade('Your article text here'))"
# Target: 7.5-8.5
```

### Run Tests

```bash
cd backend
pytest                       # Run all tests
pytest -v                    # Verbose output
pytest --cov                 # With coverage
```

### View Logs

```bash
tail -f logs/dwnews.log     # Follow logs
cat logs/dwnews.log | jq    # Pretty print JSON logs
```

### Database Operations

```bash
# Create migration
cd database
alembic revision -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View current version
alembic current

# View history
alembic history
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Articles (to be implemented)
```bash
# Get all articles
GET /api/articles

# Get article by ID
GET /api/articles/{id}

# Get articles by region
GET /api/articles?region=national

# Get articles by category
GET /api/articles?category=labor

# Get ongoing stories
GET /api/articles?ongoing=true
```

### Admin (to be implemented)
```bash
# Review pending articles
GET /api/admin/articles/pending

# Approve article
POST /api/admin/articles/{id}/approve

# Reject article
POST /api/admin/articles/{id}/reject
```

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check configuration
python config.py

# Check logs
cat logs/dwnews.log
```

### Database errors

```bash
# Reset database (WARNING: deletes all data)
rm dwnews.db
python database/init_db.py

# Check database file
sqlite3 dwnews.db ".schema"

# Verify migrations
cd database
alembic current
```

### Frontend errors

```bash
# Clear node_modules
rm -rf node_modules
npm install

# Check API connection
curl http://localhost:8000/api/health
```

### LLM API errors

```bash
# Verify API keys in .env
cat .env | grep API_KEY

# Test API connection
python -c "from anthropic import Anthropic; print(Anthropic(api_key='your-key').messages.create(...))"
```

## Code Quality

### Format Code

```bash
# Python
cd backend
black .
flake8

# JavaScript
cd frontend
npm run format
npm run lint
```

### Type Checking

```bash
cd backend
mypy .
```

## Performance Testing

### Load Testing (Local)

```bash
# Install Apache Bench
# macOS: brew install ab
# Ubuntu: apt-get install apache2-utils

# Test API endpoint
ab -n 1000 -c 10 http://localhost:8000/api/health
```

## Security

### Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Add to .env as SECRET_KEY
```

### Scan Dependencies

```bash
# Python
pip install safety
safety check

# Node.js
npm audit
npm audit fix
```

## Useful Commands

```bash
# Check service status
curl http://localhost:8000/api/health     # Backend
curl http://localhost:3000                 # Frontend

# View database
sqlite3 dwnews.db
> .tables
> SELECT * FROM articles LIMIT 5;
> .exit

# Monitor logs in real-time
tail -f logs/dwnews.log | jq -C .

# Count articles
sqlite3 dwnews.db "SELECT COUNT(*) FROM articles;"

# Check image storage
ls -lh static/images/
```

## Environment Variables Reference

See `.env.example` for complete list of environment variables and their descriptions.

## Next Steps

1. Complete Phase 1.1: Database schema implementation
2. Implement content discovery (Phase 2.1)
3. Implement viability filtering (Phase 2.2)
4. Implement article generation (Phase 2.3)

## Need Help?

- Check logs: `logs/dwnews.log`
- Review requirements: `plans/requirements.md`
- Check roadmap: `plans/roadmap.md`
- API docs: http://localhost:8000/api/docs (when backend is running)
