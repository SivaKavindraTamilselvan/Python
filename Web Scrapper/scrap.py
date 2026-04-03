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

    response = page.goto("https://www.nykaa.com/skin/moisturizers/face-moisturizer-day-cream/c/8394")

    print(response.status)

    page.wait_for_load_state("networkidle")

    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(2)

    products = page.locator("div.css-ifdzs8")

    count = products.count()

    print("Total Products : " , count)

    with open("moisturizer.csv","w",newline="",encoding="utf-8") as f:

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