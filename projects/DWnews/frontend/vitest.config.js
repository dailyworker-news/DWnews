import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./tests/setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/**',
        'tests/**',
        '**/*.config.js',
        'dev_server.py',
        'dist/**'
      ]
    },
    include: ['tests/**/*.test.js'],
    exclude: ['tests/e2e/**']
  }
});
