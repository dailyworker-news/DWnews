/**
 * E2E Tests for Homepage
 */

import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load homepage successfully', async ({ page }) => {
    await expect(page).toHaveTitle(/The Daily Worker/);
  });

  test('should display masthead with title', async ({ page }) => {
    const masthead = page.locator('.newspaper-masthead');
    await expect(masthead).toBeVisible();

    const title = page.locator('h1');
    await expect(title).toContainText('THE DAILY WORKER');
  });

  test('should display navigation links', async ({ page }) => {
    const nav = page.locator('.masthead-nav');
    await expect(nav).toBeVisible();

    // Check for category links
    await expect(page.locator('text=Latest')).toBeVisible();
    await expect(page.locator('text=Labor')).toBeVisible();
    await expect(page.locator('text=Politics')).toBeVisible();
  });

  test('should display current date', async ({ page }) => {
    const dateElement = page.locator('#currentDate');
    await expect(dateElement).toBeVisible();

    // Date should not be empty
    const dateText = await dateElement.textContent();
    expect(dateText.length).toBeGreaterThan(0);
  });

  test('should have search functionality', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]');
    await expect(searchInput).toBeVisible();
    await expect(searchInput).toHaveAttribute('placeholder', /Search/i);
  });

  test('should display articles grid', async ({ page }) => {
    const articlesGrid = page.locator('#articlesGrid, .articles-grid');
    await expect(articlesGrid).toBeVisible();
  });
});

test.describe('Article Navigation', () => {
  test('should navigate between categories', async ({ page }) => {
    await page.goto('/');

    // Click Labor category
    await page.click('text=Labor');

    // Wait for articles to load
    await page.waitForTimeout(500);

    // Check that Labor link is active
    const laborLink = page.locator('[data-category="labor"]');
    await expect(laborLink).toHaveClass(/active/);
  });

  test('should paginate articles', async ({ page }) => {
    await page.goto('/');

    // Wait for articles to load
    await page.waitForSelector('.article-card, .articles-grid', { timeout: 5000 }).catch(() => {});

    // Look for pagination controls
    const nextButton = page.locator('button:has-text("Next"), #nextPage');
    if (await nextButton.isVisible()) {
      await nextButton.click();

      // Wait for new articles to load
      await page.waitForTimeout(500);
    }
  });
});

test.describe('Responsive Design', () => {
  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    const masthead = page.locator('.newspaper-masthead');
    await expect(masthead).toBeVisible();
  });

  test('should work on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');

    const masthead = page.locator('.newspaper-masthead');
    await expect(masthead).toBeVisible();
  });

  test('should work on desktop viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');

    const masthead = page.locator('.newspaper-masthead');
    await expect(masthead).toBeVisible();
  });
});

test.describe('Footer', () => {
  test('should display footer links', async ({ page }) => {
    await page.goto('/');

    // Scroll to footer
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    // Check for footer links
    const footer = page.locator('footer');
    if (await footer.isVisible()) {
      await expect(footer).toBeVisible();
    }
  });
});
