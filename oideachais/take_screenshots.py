from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    
    # Dagster
    try:
        print("Navigating to Dagster...")
        page.goto("http://localhost:3335")
        page.wait_for_timeout(3000) # Wait for UI to render
        page.screenshot(path="dagster_ui.png", full_page=True)
        print("Saved dagster_ui.png")
    except Exception as e:
        print("Failed to screenshot Dagster:", e)
        
    # MotherDuck
    try:
        print("Navigating to MotherDuck...")
        page.goto("https://app.motherduck.com/")
        page.wait_for_timeout(5000)
        page.screenshot(path="motherduck_ui.png", full_page=True)
        print("Saved motherduck_ui.png")
    except Exception as e:
        print("Failed to screenshot MotherDuck:", e)

    browser.close()
