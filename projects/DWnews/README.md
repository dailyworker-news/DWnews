# DWnews - The Daily Worker

Daily Worker newspaper publishes worker-relevant news impacting local, national and international issues. Supporting a scientific and materialist assessment and reflection of labor issues, technology, politics, economics, current affairs, art and sport.

## Project Status

**Current Phase:** Testing and Security Configuration (Pre-Deployment)

### Completed
- ✅ Local development environment with complete MVP functionality
- ✅ Automated journalism pipeline (6 AI agents)
- ✅ Testing infrastructure (99+ automated tests)
- ✅ CI/CD pipeline (8 GitHub Actions workflows)
- ✅ Deployment automation (staging, production, rollback workflows)
- ✅ Traditional newspaper design (v3.0)

### In Progress
- 🔄 Local functional and end-user testing
- 🔄 Security configuration for production deployment
- 🔄 GCP infrastructure setup (different root account)

### Deployment Status: ON HOLD
The deployment pipeline is complete and ready, but deployment is **intentionally paused** until:
1. Complete local testing (functional + end-user)
2. Security configuration implemented (see `plans/CLOUD_SECURITY_CONFIG.md`)
3. New GCP project set up with different root account
4. All security prerequisites verified

**No rush to production** - Quality and security are the priority.

## Key Documentation

- **Roadmap:** `/plans/roadmap.md` - Development progress and deployment plan
- **Requirements:** `/plans/requirements.md` - Complete technical specifications
- **Security:** `/plans/CLOUD_SECURITY_CONFIG.md` - Security requirements (MUST complete before production)
- **Priorities:** `/plans/priorities.md` - Strategic priorities and business goals

## Technology Stack

**Backend:**
- Python 3.11+ with FastAPI
- PostgreSQL database
- 6 AI agents (Signal Intake, Evaluation, Verification, Journalist, Editorial Coordinator, Monitoring)

**Frontend:**
- Traditional newspaper design (Playfair Display + Merriweather)
- Responsive web design (mobile-first)
- Black/white/yellow color scheme

**Testing & CI/CD:**
- 99+ automated tests (backend + frontend + E2E)
- Multi-version testing (Python 3.9-3.11, Node 18.x-20.x)
- Multi-browser E2E (Chromium, Firefox, WebKit)
- 8 GitHub Actions workflows

**Deployment (Ready, Not Active):**
- GCP Cloud Run (serverless)
- Cloud SQL (PostgreSQL with private IP)
- Cloud Storage + CDN
- GitHub Actions for CI/CD

## Local Development

See individual component READMEs for setup instructions:
- Backend: `/backend/README.md`
- Frontend: `/frontend/README.md`
- Testing: `/tests/README.md`
- Scripts: `/scripts/README.md`

## Philosophy

**Marxist/Leninist influenced** - Accurate, worker-centric news that doesn't pull punches

**Local-First Development** - Prove utility locally before cloud costs

**Security-First Deployment** - Production only after complete security configuration

**Quality Over Quantity** - Satisfactory utility, not metrics-driven growth
