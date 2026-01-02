# Backend API Tests - Quick Start Guide

## Run Tests (Choose One)

### Option 1: Use the test runner script (Easiest)
```bash
cd projects/DWnews
./backend/tests/run_tests.sh
```

### Option 2: Use pytest directly
```bash
cd projects/DWnews
PYTHONPATH=$(pwd) python3 -m pytest backend/tests/test_api_endpoints.py -v
```

## Common Test Commands

### Run all tests (verbose)
```bash
./backend/tests/run_tests.sh
```

### Quick run (less output)
```bash
./backend/tests/run_tests.sh quick
```

### Run with coverage report
```bash
./backend/tests/run_tests.sh coverage
```

### Run specific test class
```bash
./backend/tests/run_tests.sh class TestArticlesEndpoints
```

### Run specific test method
```bash
./backend/tests/run_tests.sh test TestArticlesEndpoints::test_get_all_articles
```

## Test Results

All 39 tests pass:
- ✅ 2 Root & Health endpoint tests
- ✅ 16 Articles endpoint tests
- ✅ 10 Editorial endpoint tests
- ✅ 2 Integration workflow tests
- ✅ 4 Error handling tests
- ✅ 5 Performance tests

## What Gets Tested

### Articles API
- List articles (with filters)
- Get single article (by ID and slug)
- Update articles
- Pagination

### Editorial API
- Pending articles queue
- Article review data
- Approve/reject/revision workflows
- Editor workload tracking
- Overdue article monitoring

### Workflows
- Complete approval workflow
- Complete revision workflow

## Test Database

- Uses isolated SQLite database (`test_dwnews.db`)
- Fresh database for each test
- Automatic cleanup
- Pre-populated with sample data

## Files

| File | Purpose |
|------|---------|
| `test_api_endpoints.py` | 39 comprehensive API tests |
| `run_tests.sh` | Convenient test runner script |
| `README.md` | Detailed documentation |
| `TEST_SUMMARY.md` | Test coverage summary |
| `requirements-test.txt` | Test dependencies |

## Need Help?

See `backend/tests/README.md` for detailed documentation.
