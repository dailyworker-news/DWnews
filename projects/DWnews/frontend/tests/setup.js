/**
 * Vitest Setup File
 * Runs before all tests
 */

// Mock API base URL
globalThis.API_BASE_URL = 'http://localhost:8000/api';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
globalThis.localStorage = localStorageMock;

// Mock fetch globally
globalThis.fetch = vi.fn();

// Setup DOM before each test
beforeEach(() => {
  // Clear mocks
  vi.clearAllMocks();

  // Reset fetch mock
  globalThis.fetch.mockReset();

  // Clear localStorage
  localStorage.clear();
});
