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

### 4. Dependency Updates (`dependency-update.yml`)
**Trigger:** Weekly (Mondays at 9 AM UTC) or manual

**What it does:**
- Audits dependencies for security vulnerabilities
- Checks for outdated packages
- Creates GitHub issues for security problems
- Generates audit reports

**Status:** ![Dependency Updates](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/dependency-update.yml/badge.svg)

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CI Pipeline (ci.yml)                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐  ┌────────────────┐               │
│  │ Backend Tests  │  │ Code Quality   │               │
│  │ (3 Python vers)│  │ (Lint/Format)  │               │
│  └────────────────┘  └────────────────┘               │
│                                                          │
│  ┌────────────────┐  ┌────────────────┐               │
│  │ Security Scan  │  │  Build Check   │               │
│  │   (Safety)     │  │ (Imports/DB)   │               │
│  └────────────────┘  └────────────────┘               │
│                                                          │
│             ┌────────────────┐                          │
│             │  Status Check  │                          │
│             └────────────────┘                          │
└─────────────────────────────────────────────────────────┘
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

| Secret | Purpose | Required |
|--------|---------|----------|
| `CODECOV_TOKEN` | Upload coverage to Codecov | Optional |

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
[![Backend Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/backend-tests.yml)
[![Code Quality](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/code-quality.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/code-quality.yml)
[![CI Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml)
```

## Support

For issues with GitHub Actions:
- Check [GitHub Actions documentation](https://docs.github.com/en/actions)
- Review workflow logs for detailed errors
- Open an issue in this repository
