# GitHub Actions CI/CD

This directory contains automated workflows for continuous integration and deployment.

## Workflows

### 1. Backend Tests (`backend-tests.yml`)
**Trigger:** Push/PR to main/develop (backend or database changes)

**What it does:**
- Runs all 39 backend API unit tests
- Tests against Python 3.9, 3.10, and 3.11
- Generates code coverage reports
- Uploads coverage to Codecov
- Creates HTML coverage reports as artifacts

**Status:** ![Backend Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/backend-tests.yml/badge.svg)

### 2. Code Quality (`code-quality.yml`)
**Trigger:** Push/PR to main/develop (backend or database changes)

**What it does:**
- Black code formatting check
- isort import sorting check
- Flake8 style guide enforcement
- Pylint code analysis
- Bandit security scanning
- Generates security reports

**Status:** ![Code Quality](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/code-quality.yml/badge.svg)

### 3. CI Pipeline (`ci.yml`)
**Trigger:** Push/PR to main/develop

**What it does:**
- Orchestrates all CI jobs
- Runs backend tests, code quality, security scans
- Validates Python imports and database schema
- Provides comprehensive CI status report

**Status:** ![CI Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)

### 4. Frontend Tests (`frontend-tests.yml`)
**Trigger:** Push/PR to main/develop (frontend changes)

**What it does:**
- Runs 50+ frontend tests (unit, integration, E2E)
- Tests on Node 18.x and 20.x
- Multi-browser E2E tests (Chromium, Firefox, WebKit)
- Linting and formatting checks (ESLint, Prettier)
- Build validation
- Uploads coverage reports

**Status:** ![Frontend Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/frontend-tests.yml/badge.svg)

### 5. Dependency Updates (`dependency-update.yml`)
**Trigger:** Weekly (Mondays at 9 AM UTC) or manual

**What it does:**
- Audits dependencies for security vulnerabilities
- Checks for outdated packages
- Creates GitHub issues for security problems
- Generates audit reports

**Status:** ![Dependency Updates](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/dependency-update.yml/badge.svg)

---

## Deployment Workflows

### 6. Deploy to Staging (`deploy-staging.yml`)
**Trigger:** Push to `develop` branch (automatic) or manual

**What it does:**
- Security checks and secret scanning
- Runs full test suite (99+ tests)
- Builds Docker image and pushes to GCR
- Scans image for vulnerabilities
- Runs database migrations via Cloud SQL Proxy
- Deploys to GCP Cloud Run (staging environment)
- Performs health checks and smoke tests
- Creates failure notification if deployment fails

**Environment:** `dailyworker-staging` (GCP)

**Status:** ![Deploy Staging](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/deploy-staging.yml/badge.svg)

### 7. Deploy to Production (`deploy-production.yml`)
**Trigger:** Manual only (requires "DEPLOY" confirmation)

**What it does:**
- Pre-deployment security validation
- Runs full test suite
- Builds production-optimized Docker image
- Creates database backup before migration
- Runs database migrations
- Deploys new revision to Cloud Run (0% traffic initially)
- Tests new revision thoroughly
- Gradual traffic migration: 10% → 50% → 100%
- Monitors deployment for 5 minutes
- **Automatic rollback** if any step fails
- Post-deployment verification

**Environment:** `dailyworker-production` (GCP)

**Safety Features:**
- ✅ Manual approval required
- ✅ Pre-deployment database backup
- ✅ Zero-downtime blue-green deployment
- ✅ Gradual traffic rollout with monitoring
- ✅ Automatic rollback on failure

**Status:** ![Deploy Production](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/deploy-production.yml/badge.svg)

### 8. Manual Rollback (`manual-rollback.yml`)
**Trigger:** Manual only (emergency rollback)

**What it does:**
- Validates rollback confirmation
- Creates pre-rollback database backup (production)
- Rolls back to previous or specified revision
- Verifies health of rolled-back revision
- Monitors for 2 minutes
- Creates notification issue

**Use cases:**
- Emergency rollback after deployment
- Revert to known-good revision
- Recover from failed deployment

**Status:** ![Manual Rollback](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/manual-rollback.yml/badge.svg)

## Workflow Architecture

### CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    CI Pipeline (ci.yml)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │ Backend Tests  │  │Frontend Tests  │  │Code Quality  │ │
│  │ (3 Python vers)│  │(2 Node vers)   │  │(Lint/Format) │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐                    │
│  │ Security Scan  │  │  Build Check   │                    │
│  │   (Safety)     │  │ (Imports/DB)   │                    │
│  └────────────────┘  └────────────────┘                    │
│                                                              │
│             ┌────────────────┐                              │
│             │  Status Check  │                              │
│             └────────────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Pipeline

```
Git Repository
    │
    ├─── develop branch ──→ Auto Deploy to Staging
    │                        │
    │                        ├─ Security Scan
    │                        ├─ Run Tests (99+)
    │                        ├─ Build Docker Image
    │                        ├─ Migrate Database
    │                        ├─ Deploy to Cloud Run
    │                        └─ Health Checks
    │
    └─── main branch ──→ Manual Deploy to Production
                          (Requires "DEPLOY" confirmation)
                          │
                          ├─ Security Validation
                          ├─ Full Test Suite
                          ├─ Build Prod Image
                          ├─ Database Backup
                          ├─ Migrate Database
                          ├─ Deploy (0% traffic)
                          ├─ Test New Revision
                          ├─ Gradual Rollout:
                          │   • 10% traffic → monitor
                          │   • 50% traffic → monitor
                          │   • 100% traffic → monitor
                          └─ Auto Rollback (on failure)
```

