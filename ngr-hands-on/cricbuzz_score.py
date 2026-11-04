# Going to extract cricket score from cricbuzz.com using playwright
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.cricbuzz.com/")
    selector = ".carousal-item:first-child .shadow.rounded-md a"

    # Wait for the scorecard element to load
    page.wait_for_selector(selector, timeout=15000)  # Wait for up to 15 seconds

    # Extract the scorecard text
    scorecard = page.query_selector(selector).inner_text()

    print("Current Cricket Score:")
    print(scorecard)

    browser.close()
