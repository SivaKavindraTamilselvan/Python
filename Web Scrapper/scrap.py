from playwright.async_api import async_playwright
import asyncio
import csv
import re
from database import create_table , insert_product

async def scrape(url, filename):

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0;Win64;x64)"
        )

        page = await context.new_page()

        with open(filename,"w",newline="",encoding="utf-8") as f:

            writer = csv.writer(f)
            writer.writerow(["Name", "Features", "Price", "Quantity"])

            page_no = 1

            while True:

                print("Scraping Page", page_no)

                page_url = f"{url}?page_no={page_no}&sort=popularity"

                response = await page.goto(page_url, timeout=60000)
                print("Status:", response.status)

                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(3)

                products = page.locator("div.css-ifdzs8")
                count = await products.count()

                print("Total Products:", count)

                if count == 0:
                    print("No products found, stopping.")
                    break

                for i in range(count):
                    product = products.nth(i)

                    try:
                        data = await product.inner_text()
                        data = data.split("\n")

                        features = []
                        name = ""
                        original_cost = ""
                        quantity = ""

                        for line in data:
                            line = line.strip()
                            if line in ["FEATURED", "BESTSELLER", "NEW", "AD"]:
                                features.append(line)
                            elif "₹" in line and original_cost == "":
                                original_cost = int("".join(re.findall(r"\d+", line)))
                            elif "Size" in line or "Sizes" in line:
                                quantity = line
                            else:
                                if name == "":
                                    name = line
                                else:
                                    name += " " + line
                        writer.writerow([name, ", ".join(features), original_cost, quantity])
                        insert_product(name, original_cost, features, quantity)

                    except Exception as e:
                        print("Error:", e)
                        continue

                page_no += 1

        await browser.close()


async def main():

    create_table()

    page_urls = [
        ("https://www.nykaa.com/skin/serums/serums-essence/c/8397", "serums.csv"),
        ("https://www.nykaa.com/skin/moisturizers/face-moisturizer-day-cream/c/8394", "moisturizers.csv"),
    ]

    await asyncio.gather(*(scrape(url, filename) for url, filename in page_urls))

asyncio.run(main())