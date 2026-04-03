from playwright.sync_api import sync_playwright
import time
import csv
import re


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0;Win64;x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    )

    page = context.new_page()

    with open("moisturizer.csv","w",newline="",encoding="utf-8") as f:

        for page_no in range(1,88):

            print("Scrapping Page ", page_no)

            url = f"https://www.nykaa.com/skin/moisturizers/face-moisturizer-day-cream/c/8394?page_no={page_no}&sort=popularity"

            response = page.goto(url, timeout=60000)

            print(response.status)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)

            products = page.locator("div.css-ifdzs8")

            count = products.count()

            print("Total Products : ", count)

            writer = csv.writer(f)

            for i in range(count):
                product = products.nth(i)

                try:
                    data = product.inner_text()
                    data = data.split("\n")
                    print(data)

                    features = []
                    name = ""
                    original_cost = ""
                    discounted_cost = ""
                    quantity = ""

                    for line in data:
                        line = line.strip()
                        if line in ["FEATURED", "BESTSELLER", "NEW", "AD"]:
                            features.append(line)
                        elif "₹" in line and original_cost == "":
                            original_cost = re.findall(r"\d", line)
                            original_cost="".join(original_cost)
                        elif "Size" in line or "Sizes" in line:
                            quantity = line
                        else:
                            if name == "":
                                name = line
                            else:
                                name += " " + line

                    writer.writerow([name, ", ".join(features), original_cost, quantity])
                except:
                    pass

    browser.close()