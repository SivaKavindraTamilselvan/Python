## Task
Web Scraper with Anti-Bot Bypass

## Objective

Build a scraper that extracts structured data from dynamic, JavaScript-rendered websites. Handle pagination, rate limiting, retries, and rotating user-agents to avoid detection.

## 📋 Requirements

- [x]  HTTP methods, status codes, headers, and cookies
- [x]  HTML/CSS selectors (`BeautifulSoup`, `lxml`)
- [x]  `requests` or `httpx` library
- [x]  `Selenium` or `Playwright` for JS-rendered pages
- [x]  Basic `asyncio` for concurrent requests
- [x]  Regular expressions for pattern extraction

## 💡 Use-Case

- [x]  Scrape e-commerce product listings on a nightly schedule
- [x]  Store product data (name, price, SKU) in SQLite/PostgreSQL
- [x]  Compare against previous day's data and flag price changes
- [x]  Export a daily price-change report as CSV

## SCREENSHOTS

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/9eefab33-55a4-4d50-ad59-8599675a6f6f" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/be72bb29-f0f2-4713-87a5-0754c9ec5234" />
