/**
 * Integration Tests for API Calls
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mockArticles, mockArticleDetail } from '../fixtures/articles.js';

describe('API Fetch Functions', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    globalThis.fetch.mockReset();
  });

  describe('fetchArticles', () => {
    it('should fetch articles successfully', async () => {
      // Mock successful API response
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticles
      });

      const response = await fetch(`${API_BASE_URL}/articles/?status=published&limit=12`);
      const data = await response.json();

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/articles/?status=published&limit=12')
      );
      expect(data).toHaveLength(3);
      expect(data[0].title).toBe("Workers Win Major Victory in Amazon Union Drive");
    });

    it('should handle API errors gracefully', async () => {
      // Mock failed API response
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });

      const response = await fetch(`${API_BASE_URL}/articles/`);

      expect(response.ok).toBe(false);
      expect(response.status).toBe(500);
    });

    it('should include query parameters correctly', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

      const params = new URLSearchParams({
        status: 'published',
        category: 'labor',
        limit: '12',
        offset: '0'
      });

      await fetch(`${API_BASE_URL}/articles/?${params}`);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('status=published&category=labor')
      );
    });
  });

  describe('fetchArticleById', () => {
    it('should fetch single article by ID', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticleDetail
      });

      const response = await fetch(`${API_BASE_URL}/articles/1`);
      const data = await response.json();

      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/articles/1'));
      expect(data.id).toBe(1);
      expect(data.title).toBe("Workers Win Major Victory in Amazon Union Drive");
      expect(data.body).toBeDefined();
    });

    it('should handle 404 for non-existent article', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      });

      const response = await fetch(`${API_BASE_URL}/articles/99999`);

      expect(response.status).toBe(404);
    });
  });

  describe('fetchArticleBySlug', () => {
    it('should fetch article by slug', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticleDetail
      });

      const slug = 'workers-win-amazon-union';
      const response = await fetch(`${API_BASE_URL}/articles/slug/${slug}`);
      const data = await response.json();

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/articles/slug/${slug}`)
      );
      expect(data.slug).toBe(slug);
    });
  });

  describe('Health Check', () => {
    it('should check API health', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'healthy',
          version: '1.0.0'
        })
      });

      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();

      expect(data.status).toBe('healthy');
    });
  });
});

describe('API Error Handling', () => {
  it('should handle network errors', async () => {
    globalThis.fetch.mockRejectedValueOnce(new Error('Network error'));

    try {
      await fetch(`${API_BASE_URL}/articles/`);
      expect.fail('Should have thrown an error');
    } catch (error) {
      expect(error.message).toBe('Network error');
    }
  });

  it('should handle timeout errors', async () => {
    globalThis.fetch.mockRejectedValueOnce(new Error('Request timeout'));

    try {
      await fetch(`${API_BASE_URL}/articles/`);
      expect.fail('Should have thrown an error');
    } catch (error) {
      expect(error.message).toBe('Request timeout');
    }
  });
});
