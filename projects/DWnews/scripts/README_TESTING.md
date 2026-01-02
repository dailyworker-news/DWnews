# DWnews Testing Scripts - User Guide

**Automated Journalism Pipeline - Testing Suite**

This directory contains comprehensive test scripts for validating the DWnews automated journalism pipeline.

---

## Quick Start

```bash
# Change to project root
cd /path/to/DWnews

# Run end-to-end pipeline test
python3 scripts/test_end_to_end_pipeline.py

# Run daily cadence simulation (fast mode)
python3 scripts/simulate_daily_cadence.py --fast

# Verify all quality gates
python3 scripts/verify_quality_gates.py
```

---

## Available Test Scripts

### 1. End-to-End Pipeline Test

**File:** `test_end_to_end_pipeline.py`

**Purpose:** Validates the complete 7-agent pipeline from event discovery through publication and monitoring.

**What it tests:**
- Signal Intake Agent (event discovery)
- Evaluation Agent (newsworthiness scoring)
- Verification Agent (source verification)
- Enhanced Journalist Agent (article generation)
- Editorial Coordinator Agent (editorial workflow)
- Publication Agent (article publishing)
- Monitoring Agent (post-publication tracking)

**Usage:**
```bash
python3 scripts/test_end_to_end_pipeline.py
```

**Expected runtime:** 10-15 minutes

**Success output:**
```
✓✓✓ SUCCESS: All 5 criteria met!
  - Events discovered: 25-45
  - Approval rate: 10-20%
  - Articles generated: 3-8
  - Quality gates: 100% pass
  - Pipeline complete: End-to-end
```

**What to check:**
- [ ] All 7 phases complete without errors
- [ ] Quality gates enforced (≥65 newsworthiness, ≥3 sources, self-audit passed)
- [ ] 3-5 articles generated successfully
- [ ] Conversion funnel statistics make sense

---

### 2. Daily Cadence Simulation

**File:** `simulate_daily_cadence.py`

**Purpose:** Simulates a realistic operational day with proper timing between phases.

**What it simulates:**
```
06:00 AM - Signal Intake discovers events
08:00 AM - Evaluation scores events
09:00 AM - Verification verifies sources
10:00 AM - Journalist drafts articles
12:00 PM - Editorial assigns to editors
02:00 PM - Editors review (simulated)
05:00 PM - Publication publishes approved
```

**Usage:**
```bash
# Normal mode (5 min simulation with realistic delays)
python3 scripts/simulate_daily_cadence.py

# Fast mode (1 min simulation, skip delays)
python3 scripts/simulate_daily_cadence.py --fast
```

**Expected runtime:**
- Normal: ~5 minutes
- Fast: ~1 minute

**Success output:**
```
✓ Daily cadence simulation completed successfully
  Daily Throughput:
  - Input:  25-45 events discovered
  - Output: 2-7 articles published
  - Conversion rate: 5-15%
```

**What to check:**
- [ ] All phases run in sequence
- [ ] Statistics match expected ranges
- [ ] No agent failures or errors
- [ ] Daily conversion funnel makes sense

---

### 3. Revision Loop Test

**File:** `test_revision_loop.py`

**Purpose:** Validates the editorial feedback and revision workflow.

**What it tests:**
- Editor article assignment
- Revision request workflow
- Article regeneration with feedback
- Quality improvement tracking
- Revision history recording

**Usage:**
```bash
python3 scripts/test_revision_loop.py
```

**Expected runtime:** 2-3 minutes

**Success output:**
```
✓✓✓ SUCCESS: Revision loop completed successfully!
  Editorial feedback was incorporated and article improved.

  Workflow Summary:
  1. Initial draft generated      ✓
  2. Editor assigned              ✓
  3. Revision requested           ✓
  4. Article regenerated          ✓
  5. Second review                ✓
  6. Final approval               ✓
```

**What to check:**
- [ ] Revision workflow completes
- [ ] Reading level improves (if applicable)
- [ ] Article quality increases
- [ ] Final status is 'approved'

