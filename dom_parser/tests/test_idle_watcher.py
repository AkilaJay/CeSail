import pytest
import asyncio
from playwright.async_api import async_playwright, TimeoutError
from dom_parser.src.py.idle_watcher import wait_for_page_quiescence

# Test URLs - mix of static and dynamic pages
TEST_URLS = [
    "https://example.com",  # Static page
    "https://news.ycombinator.com",  # Dynamic content
    "https://reactjs.org",  # SPA
]

@pytest.mark.asyncio
async def test_idle_watcher_static_page():
    """Test idle watcher on a static page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Navigate to a static page
        await page.goto("https://example.com")
        
        # Wait for quiescence
        await wait_for_page_quiescence(page)
        
        # Verify page loaded
        title = await page.title()
        assert "Example Domain" in title
        
        await browser.close()

@pytest.mark.asyncio
async def test_idle_watcher_dynamic_page():
    """Test idle watcher on a dynamic page (Hacker News)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Navigate to Hacker News
        await page.goto("https://news.ycombinator.com")
        
        # Wait for quiescence
        await wait_for_page_quiescence(page)
        
        # Wait for the page to be ready
        await page.wait_for_load_state("networkidle")
        
        # Wait for stories to load (using a more reliable selector)
        await page.wait_for_selector("tr.athing", timeout=30000)
        
        # Verify content loaded
        stories = await page.query_selector_all("tr.athing")
        assert len(stories) > 0
        
        await browser.close()

@pytest.mark.asyncio
async def test_idle_watcher_spa():
    """Test idle watcher on a Single Page Application."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Navigate to a SPA (React docs)
        await page.goto("https://react.dev")
        
        # Wait for initial quiescence
        await wait_for_page_quiescence(page)
        
        # Wait for the app to be ready
        await page.wait_for_load_state("networkidle")
        await page.wait_for_selector("nav", state="visible", timeout=30000)
        
        # Click a link to trigger SPA navigation
        await page.click('a[href="/learn"]')
        
        # Wait for quiescence after navigation
        await wait_for_page_quiescence(page)
        
        # Verify navigation worked
        await page.wait_for_selector("h1", timeout=30000)
        title = await page.title()
        assert "React" in title
        h1_text = await page.inner_text("h1")
        assert "Quick Start" in h1_text
        
        await browser.close()

@pytest.mark.asyncio
async def test_idle_watcher_multiple_navigations():
    """Test idle watcher with multiple page navigations."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # First navigation
        await page.goto("https://example.com")
        await wait_for_page_quiescence(page)
        
        # Second navigation
        await page.goto("https://news.ycombinator.com")
        await wait_for_page_quiescence(page)
        
        # Wait for the page to be ready
        await page.wait_for_load_state("networkidle")
        
        # Wait for stories to load (using a more reliable selector)
        await page.wait_for_selector("tr.athing", timeout=30000)
        
        # Verify content loaded
        stories = await page.query_selector_all("tr.athing")
        assert len(stories) > 0
        
        await browser.close()

@pytest.mark.asyncio
async def test_idle_watcher_url_filtering():
    """Test idle watcher with URL filtering."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Navigate to a page with analytics
        await page.goto("https://example.com")
        
        # Wait for quiescence, ignoring analytics requests
        await wait_for_page_quiescence(page, skip_urls=["/analytics"])
        
        # Verify page loaded
        title = await page.title()
        assert "Example Domain" in title
        
        await browser.close()

@pytest.mark.asyncio
async def test_idle_watcher_custom_timeout():
    """Test idle watcher with custom timeout."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Navigate to a page
        await page.goto("https://example.com")
        
        # Wait for quiescence with custom timeout
        await wait_for_page_quiescence(page, idle_ms=500)
        
        # Verify page loaded
        title = await page.title()
        assert "Example Domain" in title
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(pytest.main([__file__, "-v"])) 