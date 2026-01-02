# GitHub Actions Setup Guide

Complete guide to setting up automated testing for The Daily Worker project.

## Quick Start

1. **Push to GitHub**
   ```bash
   git add .github/
   git commit -m "feat: Add GitHub Actions CI/CD workflows"
   git push origin main
   ```

2. **Verify Workflows**
   - Go to your repository on GitHub
   - Click the "Actions" tab
   - You should see all workflows listed

3. **First Run**
   - Push a change to trigger workflows
   - OR manually trigger from Actions tab
   - Watch the progress in real-time

## Detailed Setup

### Step 1: Repository Configuration

#### Enable GitHub Actions
1. Go to repository Settings
2. Click "Actions" → "General"
3. Select "Allow all actions and reusable workflows"
4. Save

#### Configure Branch Protection
1. Go to Settings → Branches
2. Add rule for `main` branch:
   - ✅ Require status checks to pass
   - Select: `Backend Tests (Python 3.11)`, `Build Check`
   - ✅ Require branches to be up to date
   - ✅ Require pull request reviews
3. Save changes

### Step 2: Secrets Configuration (Optional)

#### Codecov Integration
If using Codecov for coverage reports:

1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Add your repository
4. Copy the upload token
5. In GitHub: Settings → Secrets and variables → Actions
6. Click "New repository secret"
7. Name: `CODECOV_TOKEN`
8. Value: (paste token)
9. Click "Add secret"

### Step 3: Verify Workflows

#### Check Workflow Syntax
```bash
# Install actionlint (workflow linter)
brew install actionlint  # macOS
# or
sudo apt install actionlint  # Linux

# Lint all workflows
actionlint .github/workflows/*.yml
```

#### Test Workflows Locally (Optional)
```bash
# Install act (run GitHub Actions locally)
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflows locally
act -l  # List workflows
act push  # Simulate push event
```

### Step 4: Add Status Badges

Add to your main `README.md`:

```markdown
# The Daily Worker

[![Backend Tests](https://github.com/USERNAME/REPO/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/backend-tests.yml)
[![Code Quality](https://github.com/USERNAME/REPO/actions/workflows/code-quality.yml/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/code-quality.yml)
[![CI Pipeline](https://github.com/USERNAME/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/ci.yml)
```

**Replace:**
- `USERNAME` with your GitHub username
- `REPO` with your repository name

## Workflow Details

### Backend Tests Workflow

**File:** `.github/workflows/backend-tests.yml`

**Triggers:**
- Push to `main` or `develop` (backend/database changes)
- Pull requests to `main` or `develop`
- Manual dispatch

**Matrix Strategy:**
- Tests run on Python 3.9, 3.10, and 3.11
- Parallel execution for speed
- Fail-fast disabled (all versions complete)

**Steps:**
1. Checkout code
2. Set up Python with caching
3. Install dependencies
4. Run pytest with verbose output
5. Generate coverage (Python 3.11 only)
6. Upload coverage to Codecov
7. Upload artifacts

**Artifacts:**
- Coverage HTML report (7 days retention)
- Test database on failure (3 days)

### Code Quality Workflow

**File:** `.github/workflows/code-quality.yml`

**Checks:**
- **Black**: Code formatting (PEP 8)
- **isort**: Import statement organization
- **Flake8**: Style guide enforcement
- **Pylint**: Code analysis and linting
- **Bandit**: Security vulnerability scanning

