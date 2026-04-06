import sqlite3
from datetime import date
import re


def create_table():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products ( 
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        date TEXT NOT NULL,
        sku TEXT NOT NULL,
        features TEXT,
        quantity INTEGER
        )
    ''')

    conn.commit()
    conn.close()

def insert_product (name,price,features,quantity):
    sku = re.sub(r'\W+', '', name).lower()[:30]
    features_str = ", ".join(features)
    match = re.search(r'\d+', quantity)  # returns first match or None
    q = int(match.group()) if match else None
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""INSERT INTO products(name,price,date,sku,features,quantity) VALUES (?,?,?,?,?,?)""",(name,price,str(date.today()),sku,features_str,q))
    conn.commit()
    conn.close()