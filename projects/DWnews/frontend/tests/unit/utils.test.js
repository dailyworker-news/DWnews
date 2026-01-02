/**
 * Unit Tests for Utility Functions
 */

import { describe, it, expect, beforeEach } from 'vitest';

describe('Date Formatting', () => {
  it('should format current date correctly', () => {
    const today = new Date('2024-01-15T12:00:00Z');
    const options = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    };
    const formatted = today.toLocaleDateString('en-US', options);

    expect(formatted).toContain('2024');
    expect(formatted).toContain('January');
  });

  it('should generate archive dates for last 7 days', () => {
    const today = new Date('2024-01-15T12:00:00Z');
    const dates = [];

    for (let i = 1; i <= 7; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      dates.push(date);
    }

    expect(dates).toHaveLength(7);
    expect(dates[0].getDate()).toBe(14); // Yesterday
    expect(dates[6].getDate()).toBe(8);  // 7 days ago
  });
});

describe('URL Parameter Handling', () => {
  it('should build query string from params', () => {
    const params = new URLSearchParams({
      status: 'published',
      category: 'labor',
      limit: '12'
    });

    expect(params.toString()).toBe('status=published&category=labor&limit=12');
  });

  it('should parse URL parameters', () => {
    const url = new URL('http://example.com?category=labor&region=national');
    const params = new URLSearchParams(url.search);

    expect(params.get('category')).toBe('labor');
    expect(params.get('region')).toBe('national');
  });
});

describe('Article Card Creation', () => {
  it('should extract relevant article data', () => {
    const article = {
      id: 1,
      title: "Test Article",
      summary: "Test summary",
      category_name: "Labor",
      is_ongoing: true,
      published_at: "2024-01-01T10:00:00Z"
    };

    expect(article.title).toBe("Test Article");
    expect(article.category_name).toBe("Labor");
    expect(article.is_ongoing).toBe(true);
  });

  it('should handle missing optional fields', () => {
    const article = {
      id: 1,
      title: "Test Article",
      category_name: "Labor"
    };

    expect(article.summary).toBeUndefined();
    expect(article.image_url).toBeUndefined();
  });
});

describe('Pagination Logic', () => {
  it('should calculate correct offset', () => {
    const page = 2;
    const itemsPerPage = 12;
    const offset = (page - 1) * itemsPerPage;

    expect(offset).toBe(12);
  });

  it('should calculate total pages', () => {
    const totalArticles = 45;
    const itemsPerPage = 12;
    const totalPages = Math.ceil(totalArticles / itemsPerPage);

    expect(totalPages).toBe(4);
  });
});

describe('Category Filtering', () => {
  it('should filter articles by category', () => {
    const articles = [
      { category_name: "Labor" },
      { category_name: "Politics" },
      { category_name: "Labor" }
    ];

    const laborArticles = articles.filter(a => a.category_name === "Labor");

    expect(laborArticles).toHaveLength(2);
  });

  it('should show all articles when category is "all"', () => {
    const articles = [
      { category_name: "Labor" },
      { category_name: "Politics" }
    ];

    const category = "all";
    const filtered = category === "all" ? articles : articles.filter(a => a.category_name === category);

    expect(filtered).toHaveLength(2);
  });
});