## Configuration

### Python Versions Tested
- Python 3.9 (minimum supported)
- Python 3.10
- Python 3.11 (recommended)

### Caching
- Pip dependencies cached for faster builds
- Cache key based on requirements files

### Artifacts Uploaded
- Coverage reports (HTML)
- Security scan reports (Bandit, Safety)
- Test databases (on failure, for debugging)
- Dependency audit reports

## Required Secrets

Configure these in GitHub Settings > Secrets and variables > Actions:

### CI/CD Secrets

| Secret | Purpose | Required |
|--------|---------|----------|
| `CODECOV_TOKEN` | Upload coverage to Codecov | Optional |

### Deployment Secrets (GCP)

**Staging:**
| Secret | Purpose | Required |
|--------|---------|----------|
| `GCP_STAGING_PROJECT_ID` | GCP project ID | Yes |
| `GCP_STAGING_SA_KEY` | Service account key (JSON) | Yes |
| `GCP_STAGING_SERVICE_ACCOUNT` | App service account email | Yes |
| `GCP_STAGING_DB_CONNECTION` | Cloud SQL connection name | Yes |
| `GCP_STAGING_DB_INSTANCE` | Cloud SQL instance name | Yes |
| `GCP_STAGING_DATABASE_URL` | PostgreSQL connection string | Yes |

**Production:**
| Secret | Purpose | Required |
|--------|---------|----------|
| `GCP_PRODUCTION_PROJECT_ID` | GCP project ID | Yes |
| `GCP_PRODUCTION_SA_KEY` | Service account key (JSON) | Yes |
| `GCP_PRODUCTION_SERVICE_ACCOUNT` | App service account email | Yes |
| `GCP_PRODUCTION_DB_CONNECTION` | Cloud SQL connection name | Yes |
| `GCP_PRODUCTION_DB_INSTANCE` | Cloud SQL instance name | Yes |
| `GCP_PRODUCTION_DATABASE_URL` | PostgreSQL connection string | Yes |

**Setup Instructions:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete setup instructions.

## Branch Protection Rules

Recommended settings for `main` branch:

- ✅ Require status checks to pass before merging
  - `Backend Tests (Python 3.11)`
  - `Build Check`
- ✅ Require pull request reviews before merging
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings

## Local Testing

Before pushing, run locally:

```bash
# Run backend tests
cd projects/DWnews
./backend/tests/run_tests.sh

# Check code formatting
black --check backend/ database/

# Sort imports
isort --check-only backend/ database/

# Run linter
flake8 backend/ database/ --max-line-length=120
```

## Troubleshooting

### Workflow fails on "Install dependencies"
- Check that `backend/requirements.txt` is up to date
- Verify all packages are compatible with Python 3.9+

### Tests pass locally but fail in CI
- Ensure PYTHONPATH is set correctly locally
- Check for platform-specific code (CI runs on Ubuntu)
- Verify database file paths are relative

### Coverage upload fails
- Check that `CODECOV_TOKEN` is set (if using Codecov)
- Coverage upload is non-blocking and won't fail the build

## Monitoring

View workflow runs:
- [Actions tab](https://github.com/YOUR_USERNAME/YOUR_REPO/actions)
- Individual workflow pages
- PR status checks

## Manual Triggers

All workflows can be triggered manually:

1. Go to Actions tab
2. Select workflow
3. Click "Run workflow"
4. Choose branch and click "Run workflow"

## Best Practices

1. **Write tests first** - All new features should have tests
2. **Keep tests fast** - Target < 2 minutes for full suite
3. **Fix failures immediately** - Don't merge with failing tests
4. **Review coverage reports** - Aim for >80% coverage
5. **Update dependencies regularly** - Review weekly audit reports

## Adding New Workflows

To add a new workflow:

1. Create `.github/workflows/your-workflow.yml`
2. Define trigger conditions
3. Add jobs and steps
4. Test with `workflow_dispatch` first
5. Update this README with documentation

## Status Badges

Add to your README.md:

```markdown
[![CI Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml)
[![Backend Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/backend-tests.yml)
[![Frontend Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/frontend-tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/frontend-tests.yml)
[![Deploy Staging](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/deploy-staging.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/deploy-staging.yml)
[![Deploy Production](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/deploy-production.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/deploy-production.yml)
```

## Documentation

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment setup and procedures
- **[GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)** - GitHub Actions configuration guide
- **[WORKFLOWS_SUMMARY.md](WORKFLOWS_SUMMARY.md)** - Detailed workflow specifications

## Support

For issues with GitHub Actions:
- Check [GitHub Actions documentation](https://docs.github.com/en/actions)
- Review workflow logs for detailed errors
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment troubleshooting
- Open an issue in this repository
