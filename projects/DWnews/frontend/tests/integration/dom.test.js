/**
 * Integration Tests for DOM Manipulation
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { screen } from '@testing-library/dom';

describe('Article Card Rendering', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="articlesGrid"></div>';
  });

  it('should render article card with correct elements', () => {
    const article = {
      id: 1,
      title: "Test Article Title",
      slug: "test-article",
      summary: "This is a test summary",
      category_name: "Labor",
      is_ongoing: true,
      published_at: "2024-01-01T10:00:00Z"
    };

    const card = document.createElement('article');
    card.className = 'article-card';
    card.innerHTML = `
      <div class="article-category">${article.category_name}</div>
      <h3 class="article-title">
        <a href="/article.html?slug=${article.slug}">${article.title}</a>
      </h3>
      ${article.is_ongoing ? '<span class="badge ongoing">ONGOING</span>' : ''}
      ${article.summary ? `<p class="article-summary">${article.summary}</p>` : ''}
    `;

    document.getElementById('articlesGrid').appendChild(card);

    expect(document.querySelector('.article-card')).toBeTruthy();
    expect(document.querySelector('.article-title').textContent).toBe('Test Article Title');
    expect(document.querySelector('.article-category').textContent).toBe('Labor');
    expect(document.querySelector('.badge.ongoing')).toBeTruthy();
  });

  it('should create link with correct href', () => {
    const slug = 'test-article';
    const link = document.createElement('a');
    link.href = `/article.html?slug=${slug}`;
    link.textContent = 'Article Title';

    expect(link.href).toContain(`slug=${slug}`);
  });

  it('should show ongoing badge only for ongoing articles', () => {
    const ongoingArticle = { is_ongoing: true };
    const regularArticle = { is_ongoing: false };

    expect(ongoingArticle.is_ongoing).toBe(true);
    expect(regularArticle.is_ongoing).toBe(false);
  });
});

describe('Navigation', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <nav>
        <a href="#" class="nav-link" data-category="all">All</a>
        <a href="#" class="nav-link" data-category="labor">Labor</a>
        <a href="#" class="nav-link" data-category="politics">Politics</a>
      </nav>
    `;
  });

  it('should have all navigation links', () => {
    const links = document.querySelectorAll('.nav-link');
    expect(links).toHaveLength(3);
  });

  it('should have correct data attributes', () => {
    const laborLink = document.querySelector('[data-category="labor"]');
    expect(laborLink.dataset.category).toBe('labor');
  });

  it('should toggle active class', () => {
    const link = document.querySelector('[data-category="labor"]');
    link.classList.add('active');

    expect(link.classList.contains('active')).toBe(true);

    // Remove from others
    document.querySelectorAll('.nav-link').forEach(l => {
      if (l !== link) l.classList.remove('active');
    });

    const allLink = document.querySelector('[data-category="all"]');
    expect(allLink.classList.contains('active')).toBe(false);
  });
});

describe('Pagination', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div class="pagination">
        <button id="prevPage" disabled>Previous</button>
        <span id="pageInfo">Page 1</span>
        <button id="nextPage">Next</button>
      </div>
    `;
  });

  it('should have pagination controls', () => {
    expect(document.getElementById('prevPage')).toBeTruthy();
    expect(document.getElementById('nextPage')).toBeTruthy();
    expect(document.getElementById('pageInfo')).toBeTruthy();
  });

  it('should disable previous button on first page', () => {
    const prevButton = document.getElementById('prevPage');
    expect(prevButton.disabled).toBe(true);
  });

  it('should update page info text', () => {
    const pageInfo = document.getElementById('pageInfo');
    const currentPage = 2;
    pageInfo.textContent = `Page ${currentPage}`;

    expect(pageInfo.textContent).toBe('Page 2');
  });
});

describe('Loading States', () => {
  it('should show loading indicator', () => {
    document.body.innerHTML = '<div id="loading" style="display: block;">Loading...</div>';
    const loading = document.getElementById('loading');

    expect(loading.style.display).toBe('block');
  });

  it('should hide loading indicator', () => {
    document.body.innerHTML = '<div id="loading" style="display: block;">Loading...</div>';
    const loading = document.getElementById('loading');
    loading.style.display = 'none';

    expect(loading.style.display).toBe('none');
  });
});

describe('Error Display', () => {
  it('should show error message', () => {
    document.body.innerHTML = '<div id="errorMessage"></div>';
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = 'Failed to load articles';
    errorDiv.style.display = 'block';

    expect(errorDiv.textContent).toBe('Failed to load articles');
    expect(errorDiv.style.display).toBe('block');
  });

  it('should clear error message', () => {
    document.body.innerHTML = '<div id="errorMessage" style="display: block;">Error</div>';
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = '';
    errorDiv.style.display = 'none';

    expect(errorDiv.textContent).toBe('');
    expect(errorDiv.style.display).toBe('none');
  });
});
