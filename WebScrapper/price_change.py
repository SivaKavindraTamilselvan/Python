import sqlite3
from datetime import date, timedelta
import csv

def compare_prices():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))

    cursor.execute("""
        SELECT p1.name, p1.price, p2.price
        FROM products p1
        JOIN products p2
        ON p1.sku = p2.sku
        WHERE p1.date=? AND p2.date=?
    """, (today, yesterday))

    rows = cursor.fetchall()

    with open("price_changes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["Name", "Old Price", "New Price", "Change"])

        for name, new_price, old_price in rows:
            if new_price != old_price:
                change = new_price - old_price
                writer.writerow([name, old_price, new_price, change])

    conn.close()