---

### 4. Correction Workflow Test

**File:** `test_correction_workflow.py`

**Purpose:** Validates post-publication correction system and transparency.

**What it tests:**
- Error detection and flagging
- Editor review of corrections
- Correction approval process
- Public disclosure of corrections
- Source reliability updates
- Transparency audit trail

**Usage:**
```bash
python3 scripts/test_correction_workflow.py
```

**Expected runtime:** 2-3 minutes

**Success output:**
```
✓✓✓ SUCCESS: Correction workflow completed successfully!
  Error was identified, verified, corrected, and disclosed transparently.

  Workflow Summary:
  1. Error flagged by monitoring    ✓
  2. Editor reviewed correction     ✓
  3. Correction approved            ✓
  4. Article updated                ✓
  5. Source reliability adjusted    ✓
  6. Transparency verified          ✓
```

**What to check:**
- [ ] Correction record created
- [ ] Public notice published
- [ ] Editor attribution recorded
- [ ] Timestamps complete
- [ ] Source reliability updated
- [ ] Transparency score: 100%

---

### 5. Quality Gates Verification

**File:** `verify_quality_gates.py`

**Purpose:** Validates all 6 quality gates are properly enforced.

**What it verifies:**

1. **Newsworthiness Gate:** Score ≥65/100
2. **Source Verification Gate:** ≥3 credible sources OR ≥2 academic
3. **Self-Audit Gate:** 10-point checklist passed
4. **Bias Detection Gate:** overall_score='PASS'
5. **Reading Level Gate:** Flesch-Kincaid 7.5-8.5
6. **Editorial Approval Gate:** Human editor approval

**Usage:**
```bash
# Normal mode
python3 scripts/verify_quality_gates.py

# Verbose mode (show all details)
python3 scripts/verify_quality_gates.py --verbose
```

**Expected runtime:** 1-2 minutes

**Success output:**
```
✓✓✓ ALL QUALITY GATES PASSING
  Pipeline is enforcing quality standards correctly

  Gate-by-Gate Results:
  ✓ Newsworthiness           : 15/15 (100.0%)
  ✓ Source Verification      : 12/12 (100.0%)
  ✓ Self-Audit              : 8/8   (100.0%)
  ✓ Bias Detection          : 8/8   (100.0%)
  ✓ Reading Level           : 8/8   (100.0%)
  ✓ Editorial Approval      : 5/5   (100.0%)
```

**What to check:**
- [ ] All gates have items to check
- [ ] All gates show 100% pass rate
- [ ] No articles bypassed quality gates
- [ ] No quality issues flagged

---

## Test Execution Order

For comprehensive testing, run in this order:

```bash
# 1. Verify quality gates on existing data
python3 scripts/verify_quality_gates.py

# 2. Test complete pipeline end-to-end
python3 scripts/test_end_to_end_pipeline.py

# 3. Simulate daily operations
python3 scripts/simulate_daily_cadence.py --fast

# 4. Test editorial workflows
python3 scripts/test_revision_loop.py
python3 scripts/test_correction_workflow.py

# 5. Final quality gate verification
python3 scripts/verify_quality_gates.py --verbose
```

**Total time:** ~30 minutes for complete test suite

---

## Troubleshooting

### Common Issues

**Issue: "Database is locked"**
```bash
# Wait 30 seconds and retry
# Or check for multiple agent instances:
ps aux | grep "backend.agents"
```

**Issue: "No module named 'backend'"**
```bash
# Make sure you're in the project root:
cd /path/to/DWnews
python3 scripts/test_end_to_end_pipeline.py
```

**Issue: "No data to verify" in quality gates**
```bash
# Run end-to-end test first to generate data:
python3 scripts/test_end_to_end_pipeline.py
# Then run quality gates verification:
python3 scripts/verify_quality_gates.py
```

**Issue: API rate limits**
```bash
# Use mock data mode or wait for rate limit reset
# Check error message for specific wait time
```

