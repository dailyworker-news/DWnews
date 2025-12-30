# Test Suite

Comprehensive test suite for The Daily Worker project.

## Running Tests

### Run All Tests
```bash
cd projects/DWnews
pytest
```

### Run Specific Test Files
```bash
# Database tests
pytest tests/test_database/

# Backend tests
pytest tests/test_backend/

# Script tests
pytest tests/test_scripts/

# Integration tests
pytest tests/test_integration/
```

### Run Specific Test Classes
```bash
pytest tests/test_database/test_models.py::TestArticleModel
```

### Run with Coverage
```bash
pytest --cov=backend --cov=database --cov=scripts --cov-report=html
open htmlcov/index.html
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Markers
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m database      # Run only database tests
```

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures
├── test_database/
│   ├── test_models.py              # Database model tests
│   ├── test_init_db.py             # Database initialization tests
│   └── test_seed_data.py           # Seed data tests
├── test_backend/
│   ├── test_config.py              # Configuration tests
│   └── test_logging.py             # Logging tests
├── test_scripts/
│   ├── test_text_utils.py          # Text utility tests
│   ├── test_filter_topics.py       # Topic filtering tests
│   └── test_generate_articles.py  # Article generation tests
└── test_integration/
    └── test_content_pipeline.py    # End-to-end pipeline tests
```

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `test_db_engine` - In-memory SQLite database engine
- `db_session` - Database session for each test
- `sample_source` - Pre-created news source
- `sample_category` - Pre-created category
- `sample_region` - Pre-created region
- `sample_topic` - Pre-created topic
- `sample_article` - Pre-created article

## Writing New Tests

### Test Naming Convention
- File: `test_*.py`
- Class: `Test*`
- Function: `test_*`

### Example Test
```python
def test_article_creation(db_session, sample_category):
    """Test creating a new article"""
    article = Article(
        title="Test Article",
        slug="test-article",
        body="Test content",
        category_id=sample_category.id
    )
    db_session.add(article)
    db_session.commit()

    assert article.id is not None
    assert article.title == "Test Article"
```

### Using Markers
```python
import pytest

@pytest.mark.unit
def test_something():
    """Unit test"""
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_pipeline():
    """Integration test that's slow"""
    pass
```

## Test Coverage

Current test coverage:

- ✅ Database Models (90%+)
- ✅ Backend Configuration (80%+)
- ✅ Text Utilities (95%+)
- ✅ Topic Filtering (85%+)
- ✅ Content Pipeline Integration (75%+)

### Coverage Goals
- Maintain >80% coverage on core modules
- >90% coverage on utility functions
- >70% coverage on integration workflows

## Continuous Integration

Tests are designed to run in CI/CD environments:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r backend/requirements.txt
    pip install pytest pytest-cov
    pytest --cov --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Test Database

Tests use an in-memory SQLite database by default:
- Fast test execution
- No cleanup needed
- Isolated test environment

For PostgreSQL-specific tests:
```python
@pytest.fixture
def postgres_session():
    engine = create_engine("postgresql://test:test@localhost/test_db")
    # ...
```

## Mocking External APIs

For tests that would call external APIs:

```python
from unittest.mock import patch, Mock

def test_rss_discovery(db_session):
    with patch('feedparser.parse') as mock_parse:
        mock_parse.return_value = Mock(entries=[
            {'title': 'Test', 'description': 'Test'}
        ])

        # Run test with mocked RSS feed
        # ...
```

## Performance Tests

For performance-sensitive code:

```python
import time

def test_query_performance(db_session):
    """Test that query completes in <500ms"""
    start = time.time()

    # Run query
    results = db_session.query(Article).filter_by(
        status='published'
    ).limit(100).all()

    duration = time.time() - start
    assert duration < 0.5  # Must complete in 500ms
```

## Troubleshooting

### Import Errors
```bash
# Make sure you're in the project root
cd projects/DWnews

# Install test dependencies
pip install pytest pytest-cov
```

### Database Errors
```bash
# Tests use in-memory database, but if you see errors:
rm dwnews.db  # Remove actual database
pytest        # Re-run tests
```

### Fixture Not Found
Check that `conftest.py` is in the tests directory and properly imported.

## Best Practices

1. **One assertion per test** (when possible)
2. **Use descriptive test names**
3. **Keep tests isolated** (no dependencies between tests)
4. **Mock external dependencies**
5. **Test edge cases**
6. **Use fixtures for common setup**
7. **Clean up after tests** (fixtures handle this automatically)

## Running Tests Before Commit

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run fast tests only
pytest -m "not slow"
```

Add to git pre-commit hook:
```bash
#!/bin/sh
cd projects/DWnews
pytest -m "not slow"
```
