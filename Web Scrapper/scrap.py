from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0;Win64;x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    )

    page = context.new_page()

    response = page.goto("https://www.nykaa.com/skin/moisturizers/face-moisturizer-day-cream/c/8394")

    print(response.status)

    browser.close()