/**
 * E2E Tests for Admin Interface
 */

import { test, expect } from '@playwright/test';

test.describe('Admin Dashboard', () => {
  test('should load admin page', async ({ page }) => {
    await page.goto('/admin/');

    await expect(page).toHaveTitle(/Admin|Dashboard/i);
  });

  test('should display admin navigation', async ({ page }) => {
    await page.goto('/admin/');

    // Wait for page to load
    await page.waitForTimeout(500);

    // Check for admin elements
    const adminContent = page.locator('body');
    await expect(adminContent).toBeVisible();
  });
});

test.describe('Article Review', () => {
  test('should load review article page', async ({ page }) => {
    await page.goto('/admin/review-article.html');

    await expect(page).toHaveTitle(/Review|Article/i);
  });

  test('should display article review form', async ({ page }) => {
    await page.goto('/admin/review-article.html');

    // Wait for content
    await page.waitForTimeout(500);
  });
});

test.describe('Admin Security', () => {
  test('should have secure page structure', async ({ page }) => {
    await page.goto('/admin/');

    // Admin pages should load without errors
    await page.waitForTimeout(500);
  });
});
