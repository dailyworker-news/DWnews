# The Daily Worker - AI-Powered Working-Class News Platform

An AI-powered news platform delivering accurate, worker-centric news through a Marxist/Leninist lens. Quality over quantity, no punches pulled.

**Current Status:** ✅ Batch 4 Complete - Ready for Testing & Production Prep

## Project Overview

**Mission:** Deliver accurate, timely news that matters to working-class Americans, with analysis that doesn't shy away from uncomfortable truths.

**Core Features:**
- 3-10 quality articles daily (scales with readership)
- Broad category coverage across 9 categories
- NEW vs ONGOING story prominence with event-based homepage
- Regional content (National + Local based on user location)
- Mobile-first responsive design
- Worker-centric perspective on all news
- Complete admin dashboard for article review
- Social sharing integration

## Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd daily_worker/projects/DWnews

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Initialize database
python database/init_db.py
python database/seed_data.py

# 5. Generate sample articles (optional)
python scripts/generate_sample_content.py

# 6. Start backend
cd backend
uvicorn main:app --reload
# Backend runs at http://localhost:8000

# 7. Open frontend
# In another terminal, open frontend/index.html in your browser
# Or use a simple HTTP server:
python -m http.server 8080 --directory frontend
# Frontend runs at http://localhost:8080
```

## Development Status

### ✅ Completed Batches (4/7)

#### Batch 1: Local Development Setup
- ✅ Version control with Git
- ✅ FastAPI backend with comprehensive configuration
- ✅ SQLite database with complete schema
- ✅ SQLAlchemy ORM models
- ✅ Seed data with 15 credible sources
- ✅ Development documentation

#### Batch 2: Local Content Pipeline
- ✅ RSS feed discovery (15 sources)
- ✅ Social media discovery (Twitter, Reddit)
- ✅ Multi-criteria topic filtering
- ✅ LLM article generation (Claude, OpenAI, Gemini support)
- ✅ Image sourcing (Unsplash, Pexels)
- ✅ Master content pipeline script

#### Batch 3: Local Web Portal
- ✅ Admin dashboard for article review
- ✅ Event-based homepage (ongoing + latest sections)
- ✅ Dedicated article detail pages
- ✅ URL state management for filters
- ✅ Social sharing buttons (6 platforms)
- ✅ Mobile-responsive design

#### Batch 4: Local Testing & Validation
- ✅ End-to-end testing suite
- ✅ API endpoint tests
- ✅ Security review and scanning
- ✅ Sample content generation
- ✅ Documentation updates

### 🔲 Upcoming Batches (3/7)

#### Batch 5: GCP Infrastructure (Planned)
- Cloud Run deployment
- Cloud SQL (PostgreSQL)
- Cloud Storage for images
- Secret Manager
- Cloud Scheduler for automation

#### Batch 6: Production Readiness (Planned)
- CI/CD pipeline
- Monitoring and alerting
- Performance optimization
- Security hardening
- OAuth2 authentication

#### Batch 7: Launch (Planned)
- Domain and SSL setup
- CDN configuration
- Soft launch validation
- Production monitoring
- Go-live

## Project Structure

```
daily_worker/
├── projects/DWnews/
│   ├── backend/                     # FastAPI backend
│   │   ├── main.py                  # Application entry point
│   │   ├── config.py                # Configuration management
│   │   ├── auth.py                  # Authentication (Basic Auth)
│   │   ├── database.py              # Database session management
│   │   └── routes/
│   │       └── articles.py          # Article API endpoints
│   │
│   ├── frontend/                    # Static frontend
│   │   ├── index.html               # Homepage
│   │   ├── article.html             # Article detail page
│   │   ├── styles/
│   │   │   ├── main.css             # Homepage styles
│   │   │   └── article.css          # Article page styles
│   │   ├── scripts/
│   │   │   ├── main.js              # Homepage logic
│   │   │   └── article.js           # Article page logic
│   │   └── admin/
│   │       ├── index.html           # Admin dashboard
│   │       ├── admin.css            # Admin styles
│   │       └── admin.js             # Admin logic
│   │
│   ├── database/                    # Database layer
│   │   ├── schema.sql               # Database schema
│   │   ├── models.py                # SQLAlchemy models
│   │   ├── init_db.py               # Database initialization
│   │   ├── seed_data.py             # Seed data loader
│   │   └── test_data.py             # Test data generator
│   │
│   ├── scripts/                     # Content generation scripts
│   │   ├── content/
│   │   │   ├── rss_discovery.py     # RSS feed aggregation
│   │   │   ├── social_discovery.py  # Twitter/Reddit discovery
│   │   │   ├── filter_topics.py     # Multi-criteria filtering
│   │   │   ├── generate_articles.py # LLM article generation
│   │   │   ├── source_images.py     # Image sourcing/optimization
│   │   │   └── run_pipeline.py      # Master pipeline runner
│   │   ├── utils/
│   │   │   └── text_utils.py        # Text processing utilities
│   │   ├── generate_sample_content.py # Sample article generator
│   │   └── security_scan.sh         # Security scanner
│   │
│   ├── tests/                       # Test suite
│   │   ├── test_database/           # Database model tests
│   │   ├── test_backend/            # Backend tests
│   │   ├── test_scripts/            # Script tests
│   │   ├── test_integration/        # Integration tests
│   │   ├── test_e2e/                # End-to-end tests
│   │   └── run_e2e_tests.sh         # Test runner
│   │
│   ├── plans/                       # Planning documents
│   │   ├── requirements.md          # Product requirements
│   │   ├── roadmap.md               # Development roadmap
│   │   └── priorities.md            # Feature priorities
│   │
│   ├── SECURITY.md                  # Security review document
│   ├── DEVLOG.md                    # Development log
│   ├── DEVELOPMENT.md               # Development guide
│   └── .env.example                 # Environment template
│
├── agent-chat/                      # Agent coordination system
└── CLAUDE.md                        # Agent instructions
```

## Environment Configuration

Create `.env` file in `projects/DWnews/`:

```env
# Environment
ENVIRONMENT=local
DEBUG=true