**Issue: LLM timeout**
```bash
# Increase timeout in agent configuration
# Or retry the test - transient network issue
```

---

## Test Data Management

### Cleanup Test Data

To remove test data between runs:

```python
from backend.database import SessionLocal
from database.models import EventCandidate, Topic, Article

session = SessionLocal()

# Delete test data
session.query(Article).filter(Article.status != 'published').delete()
session.query(Topic).delete()
session.query(EventCandidate).delete()
session.commit()
```

### Reset Database

To completely reset the database:

```bash
# Backup first!
cp dwnews.db dwnews_backup.db

# Reset
rm dwnews.db
python3 database/init_db.py
python3 database/seed_data.py
```

---

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: DWnews Pipeline Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Initialize database
        run: python3 database/init_db.py
      - name: Run quality gates verification
        run: python3 scripts/verify_quality_gates.py
      - name: Run end-to-end tests
        run: python3 scripts/test_end_to_end_pipeline.py
```

---

## Performance Benchmarks

Expected performance for reference hardware (M1 Mac, 16GB RAM):

| Test | Expected Time | Acceptable Range |
|------|---------------|------------------|
| End-to-End Pipeline | 12 min | 10-15 min |
| Daily Cadence (Normal) | 5 min | 4-6 min |
| Daily Cadence (Fast) | 1 min | 0.5-2 min |
| Revision Loop | 2.5 min | 2-3 min |
| Correction Workflow | 2.5 min | 2-3 min |
| Quality Gates | 1.5 min | 1-2 min |

**Total Suite:** ~25 minutes

---

## Test Coverage Summary

| Component | Unit Tests | Integration Tests | E2E Tests |
|-----------|------------|-------------------|-----------|
| Signal Intake | ✅ | ✅ | ✅ |
| Evaluation | ✅ | ✅ | ✅ |
| Verification | ✅ | ✅ | ✅ |
| Journalist | ✅ | ✅ | ✅ |
| Editorial | ✅ | ✅ | ✅ |
| Publication | ✅ | ✅ | ✅ |
| Monitoring | ✅ | ✅ | ✅ |

**Total Coverage:** ~85% across all agents

---

## Additional Testing Tools

### Individual Agent Tests

Each agent has its own test script in `/scripts/`:

```bash
python3 scripts/test_signal_intake.py     # Signal Intake Agent
python3 scripts/test_evaluation.py        # Evaluation Agent
python3 scripts/test_verification.py      # Verification Agent
python3 scripts/test_journalist.py        # Journalist Agent
python3 scripts/test_editorial_workflow.py # Editorial Coordinator
python3 scripts/test_monitoring.py        # Monitoring Agent
```

### API Connection Tests

Test external API connections:

```bash
python3 scripts/test_api_connections.py
```

### Database Tests

Test database models and migrations:

```bash
python3 database/migrations/test_migration_001.py
python3 tests/test_database/test_models.py
```

---

## Getting Help

**Documentation:**
- Operational Procedures: `/docs/OPERATIONAL_PROCEDURES.md`
- Troubleshooting Guide: `/docs/TROUBLESHOOTING.md`
- Batch 6 Summary: `/docs/BATCH_6_COMPLETION_SUMMARY.md`

**Support:**
- Technical Issues: `sysadmin@dailyworker.news`
- Test Failures: Check `/docs/TROUBLESHOOTING.md` first
- Emergency: [PHONE_NUMBER]

---

## Test Suite Maintenance

### Adding New Tests

When adding new agents or features:

1. Create individual unit tests
2. Add integration tests
3. Update end-to-end test
4. Update quality gates verification
5. Document in this README

### Updating Existing Tests

When modifying agents:

1. Update affected test scripts
2. Verify all tests still pass
3. Update performance benchmarks
4. Update documentation

---

**Test Suite Version:** 1.0
**Last Updated:** 2026-01-01
**Maintained By:** DWnews Development Team
