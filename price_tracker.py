import sqlite3
from datetime import datetime


DB_NAME = "buywise.db"


# Get current date and time
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Save product price history
def save_price_history(products):

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price_inr REAL NOT NULL,
                checked_at TEXT NOT NULL
            )
        """)

        for item in products:

            cursor.execute("""
                INSERT INTO price_history
                (product_name, price_inr, checked_at)
                VALUES (?, ?, ?)
            """, (
                item["name"],
                item["price_inr"],
                get_current_time()
            ))

        conn.commit()

    finally:
        conn.close()


# Get price history of a product
def get_price_history(product_name):

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price_inr REAL NOT NULL,
                checked_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            SELECT product_name, price_inr, checked_at
            FROM price_history
            WHERE product_name = ?
            ORDER BY checked_at ASC
        """, (product_name,))

        history = cursor.fetchall()

        return history

    finally:
        conn.close()


# Create Wishlist table
def create_wishlist_table(cursor):

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT UNIQUE,
            brand TEXT,
            price_inr REAL,
            image TEXT,
            saved_at TEXT
        )
    """)


# Add product to Wishlist
def save_to_wishlist(item):

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        create_wishlist_table(cursor)

        cursor.execute("""
            INSERT OR IGNORE INTO wishlist
            (product_name, brand, price_inr, image, saved_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            item["name"],
            item.get("brand", "Unknown"),
            item["price_inr"],
            item.get("image", ""),
            get_current_time()
        ))

        conn.commit()

    finally:
        conn.close()


# Get all Wishlist products
def get_wishlist():

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        create_wishlist_table(cursor)

        cursor.execute("""
            SELECT product_name, brand, price_inr, image, saved_at
            FROM wishlist
            ORDER BY saved_at DESC
        """)

        wishlist = cursor.fetchall()

        return wishlist

    finally:
        conn.close()


# Remove product from Wishlist
def remove_from_wishlist(product_name):

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        create_wishlist_table(cursor)

        cursor.execute("""
            DELETE FROM wishlist
            WHERE product_name = ?
        """, (product_name,))

        conn.commit()

    finally:
        conn.close()


print("Price Tracker and Wishlist functions loaded successfully!")
# Create Price Alert Table
def create_price_alert_table(cursor):

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT UNIQUE,
            target_price REAL NOT NULL,
            created_at TEXT
        )
    """)


# Save Price Alert
def save_price_alert(product_name, target_price):

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        create_price_alert_table(cursor)

        cursor.execute("""
            INSERT INTO price_alerts
            (product_name, target_price, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(product_name)
            DO UPDATE SET
            target_price = excluded.target_price
        """, (
            product_name,
            target_price,
            get_current_time()
        ))

        conn.commit()

    finally:
        conn.close()


# Get All Price Alerts
def get_price_alerts():

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        create_price_alert_table(cursor)

        cursor.execute("""
            SELECT product_name, target_price, created_at
            FROM price_alerts
            ORDER BY created_at DESC
        """)

        alerts = cursor.fetchall()

        return alerts

    finally:
        conn.close()


# Remove Price Alert
def remove_price_alert(product_name):

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        create_price_alert_table(cursor)

        cursor.execute("""
            DELETE FROM price_alerts
            WHERE product_name = ?
        """, (product_name,))

        conn.commit()

    finally:
        conn.close()