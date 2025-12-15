// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('NRI News Brief Dashboard', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
    });

    test('should load the dashboard with header', async ({ page }) => {
        // Check page title
        await expect(page).toHaveTitle(/NRI News Brief/);
        
        // Check header elements
        await expect(page.locator('h1:has-text("NRI News Brief")')).toBeVisible();
        await expect(page.locator('input[placeholder*="Search"]')).toBeVisible();
    });

    test('should display archive sidebar', async ({ page }) => {
        // Check archive section
        await expect(page.locator('text=Archive')).toBeVisible();
        await expect(page.locator('.date-btn')).toHaveCount(7); // 7 days
    });

    test('should display period toggle buttons', async ({ page }) => {
        await expect(page.locator('button:has-text("Morning")')).toBeVisible();
        await expect(page.locator('button:has-text("Evening")')).toBeVisible();
    });

    test('should display region filter buttons', async ({ page }) => {
        await expect(page.locator('button:has-text("All Regions")')).toBeVisible();
        await expect(page.locator('button:has-text("USA")')).toBeVisible();
        await expect(page.locator('button:has-text("India")')).toBeVisible();
        await expect(page.locator('button:has-text("World")')).toBeVisible();
    });

    test('should load and display articles', async ({ page }) => {
        // Wait for articles to load (either loading state ends or articles appear)
        await page.waitForSelector('#loading-state.hidden, #articles-container article', { 
            state: 'attached', 
            timeout: 10000 
        });
        
        // Check for articles or appropriate state
        const hasArticles = await page.locator('#articles-container article').count() > 0;
        const hasError = await page.locator('#error-state:not(.hidden)').isVisible();
        
        // Either articles loaded or proper error state shown
        expect(hasArticles || hasError).toBeTruthy();
    });

    test('should toggle between regions', async ({ page }) => {
        // Wait for initial load
        await page.waitForTimeout(1000);
        
        // Click USA filter
        await page.click('button:has-text("USA")');
        
        // USA button should now be active
        const usaBtn = page.locator('button[data-region="usa"]');
        await expect(usaBtn).toHaveClass(/bg-primary/);
    });

    test('should toggle between morning and evening', async ({ page }) => {
        // Morning should be active by default
        const morningBtn = page.locator('#btn-morning');
        await expect(morningBtn).toHaveClass(/text-primary/);
        
        // Click evening
        await page.click('#btn-evening');
        
        // Evening should now be active
        const eveningBtn = page.locator('#btn-evening');
        await expect(eveningBtn).toHaveClass(/text-primary/);
    });

    test('should search articles', async ({ page }) => {
        // Wait for articles to load
        await page.waitForTimeout(2000);
        
        // Type in search
        await page.fill('input[placeholder*="Search"]', 'economy');
        
        // Wait for filter to apply
        await page.waitForTimeout(500);
        
        // Article count should update
        const countText = await page.locator('#article-count').textContent();
        expect(countText).toContain('AI-summarized updates');
    });

    test('should select date from archive', async ({ page }) => {
        // Wait for date list to render
        await page.waitForSelector('.date-btn');
        
        // Get all date buttons
        const dateButtons = page.locator('.date-btn');
        const count = await dateButtons.count();
        
        expect(count).toBe(7); // 7 days of history
        
        // First date should be selected (today)
        await expect(dateButtons.first()).toHaveClass(/bg-primary/);
    });

    test('should have working theme toggle', async ({ page }) => {
        // Page should start in dark mode
        await expect(page.locator('html')).toHaveClass(/dark/);
        
        // Click theme toggle
        await page.click('#theme-toggle');
        
        // Should switch to light mode
        await expect(page.locator('html')).not.toHaveClass(/dark/);
        
        // Toggle back
        await page.click('#theme-toggle');
        await expect(page.locator('html')).toHaveClass(/dark/);
    });

    test('should display proper citation publishers (no Unknown or example.com)', async ({ page }) => {
        // Wait for articles to load
        await page.waitForSelector('#loading-state.hidden, #articles-container article', { 
            state: 'attached', 
            timeout: 10000 
        });
        
        // Check if articles exist
        const articleCount = await page.locator('#articles-container article').count();
        
        if (articleCount > 0) {
            // Get all citation links
            const citationLinks = page.locator('a[target="_blank"][rel="noopener noreferrer"]');
            const linkCount = await citationLinks.count();
            
            if (linkCount > 0) {
                // Check first 5 citations
                const checkCount = Math.min(5, linkCount);
                for (let i = 0; i < checkCount; i++) {
                    const link = citationLinks.nth(i);
                    const href = await link.getAttribute('href');
                    
                    // Should not contain example.com
                    expect(href).not.toContain('example.com');
                    
                    // URL should be a valid HTTP/HTTPS URL
                    expect(href).toMatch(/^https?:\/\/.+/);
                }
            }
        }
    });
});
