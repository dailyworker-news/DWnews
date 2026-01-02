# Backend API Tests

Comprehensive unit tests for The Daily Worker backend API endpoints.

## Test Coverage

### Root and Health Endpoints (2 tests)
- GET `/` - Root endpoint
- GET `/api/health` - Health check

### Articles Endpoints (16 tests)
- GET `/api/articles/` - List articles (with filtering by status, category, region, ongoing)
- GET `/api/articles/{id}` - Get article by ID
- GET `/api/articles/slug/{slug}` - Get article by slug
- PATCH `/api/articles/{id}` - Update article (status, title, body, ongoing)

### Editorial Endpoints (10 tests)
- GET `/api/editorial/pending` - Get pending articles for review
- GET `/api/editorial/review/{id}` - Get full article review data
- POST `/api/editorial/{id}/approve` - Approve article
- POST `/api/editorial/{id}/request-revision` - Request revision
- POST `/api/editorial/{id}/reject` - Reject article
- GET `/api/editorial/overdue` - Get overdue articles
- GET `/api/editorial/workload/{email}` - Get editor workload
- POST `/api/editorial/auto-assign` - Auto-assign articles to editors
- POST `/api/editorial/send-overdue-alerts` - Send overdue alerts

### Integration Tests (2 tests)
- Complete article approval workflow
- Complete article revision workflow

### Error Handling Tests (4 tests)
- Invalid article ID type
- Empty database queries
- Malformed JSON requests
- Missing required fields

### Performance Tests (2 tests)
- Large result set pagination
- Complex filter combinations

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -r backend/tests/requirements-test.txt
```

Or install individually:

```bash
pip install pytest pytest-cov httpx
```

### Run All Tests

From the project root (`/projects/DWnews/`):

```bash
PYTHONPATH=/Users/home/sandbox/daily_worker/projects/DWnews python3 -m pytest backend/tests/test_api_endpoints.py -v
```

### Run Specific Test Class

```bash
PYTHONPATH=/Users/home/sandbox/daily_worker/projects/DWnews python3 -m pytest backend/tests/test_api_endpoints.py::TestArticlesEndpoints -v
```

### Run Specific Test

```bash
PYTHONPATH=/Users/home/sandbox/daily_worker/projects/DWnews python3 -m pytest backend/tests/test_api_endpoints.py::TestArticlesEndpoints::test_get_articles_by_status -v
```

### Run with Coverage Report

```bash
PYTHONPATH=/Users/home/sandbox/daily_worker/projects/DWnews python3 -m pytest backend/tests/test_api_endpoints.py --cov=backend --cov-report=html
```

### Quick Test Run (Less Verbose)

```bash
PYTHONPATH=/Users/home/sandbox/daily_worker/projects/DWnews python3 -m pytest backend/tests/test_api_endpoints.py
```

## Test Database

Tests use a separate SQLite database (`test_dwnews.db`) that is:
- Created fresh for each test function
- Populated with sample data via fixtures
- Automatically cleaned up after each test

The test database is completely isolated from the production/development database.

## Test Fixtures

### `test_db`
Creates a fresh database session for each test with all tables initialized.

### `client`
FastAPI TestClient with database dependency override for isolated testing.

### `sample_data`
Pre-populated test data including:
- 2 categories (Labor & Unions, Politics)
- 2 regions (National, Midwest)
- 2 sources (Associated Press, ProPublica)
- 3 articles (published, draft, under_review)
- 1 article revision

## Test Organization

Tests are organized into classes by functionality:

- `TestRootAndHealth` - Basic API endpoints
- `TestArticlesEndpoints` - Article CRUD operations
- `TestEditorialEndpoints` - Editorial workflow endpoints
- `TestIntegration` - End-to-end workflows
- `TestErrorHandling` - Error cases and validation
- `TestPerformance` - Basic performance tests

## Writing New Tests

To add new tests:

1. Add test method to appropriate class or create new class
2. Use `client` fixture for API calls
3. Use `sample_data` fixture for test data
4. Use `test_db` fixture for direct database access
5. Follow naming convention: `test_<action>_<expected_result>`

Example:

```python
def test_get_article_by_category(self, client, sample_data):
    """Test GET /api/articles/?category=labor-unions"""
    response = client.get("/api/articles/?category=labor-unions")
    assert response.status_code == 200
    data = response.json()
    assert all(article["category_name"] == "Labor & Unions" for article in data)
```

## Continuous Integration

To integrate with CI/CD:

```yaml
# .github/workflows/test.yml
- name: Run backend tests
  run: |
    cd projects/DWnews
    pip install -r backend/tests/requirements-test.txt
    PYTHONPATH=$(pwd) pytest backend/tests/test_api_endpoints.py -v --cov=backend
```

## Notes

- Tests are isolated - each test gets a fresh database
- Database files are automatically cleaned up
- Test data is deterministic and predictable
- All endpoints are tested with both success and failure cases
- Integration tests verify complete workflows
