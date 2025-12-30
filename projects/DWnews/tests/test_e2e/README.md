# End-to-End Tests

Complete system validation tests for the Daily Worker platform.

## Overview

End-to-end tests validate the entire workflow from content discovery to publishing, including:
- Complete article lifecycle (draft → published → archived)
- API endpoints with real HTTP requests
- Database operations and queries
- Admin dashboard workflows
- Content filtering and pagination
- Multi-source article management

## Test Files

### `test_complete_workflow.py`
Tests the complete content workflow:
- **Topic to Published Article**: Full workflow from discovery to publishing
- **Ongoing Story Workflow**: Marking and querying ongoing stories
- **Multi-Source Articles**: Articles with multiple source citations
- **Article Archival**: Archiving old articles
- **Category Filtering**: Filter articles by category
- **National vs Local**: Filter by regional scope
- **Reading Level Validation**: Ensure reading level constraints

### `test_api_endpoints.py`
Tests all API endpoints:
- **Health Check**: `/api/health` endpoint
- **List Articles**: GET `/api/articles/` with various filters
- **Get Single Article**: GET `/api/articles/{id}`
- **Update Article**: PATCH `/api/articles/{id}`
- **Filter by Status**: draft, published, archived
- **Filter by Ongoing**: ongoing stories vs regular articles
- **Pagination**: limit and offset parameters
- **Combined Filters**: Multiple filters simultaneously

## Running Tests

### Quick Run
```bash
# Run all end-to-end tests
pytest tests/test_e2e/ -v

# Run specific test file
pytest tests/test_e2e/test_complete_workflow.py -v
pytest tests/test_e2e/test_api_endpoints.py -v

# Run specific test
pytest tests/test_e2e/test_api_endpoints.py::TestArticlesEndpoints::test_list_articles_with_data -v
```

### Complete System Test
```bash
# Run comprehensive test suite
./tests/run_e2e_tests.sh
```

This script:
1. Checks environment and dependencies
2. Initializes database if needed
3. Runs unit tests
4. Runs integration tests
5. Runs end-to-end tests
6. Starts backend server and tests endpoints
7. Validates complete system health

## Test Coverage

### Workflow Tests
- ✅ Topic discovery → Article generation → Publishing
- ✅ Draft → Published → Archived status transitions
- ✅ Ongoing story flagging and querying
- ✅ Multi-source article citations
- ✅ Category-based filtering
- ✅ Regional filtering (national/local)
- ✅ Reading level validation

### API Tests
- ✅ Health check endpoint
- ✅ List articles with pagination
- ✅ Get single article details
- ✅ Update article status (publish, archive)
- ✅ Mark articles as ongoing
- ✅ Filter by status (draft/published/archived)
- ✅ Filter by ongoing flag
- ✅ Filter by category
- ✅ Combined multi-filter queries

## Expected Results

### All Tests Passing
When all tests pass, you should see:
```
tests/test_e2e/test_complete_workflow.py ........... PASSED
tests/test_e2e/test_api_endpoints.py ............... PASSED

===================== 25 passed in 2.34s =====================
```

### Test Database
Tests use an in-memory SQLite database that is:
- Created fresh for each test
- Isolated from production data
- Automatically cleaned up after tests
- Fast (no disk I/O)

## Fixtures Used

Tests rely on fixtures from `conftest.py`:
- `db_session`: In-memory database session
- `sample_category`: Pre-created category
- `sample_source`: Pre-created news source
- `client`: FastAPI test client (API tests only)

## CI/CD Integration

These tests can be run in CI/CD pipelines:

### GitHub Actions Example
```yaml
- name: Run E2E Tests
  run: |
    python -m pytest tests/test_e2e/ -v
```

### GitLab CI Example
```yaml
test-e2e:
  script:
    - pytest tests/test_e2e/ -v
```

## Troubleshooting

### Import Errors
If you see import errors, ensure you're running from the project root:
```bash
cd /path/to/daily_worker/projects/DWnews
pytest tests/test_e2e/ -v
```

### Database Errors
If tests fail with database errors:
```bash
# Clean up any test databases
rm -f test_*.db

# Run tests again
pytest tests/test_e2e/ -v
```

### API Test Failures
If API tests fail:
1. Check that FastAPI is installed: `pip install fastapi`
2. Check that test client is working: `pip install httpx`
3. Verify database models are up to date

## Test Markers

Tests can be filtered using markers:
```bash
# Run only workflow tests
pytest tests/test_e2e/ -m workflow

# Run only API tests
pytest tests/test_e2e/ -m api

# Skip slow tests
pytest tests/test_e2e/ -m "not slow"
```

## Performance

### Expected Test Times
- Workflow tests: ~2 seconds
- API tests: ~3 seconds
- Total E2E suite: ~5 seconds

### Optimization Tips
- Tests use in-memory database (fast)
- Parallel execution: `pytest -n auto` (requires pytest-xdist)
- Skip slow tests during development: `pytest -m "not slow"`

## Maintenance

### Adding New Tests
1. Add test to appropriate file (workflow vs API)
2. Use existing fixtures where possible
3. Follow naming convention: `test_<feature>_<scenario>`
4. Add docstrings explaining what's being tested
5. Use assertions to validate expected behavior

### Updating Tests
When models or APIs change:
1. Update affected test cases
2. Run tests to verify changes
3. Update this README if test coverage changes

## Quality Gates

Before deploying:
- ✅ All E2E tests must pass
- ✅ No database errors
- ✅ API endpoints responding correctly
- ✅ Workflow from discovery to publishing works
- ✅ Admin actions (publish, archive, ongoing) work

## See Also

- [Test Suite README](../README.md) - Overview of all tests
- [Integration Tests](../test_integration/) - Integration test documentation
- [Backend Tests](../test_backend/) - Backend unit tests
- [Database Tests](../test_database/) - Database model tests
