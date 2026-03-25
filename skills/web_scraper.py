import asyncio
from playwright.async_api import async_playwright

async def run_scraper(url):
    """
    Skill: Stealth Scraper
    Logic: Uses a headless browser to extract raw text while mimicking human behavior.
    """
    async with async_playwright() as p:
        # Launching browser with human-like 'User Agent'
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # Go to the URL and wait for it to load
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Extract only the visible text from the body
            content = await page.inner_text("body")
            
            # Basic cleaning to remove excess whitespace
            clean_content = " ".join(content.split())
            
            return {"status": "success", "data": clean_content[:10000]} # Limit to 10k chars
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            await browser.close()

# To test it, run: python skills/web_scraper.py (after installing playwright)