import sqlite3
from datetime import date


def create_table():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products ( 
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        date TEXT NOT NULL,
        features TEXT,
        quantity INTEGER
        )
    ''')

    conn.commit()
    conn.close()

def insert_product (name,price,features,quantity):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""INSERT INTO products VALUES (?,?,?,?,?)""",(name,price,str(date.today()),features,quantity))
    conn.commit()
    conn.close()