# Database
DATABASE_URL=sqlite:///./dwnews.db

# Admin Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=<bcrypt_hash>

# LLM APIs (optional, use existing subscriptions)
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# Social Media APIs (optional, for content discovery)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=DailyWorker/1.0

# Image APIs (optional, for article images)
UNSPLASH_ACCESS_KEY=your_unsplash_key
PEXELS_API_KEY=your_pexels_key

# Content Settings
MIN_READING_LEVEL=7.5
MAX_READING_LEVEL=8.5
MIN_CREDIBLE_SOURCES=3
MIN_ACADEMIC_CITATIONS=2
MIN_ENGAGEMENT_SCORE=0.3
MIN_WORKER_RELEVANCE=0.3
```

## Available Scripts

### Database Management
```bash
# Initialize database
python database/init_db.py

# Load seed data (15 sources, 9 categories, 7 regions)
python database/seed_data.py

# Generate test articles
python database/test_data.py

# Generate sample articles (for demo)
python scripts/generate_sample_content.py
```

### Content Pipeline
```bash
# Run complete pipeline (discovery → filtering → generation → images)
python scripts/content/run_pipeline.py

# Or run individual steps:
python scripts/content/rss_discovery.py           # RSS discovery
python scripts/content/social_discovery.py        # Social media discovery
python scripts/content/filter_topics.py           # Filter topics
python scripts/content/generate_articles.py       # Generate articles
python scripts/content/source_images.py           # Source images
```

### Testing
```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/test_database/           # Database tests
pytest tests/test_backend/            # Backend tests
pytest tests/test_e2e/                # End-to-end tests

# Run complete test suite with reporting
./tests/run_e2e_tests.sh
```

### Security
```bash
# Run security scan
./scripts/security_scan.sh

# Check for hardcoded secrets, SQL injection risks, XSS vulnerabilities
```

### Backend Server
```bash
# Development server (with auto-reload)
cd backend
uvicorn main:app --reload

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Public Endpoints
- `GET /api/health` - Health check
- `GET /api/articles/` - List published articles
  - Query params: `status`, `category`, `region`, `ongoing`, `limit`, `offset`
- `GET /api/articles/{id}` - Get single article

### Admin Endpoints (Requires Basic Auth)
- `PATCH /api/articles/{id}` - Update article (publish, archive, mark ongoing)

## Admin Dashboard

Access the admin dashboard at `frontend/admin/index.html`:

**Features:**
- Review pending articles (draft status)
- Preview full article content
- Approve and publish articles
- Mark articles as ongoing stories
- Archive outdated articles
- View statistics (today's articles, this week, avg reading level)

**Default Credentials:**
- Username: `admin`
- Password: Set in `.env` as `ADMIN_PASSWORD_HASH`

## Content Generation Workflow

1. **Discovery** - Find potential topics from RSS feeds and social media
2. **Filtering** - Apply multi-criteria viability checks:
   - Source credibility (≥3 sources)
   - Worker relevance (≥0.3 score)
   - Engagement potential (≥0.3 score)
3. **Generation** - Use LLM to generate article with:
   - Worker-centric perspective
   - Reading level 7.5-8.5 (Flesch-Kincaid)
   - "Why This Matters" section
   - "What You Can Do" action section
4. **Review** - Admin reviews and approves in dashboard
5. **Publish** - Article appears on homepage

## Testing Locally

### Manual Testing Checklist
- [ ] Backend starts without errors
- [ ] Homepage loads and displays articles
- [ ] Ongoing stories section appears when articles marked ongoing
- [ ] Latest stories section shows recent articles
- [ ] Category filtering works
- [ ] Region filtering works (national/local/all)
- [ ] Pagination works (previous/next buttons)
- [ ] Article pages display full content
- [ ] Share buttons work (Twitter, Facebook, LinkedIn, Reddit, Email, Copy)
- [ ] Admin dashboard loads
- [ ] Admin can approve articles (draft → published)
- [ ] Admin can mark articles as ongoing
- [ ] Admin can archive articles
- [ ] Mobile responsive design works

### Automated Testing
```bash
# Run all tests
./tests/run_e2e_tests.sh

# Expected output:
# ✓ 80+ unit tests passing
# ✓ 25+ integration tests passing
# ✓ 25+ end-to-end tests passing
# ✓ Backend server operational
# ✓ API endpoints functional
```

## Security

See [SECURITY.md](projects/DWnews/SECURITY.md) for complete security review.

**Current Status:** ✅ Secure for Local Development

**Security Controls:**
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS prevention (content escaping)
- ✅ Secrets management (environment variables)
- ✅ CORS restricted to localhost
- ⚠️  Basic Auth (upgrade to OAuth2 for production)

**Production Requirements:**
- OAuth2 or JWT authentication
- Rate limiting
- HTTPS enforcement
- Security headers (CSP, HSTS)
- Web Application Firewall
- Audit logging

## Troubleshooting

### Database Issues
```bash
# Reset database
rm dwnews.db
python database/init_db.py
python database/seed_data.py
```

### Port Already in Use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn main:app --port 8001
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Frontend Not Loading
```bash
# Use a simple HTTP server
cd frontend
python -m http.server 8080

# Or open directly in browser
open index.html  # macOS
start index.html  # Windows
xdg-open index.html  # Linux
```

## Documentation

- [Requirements](projects/DWnews/plans/requirements.md) - Complete product specification
- [Roadmap](projects/DWnews/plans/roadmap.md) - Development roadmap
- [Security Review](projects/DWnews/SECURITY.md) - Security assessment
- [Development Log](projects/DWnews/DEVLOG.md) - Complete development history
- [Development Guide](projects/DWnews/DEVELOPMENT.md) - Developer workflows

## Key Design Principles

1. **Local-First:** Build and validate locally before cloud costs
2. **Quality Over Quantity:** 3-10 quality articles > 50 mediocre ones
3. **Agent-Driven:** AI agents are autonomous developers
4. **Worker-Centric:** All news through a working-class lens
5. **No Punches Pulled:** Accurate, truthful, uncompromising
6. **Event-Based Layout:** Ongoing stories get prominence over chronological

## Cost Structure

- **Local Development (Batches 1-4):** $0 ✅
- **Content Generation:** $0.50-2.00 per run (LLM costs)
- **Production Deployment:** TBD (Batch 5-7)
- **Target Monthly OpEx:** <$100/month

## What's Next?

**Immediate:** Phase 4.5 - Create legal pages (About, Privacy, Terms)
**Next Batch:** Batch 5 - GCP infrastructure setup and cloud deployment

## Contributing

This is an agent-driven project. Human contributions welcome:

1. Review agent-generated content
2. Provide feedback on UX/UI
3. Report bugs and issues
4. Suggest feature improvements
5. Test the application

## License

TBD

---

**Version:** 4.0 (Batch 4 Complete)
**Last Updated:** 2025-12-29
**Status:** ✅ Local development complete, ready for production prep
**Next Milestone:** Legal pages and cloud deployment planning