**Configuration:**
- Max line length: 120
- Continue on error (warnings don't fail build)
- Security report uploaded as artifact

### CI Pipeline Workflow

**File:** `.github/workflows/ci.yml`

**Orchestration:**
- Runs all sub-workflows
- Includes security scanning
- Validates build and imports
- Provides unified status

**Jobs:**
1. Backend tests (reusable workflow)
2. Code quality (reusable workflow)
3. Security scan (Safety check)
4. Build validation
5. Status aggregation

### Dependency Update Workflow

**File:** `.github/workflows/dependency-update.yml`

**Schedule:** Weekly (Mondays, 9 AM UTC)

**Actions:**
- Audits dependencies with `pip-audit`
- Checks for outdated packages
- Creates GitHub issues for vulnerabilities
- Uploads audit report

## Customization

### Change Test Trigger Paths

Edit trigger paths in workflows:

```yaml
on:
  push:
    paths:
      - 'projects/DWnews/backend/**'
      - 'projects/DWnews/database/**'
      - 'your/custom/path/**'
```

### Add Python Versions

Edit matrix in `backend-tests.yml`:

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
```

### Adjust Linting Rules

Edit linter commands in `code-quality.yml`:

```yaml
- name: Run Flake8
  run: |
    flake8 backend/ \
      --max-line-length=100 \
      --ignore=E203,W503
```

### Change Test Coverage Threshold

Add to `backend-tests.yml`:

```yaml
- name: Check coverage threshold
  run: |
    pytest --cov=backend \
      --cov-fail-under=80  # Fail if coverage < 80%
```

## Troubleshooting

### Common Issues

#### 1. Workflow Not Running

**Symptoms:** No workflow runs appear in Actions tab

**Solutions:**
- Check workflow syntax with `actionlint`
- Verify trigger paths match changed files
- Ensure Actions are enabled in repo settings
- Check branch protection isn't blocking runs

#### 2. Import Errors in Tests

**Symptoms:** `ModuleNotFoundError` in CI but works locally

**Solutions:**
- Verify PYTHONPATH is set in workflow
- Check that `database/__init__.py` exists
- Ensure all packages are in requirements.txt

#### 3. Tests Pass Locally but Fail in CI

**Symptoms:** Tests work on your machine but fail in GitHub Actions

**Solutions:**
- Check for hardcoded paths (use relative paths)
- Verify database files are created in temp directories
- Check for timezone-dependent code
- Ensure no local environment variables are required

#### 4. Dependency Installation Fails

**Symptoms:** `pip install` step fails

**Solutions:**
- Pin package versions in requirements.txt
- Check for system dependencies (apt packages)
- Verify Python version compatibility
- Clear pip cache in workflow

#### 5. Coverage Upload Fails

**Symptoms:** Codecov step shows errors

**Solutions:**
- Verify `CODECOV_TOKEN` is set correctly
- Check Codecov service status
- Coverage upload is non-blocking (won't fail build)
- Try regenerating Codecov token

### Debug Mode

Enable debug logging:

1. Go to Settings → Secrets and variables → Actions
2. Add variable: `ACTIONS_STEP_DEBUG` = `true`
3. Re-run workflow
4. View detailed logs

### Get Workflow Logs

```bash
# Install GitHub CLI
brew install gh  # macOS
# or
sudo apt install gh  # Linux

# View workflow runs
gh run list

# View specific run
gh run view RUN_ID

# Download logs
gh run download RUN_ID
```

## Monitoring

### Email Notifications

Configure in GitHub Settings → Notifications:
- Send notifications for failed workflows
- Daily digest of workflow activity

### Workflow Status

Check workflow health:
1. Actions tab → Choose workflow
2. View success rate
3. Monitor average run time
4. Review failure patterns

### Performance

Typical run times:
- Backend Tests: ~1-2 minutes
- Code Quality: ~30 seconds
- Full CI Pipeline: ~3-4 minutes

## Best Practices

### 1. Keep Tests Fast
- Target < 2 minutes for full test suite
- Use test database fixtures efficiently
- Parallelize where possible

### 2. Meaningful Commits
```bash
# Good commit messages trigger appropriate workflows
git commit -m "fix(backend): Fix article status validation"
git commit -m "test: Add tests for editorial workflow"
```

### 3. Review Before Merge
- Always review workflow results before merging
- Don't merge failing tests
- Check code coverage trends

### 4. Update Dependencies
- Review weekly dependency audit reports
- Update packages regularly
- Test thoroughly after updates

### 5. Monitor Workflow Costs
- GitHub Actions free tier: 2,000 minutes/month
- Optimize workflows to stay within limits
- Use caching to reduce build time

## Advanced Configuration

### Conditional Execution

Run tests only when specific files change:

```yaml
jobs:
  test:
    if: |
      contains(github.event.head_commit.message, '[test]') ||
      github.event_name == 'pull_request'
```

### Matrix Exclusions

Exclude specific combinations:

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
    exclude:
      - python-version: '3.9'
```

### Concurrency Control

Prevent concurrent runs:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### Environment Variables

Set defaults for all steps:

```yaml
env:
  PYTHONPATH: ${{ github.workspace }}/projects/DWnews
  DEBUG: false
```

## Migration from Other CI

### From Travis CI
- Replace `.travis.yml` with workflows
- Update build matrix syntax
- Adjust environment variable names

### From CircleCI
- Replace `.circleci/config.yml`
- Convert jobs to workflow jobs
- Update caching mechanism

### From Jenkins
- Convert Jenkinsfile to YAML
- Replace shell scripts with workflow steps
- Update artifact handling

## Support Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Codecov Documentation](https://docs.codecov.com/)

## Maintenance

### Weekly Tasks
- Review dependency audit reports
- Check workflow success rates
- Monitor execution times

### Monthly Tasks
- Update action versions (e.g., `actions/checkout@v4`)
- Review and update branch protection rules
- Audit workflow permissions

### Quarterly Tasks
- Review and optimize workflow configurations
- Update Python versions tested
- Audit secrets and clean up unused ones

## Success Checklist

- [ ] All workflows visible in Actions tab
- [ ] Backend tests passing on all Python versions
- [ ] Code quality checks running
- [ ] Security scans completing
- [ ] Branch protection rules active
- [ ] Status badges added to README
- [ ] Team trained on workflow usage
- [ ] Monitoring and alerts configured

---

**Status:** Once setup is complete, your repository will have enterprise-grade CI/CD! 🚀
