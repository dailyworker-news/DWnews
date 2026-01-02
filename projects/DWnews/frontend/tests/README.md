# Frontend Tests

Comprehensive testing suite for The Daily Worker frontend using Vitest (unit/integration) and Playwright (E2E).

## Test Coverage

### Unit Tests (`tests/unit/`)
- **utils.test.js** - Utility function tests
  - Date formatting
  - URL parameter handling
  - Article data extraction
  - Pagination logic
  - Category filtering

### Integration Tests (`tests/integration/`)
- **api.test.js** - API integration tests
  - Fetch articles
  - Fetch single article (by ID and slug)
  - API error handling
  - Health checks
- **dom.test.js** - DOM manipulation tests
  - Article card rendering
  - Navigation controls
  - Pagination UI
  - Loading states
  - Error displays

### E2E Tests (`tests/e2e/`)
- **homepage.spec.js** - Homepage functionality
  - Page load and rendering
  - Navigation between categories
  - Pagination
  - Responsive design (mobile, tablet, desktop)
- **article-page.spec.js** - Article detail page
  - Article content display
  - Metadata rendering
  - Navigation
  - Special sections
- **admin.spec.js** - Admin interface
  - Dashboard access
  - Article review workflow

## Running Tests

### Prerequisites

Install dependencies:

```bash
cd projects/DWnews/frontend
npm install
```

### Unit & Integration Tests

```bash
# Run all unit/integration tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run test:coverage
```

### E2E Tests

```bash
# Run E2E tests (headless)
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Run E2E tests in headed mode (see browser)
npm run test:e2e:headed

# Run specific E2E test file
npx playwright test tests/e2e/homepage.spec.js
```

### Run All Tests

```bash
npm run test:all
```

## Test Configuration

### Vitest (`vitest.config.js`)
- **Environment**: happy-dom (fast DOM simulation)
- **Coverage**: V8 provider with HTML/LCOV reports
- **Setup**: Global test utilities in `tests/setup.js`

### Playwright (`playwright.config.js`)
- **Browsers**: Chromium, Firefox, WebKit
- **Base URL**: http://localhost:8000
- **Screenshots**: On failure only
- **Retries**: 2 in CI, 0 locally

## Test Structure

```
tests/
├── setup.js                    # Global test setup
├── fixtures/
│   └── articles.js             # Test data fixtures
├── unit/
│   └── utils.test.js           # Unit tests
├── integration/
│   ├── api.test.js             # API integration tests
│   └── dom.test.js             # DOM tests
└── e2e/
    ├── homepage.spec.js        # Homepage E2E tests
    ├── article-page.spec.js    # Article page E2E tests
    └── admin.spec.js           # Admin E2E tests
```

## Writing New Tests

### Unit Test Example

```javascript
import { describe, it, expect } from 'vitest';

describe('My Feature', () => {
  it('should do something', () => {
    const result = myFunction();
    expect(result).toBe(expected);
  });
});
```

### Integration Test Example

```javascript
import { describe, it, expect, beforeEach } from 'vitest';
import { mockArticles } from '../fixtures/articles.js';

describe('API Integration', () => {
  beforeEach(() => {
    globalThis.fetch.mockReset();
  });

  it('should fetch data', async () => {
    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockArticles
    });

    const response = await fetch('/api/articles/');
    const data = await response.json();

    expect(data).toHaveLength(3);
  });
});
```

### E2E Test Example

```javascript
import { test, expect } from '@playwright/test';

test('homepage loads successfully', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/The Daily Worker/);
});
```

## Code Quality

### Linting

```bash
# Run ESLint
npm run lint

# Fix linting issues
npm run lint:fix
```

### Formatting

```bash
# Check formatting
npm run format:check

# Auto-format code
npm run format
```

## CI/CD Integration

Tests run automatically in GitHub Actions:

- **Unit/Integration Tests**: Run on Node 18.x and 20.x
- **E2E Tests**: Run on Chromium, Firefox, WebKit
- **Coverage Reports**: Uploaded to Codecov
- **Build Validation**: Ensures frontend builds successfully

## Debugging

### Debug Unit Tests

```bash
# Run specific test file
npm test -- tests/unit/utils.test.js

# Run tests matching pattern
npm test -- --grep "Date Formatting"
```

### Debug E2E Tests

```bash
# Run with Playwright Inspector
npx playwright test --debug

# Run specific test
npx playwright test tests/e2e/homepage.spec.js --debug

# View test report
npx playwright show-report
```

### View Coverage Report

After running `npm run test:coverage`:

```bash
# Open HTML coverage report
open coverage/index.html
```

## Mocking

### Mock API Calls

```javascript
globalThis.fetch.mockResolvedValueOnce({
  ok: true,
  json: async () => ({ data: 'test' })
});
```

### Mock localStorage

```javascript
localStorage.setItem('key', 'value');
expect(localStorage.setItem).toHaveBeenCalledWith('key', 'value');
```

## Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Use Fixtures**: Share test data via fixtures
3. **Mock External Dependencies**: Mock API calls, not internal functions
4. **Test User Behavior**: Focus on what users do, not implementation
5. **Keep Tests Fast**: Unit tests should run in milliseconds
6. **Meaningful Assertions**: Test meaningful outcomes, not trivial details
7. **Clear Test Names**: Describe what the test verifies

## Common Issues

### Port Already in Use

If E2E tests fail with "port already in use":

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Browser Not Installed

```bash
# Install Playwright browsers
npx playwright install
```

### Tests Pass Locally but Fail in CI

- Check for timing issues (add waits where needed)
- Verify test data is consistent
- Check for hardcoded paths or URLs

## Performance

- **Unit Tests**: ~100-300ms
- **Integration Tests**: ~500ms-1s
- **E2E Tests**: ~2-5 minutes
- **Total Test Suite**: ~3-6 minutes

## Continuous Improvement

- Add tests for new features
- Increase coverage to >80%
- Add visual regression testing
- Add accessibility tests
- Add performance tests

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library](https://testing-library.com/)
