# The Daily Worker - AI-Powered Working-Class News Platform

An AI-powered news platform delivering accurate, worker-centric news through a Marxist/Leninist lens. Quality over quantity, no punches pulled.

## Project Overview

**Mission:** Deliver accurate, timely news that matters to working-class Americans, with analysis that doesn't shy away from uncomfortable truths.

**Core Features:**
- 3-10 quality articles daily (scales with readership)
- Broad category coverage across 9 categories
- NEW vs ONGOING story prominence
- Regional content (National + Local based on user location)
- Mobile-first responsive design
- Worker-centric perspective on all news

## Development Approach

This project uses a **local-first development model**:
1. Build and validate everything locally (Batches 1-4) - **Zero cost**
2. Deploy to GCP only after complete validation (Batches 5-7)
3. Agent-driven development using AI agents as autonomous developers

## Local Setup Instructions

### Prerequisites

- **Python 3.9+** or **Node.js 16+** (depending on implementation choice)
- **PostgreSQL** (local) or **SQLite**
- **Git**
- **Docker** (optional, for NATS Jetstream agent chat system)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd daily_worker
```

### Step 2: Set Up Agent Chat System (Optional)

The agent chat system enables coordination between AI agents working on the project.

```bash
cd agent-chat

# Start NATS Jetstream
docker-compose up -d

# Verify NATS is running
docker ps | grep nats

# Install dependencies
npm install

# Start the dashboard (optional, for monitoring)
npm run dashboard
# Opens at http://localhost:3000
```

### Step 3: Set Up Development Environment

```bash
cd projects/DWnews

# Python setup (if using Python backend)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# OR Node.js setup (if using Node backend)
npm install
```

### Step 4: Configure Environment Variables

Create a `.env` file in `projects/DWnews/`:

```env
# Database
DATABASE_URL=postgresql://localhost/dwnews  # or sqlite:///./dwnews.db

# LLM APIs (use your existing subscriptions)
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# Social Media APIs (free tiers)
TWITTER_API_KEY=your_twitter_api_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Local settings
ENVIRONMENT=local
DEBUG=true
```

### Step 5: Initialize Database

```bash
# Run database migrations
python manage.py migrate  # Django example
# OR
npm run db:migrate  # Node example

# Load seed data (credible news sources)
python manage.py seed  # or equivalent command
```

### Step 6: Run the Application

```bash
# Backend API
python manage.py runserver  # or npm start
# Runs at http://localhost:8000

# Frontend (if separate)
cd frontend
npm run dev
# Runs at http://localhost:3000
```

### Step 7: Access Admin Dashboard

Navigate to `http://localhost:8000/admin` (or configured admin route)

- Default credentials will be set during initial setup
- Use admin dashboard to review and approve AI-generated articles

## Project Structure

```
daily_worker/
├── .claude/
│   ├── mcp.json                    # MCP server configuration
│   └── agents/                     # Custom agent definitions
├── agent-chat/                     # Inter-agent communication system
│   ├── index.js                    # MCP server
│   ├── dashboard.js                # Web dashboard
│   └── docker-compose.yml          # NATS infrastructure
├── projects/
│   └── DWnews/
│       ├── plans/                  # Requirements and roadmap
│       ├── backend/                # API server (TBD)
│       ├── frontend/               # Web portal (TBD)
│       ├── database/               # Schema and migrations (TBD)
│       └── scripts/                # Content generation scripts (TBD)
└── README.md
```

## Development Workflow

### Content Generation Workflow

1. **Discovery:** Run content discovery script to find topics
   ```bash
   python scripts/discover_topics.py
   ```

2. **Filtering:** Topics automatically filtered for viability
   - ≥3 credible sources OR ≥2 academic citations
   - Direct impact on working-class Americans
   - Evidence of social interest

3. **Generation:** Generate articles using LLM
   ```bash
   python scripts/generate_articles.py
   ```

4. **Review:** Human reviews articles in admin dashboard
   - Preview formatting
   - Approve or reject
   - Edit if needed

5. **Publish:** Approved articles appear on homepage

### Branching Strategy

- `main` - Production-ready code (after GCP deployment)
- `development` - Active development branch
- Feature branches: `feature/phase-X.Y-description`

```bash
# Create a feature branch
git checkout -b feature/phase-1.1-database-setup

# Make changes, commit
git add .
git commit -m "Phase 1.1: Database schema design"

# Merge to development
git checkout development
git merge feature/phase-1.1-database-setup

# Delete feature branch
git branch -d feature/phase-1.1-database-setup
```

## Testing Locally

### Run Tests

```bash
# Backend tests
pytest  # Python
# or
npm test  # Node

# End-to-end testing
python scripts/test_e2e.py
```

### Manual Testing Checklist

- [ ] Content discovery finds diverse topics
- [ ] Viability filtering works correctly
- [ ] Articles generate at 7.5-8.5 reading level (Flesch-Kincaid)
- [ ] Admin dashboard displays articles
- [ ] Homepage shows NEW and ONGOING stories correctly
- [ ] Regional filtering works (national + local)
- [ ] All 9 categories represented
- [ ] Mobile responsive design
- [ ] Share buttons functional

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Reset database
dropdb dwnews
createdb dwnews
python manage.py migrate
```

### NATS Connection Issues

```bash
# Check NATS is running
docker ps | grep nats

# Restart NATS
cd agent-chat
docker-compose restart

# Check NATS logs
docker logs agent-chat-nats-1
```

### Module Not Found Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt  # Python
# or
npm install  # Node
```

## Agent Chat System

The agent chat system enables AI agents to coordinate work:

- `#roadmap` - Roadmap updates and project direction
- `#coordination` - Work coordination and status updates
- `#errors` - Error reports

Agents announce their work to avoid conflicts:

```javascript
set_handle({ handle: "backend-dev-01" })
publish_message({
  channel: "coordination",
  message: "Starting Phase 1.1 - Database Schema. ETA: 30 mins"
})
```

View agent communications at http://localhost:3000 (dashboard)

## Documentation

- [Requirements](projects/DWnews/plans/requirements.md) - Complete product specification
- [Roadmap](projects/DWnews/plans/roadmap.md) - Active work tracking
- [Priorities](projects/DWnews/plans/priorities.md) - Feature prioritization
- [CLAUDE.md](CLAUDE.md) - Agent instructions

## Key Design Principles

1. **Local-First:** Build and validate locally before cloud costs
2. **Quality Over Quantity:** 3-10 quality articles > 50 mediocre ones
3. **Agent-Driven:** AI agents are autonomous developers
4. **Worker-Centric:** All news through a working-class lens
5. **No Punches Pulled:** Accurate, truthful, uncompromising

## Cost Structure

- **Local Development (Batches 1-4):** $0
- **GCP Deployment (Batches 5-7):** Costs reported when deployment begins
- **Target Monthly OpEx:** <$100/month

## Contributing

This is an agent-driven project. Human contributions welcome:

1. Review agent-generated content
2. Provide feedback on UX
3. Report bugs
4. Suggest feature improvements

## License

TBD

## Contact

TBD

---

**Version:** 2.0 (Local-First)
**Last Updated:** 2025-12-29
**Status:** Batch 1 - Local Development Setup
