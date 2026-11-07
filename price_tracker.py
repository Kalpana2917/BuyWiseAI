import sqlite3
from datetime import datetime
from pathlib import Path

DB_NAME = Path(__file__).parent / "buywise.db"


# Database Connection
def get_connection():

    conn = sqlite3.connect(
        str(DB_NAME),
        timeout=10
    )

    conn.execute("PRAGMA busy_timeout = 10000")

    return conn


# Get Current Date and Time
def get_current_time():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# Initialize Database Tables
def initialize_database():

    with get_connection() as conn:

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
            CREATE TABLE IF NOT EXISTS wishlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT UNIQUE,
                brand TEXT,
                price_inr REAL,
                image TEXT,
                saved_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT UNIQUE,
                target_price REAL NOT NULL,
                created_at TEXT
            )
        """)

        # Database Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_price_product_time
            ON price_history(product_name, checked_at)
        """)


# Save Product Price History
def save_price_history(products):

    if not products:
        return

    current_time = get_current_time()

    records = [
        (
            item["name"],
            item["price_inr"],
            current_time
        )
        for item in products
    ]

    with get_connection() as conn:

        conn.executemany("""
            INSERT INTO price_history
            (product_name, price_inr, checked_at)
            VALUES (?, ?, ?)
        """, records)


# Get Product Price History
def get_price_history(product_name):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT product_name, price_inr, checked_at
            FROM price_history
            WHERE product_name = ?
            ORDER BY checked_at ASC
        """, (product_name,))

        return cursor.fetchall()


# Create Wishlist Table
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


# Save Product to Wishlist
# Save or Update Product in Wishlist
def save_to_wishlist(item):

    with get_connection() as conn:

        conn.execute("""
            INSERT INTO wishlist
            (product_name, brand, price_inr, image, saved_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(product_name)
            DO UPDATE SET
                brand = excluded.brand,
                price_inr = excluded.price_inr,
                image = excluded.image,
                saved_at = excluded.saved_at
        """, (
            item["name"],
            item.get("brand", "Unknown"),
            item["price_inr"],
            item.get("image", ""),
            get_current_time()
        ))
        
# Get Wishlist
def get_wishlist():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT product_name, brand, price_inr, image, saved_at
            FROM wishlist
            ORDER BY saved_at DESC
        """)

        return cursor.fetchall()


# Remove Wishlist Product
def remove_from_wishlist(product_name):

    with get_connection() as conn:

        conn.execute("""
            DELETE FROM wishlist
            WHERE product_name = ?
        """, (product_name,))


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
# Save or Update Price Alert
def save_price_alert(product_name, target_price):

    with get_connection() as conn:

        conn.execute("""
            INSERT INTO price_alerts
            (product_name, target_price, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(product_name)
            DO UPDATE SET
                target_price = excluded.target_price,
                created_at = excluded.created_at
        """, (
            product_name,
            target_price,
            get_current_time()
        ))

# Get Price Alerts
def get_price_alerts():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT product_name, target_price, created_at
            FROM price_alerts
            ORDER BY created_at DESC
        """)

        return cursor.fetchall()


# Remove Price Alert
def remove_price_alert(product_name):

    with get_connection() as conn:

        conn.execute("""
            DELETE FROM price_alerts
            WHERE product_name = ?
        """, (product_name,))


# Initialize Database
initialize_database()

print("BuyWise AI Database Loaded Successfully!")