import asyncio
from playwright.async_api import async_playwright

async def capture_dagster():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Navigate to Dagster Assets
        print("Navigating to Dagster...")
        await page.goto("http://localhost:3000/assets")
        
        # Wait for the asset graph to load
        await page.wait_for_selector(".bp3-spinner", state="hidden", timeout=10000)
        await page.wait_for_timeout(3000) # Give it an extra 3 seconds to render SVG
        
        # Take a screenshot
        os.makedirs("docs/dashboards", exist_ok=True)
        await page.screenshot(path="docs/dashboards/dagster_local.png", full_page=True)
        print("Screenshot saved to docs/dashboards/dagster_local.png")
        
        await browser.close()

if __name__ == "__main__":
    import os
    asyncio.run(capture_dagster())
