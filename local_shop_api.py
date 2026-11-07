import csv
from pathlib import Path
import streamlit as st

DATA_FILE = Path(__file__).parent / "data" / "local_shops.csv"


@st.cache_data(ttl=300, show_spinner=False)
def search_local_shops(product_name, city=None):

    if not DATA_FILE.exists():
        return []

    product_name = product_name.strip().lower()
    city = city.strip().lower() if city else None

    results = []

    with open(DATA_FILE, "r", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        for shop in reader:

            name = shop.get("product_name", "").lower()
            shop_city = shop.get("city", "").lower()

            if product_name not in name:
                continue

            if city and city not in shop_city:
                continue

            try:
                shop["price_inr"] = float(shop["price_inr"])
            except (ValueError, TypeError, KeyError):
                continue

            results.append(shop)

    return sorted(
        results,
        key=lambda x: x["price_inr"]
    )