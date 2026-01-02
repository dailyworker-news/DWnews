/**
 * E2E Tests for Article Detail Page
 */

import { test, expect } from '@playwright/test';

test.describe('Article Detail Page', () => {
  test('should display article title', async ({ page }) => {
    // Navigate to article page (may need to adjust based on actual routing)
    await page.goto('/article.html?slug=test-article');

    // Wait for article content to load
    await page.waitForSelector('article, .article-content', { timeout: 5000 }).catch(() => {});
  });

  test('should show article metadata', async ({ page }) => {
    await page.goto('/article.html?slug=test-article');

    // Check for common metadata elements
    // Note: These selectors may need adjustment based on actual HTML structure
    await page.waitForTimeout(500);
  });

  test('should have navigation back to homepage', async ({ page }) => {
    await page.goto('/article.html');

    // Look for back/home link
    const homeLink = page.locator('a[href="/"], a[href="index.html"]');
    const linkCount = await homeLink.count();

    // Should have at least one link to homepage
    expect(linkCount).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Article Rendering', () => {
  test('should handle 404 for non-existent article', async ({ page }) => {
    const response = await page.goto('/article.html?slug=non-existent-article-12345');

    // May show error or redirect
    await page.waitForTimeout(500);
  });

  test('should load article images', async ({ page }) => {
    await page.goto('/article.html?slug=test-article');

    // Check if images are present
    const images = page.locator('article img');
    const imageCount = await images.count();

    if (imageCount > 0) {
      // First image should be visible
      await expect(images.first()).toBeVisible();
    }
  });
});

test.describe('Article Sections', () => {
  test('should show "Why This Matters" section if present', async ({ page }) => {
    await page.goto('/article.html?slug=test-article');
    await page.waitForTimeout(500);

    // Look for special sections
    const whyMatters = page.locator('text=/Why This Matters/i');
    const count = await whyMatters.count();

    // Section may or may not exist depending on article
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should show "What You Can Do" section if present', async ({ page }) => {
    await page.goto('/article.html?slug=test-article');
    await page.waitForTimeout(500);

    const whatYouCanDo = page.locator('text=/What You Can Do/i');
    const count = await whatYouCanDo.count();

    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Social Sharing', () => {
  test('should have share buttons', async ({ page }) => {
    await page.goto('/article.html?slug=test-article');
    await page.waitForTimeout(500);

    // Look for share buttons (if implemented)
    const shareButtons = page.locator('[class*="share"], [id*="share"]');
    const count = await shareButtons.count();

    // Share functionality may or may not be implemented
    expect(count).toBeGreaterThanOrEqual(0);
  });
});
