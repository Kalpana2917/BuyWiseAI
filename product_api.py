import requests
import streamlit as st

API_URL = "https://dummyjson.com/products/search"


@st.cache_data(ttl=300, show_spinner=False)
def search_products(query):

    query = str(query or "").strip()

    if not query:
        return []

    products = {}

    try:

        # First search: Complete product name
        search_terms = [query]

        response = requests.get(
            API_URL,
            params={
                "q": query,
                "limit": 100
            },
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        for item in data.get("products", []):

            product_id = item.get("id")

            if product_id is None or product_id in products:
                continue

            products[product_id] = {
                "id": product_id,
                "name": item.get("title", "Unknown"),
                "price": item.get("price", 0),
                "rating": item.get("rating", 0),
                "brand": item.get("brand", "Unknown"),
                "image": item.get("thumbnail", ""),
                "description": item.get("description", ""),
                "category": item.get("category", "Unknown"),
                "stock": item.get("stock", 0),
                "availability": item.get(
                    "availabilityStatus", "Unknown"
                ),
                "source": "DummyJSON Test API"
            }

        # Fallback search using first two words only
        words = query.split()

        if len(words) > 1:

            fallback_term = " ".join(words[:2])

            if fallback_term.lower() != query.lower():

                response = requests.get(
                    API_URL,
                    params={
                        "q": fallback_term,
                        "limit": 100
                    },
                    timeout=15
                )

                response.raise_for_status()

                data = response.json()

                for item in data.get("products", []):

                    product_id = item.get("id")

                    if product_id is None or product_id in products:
                        continue

                    products[product_id] = {
                        "id": product_id,
                        "name": item.get("title", "Unknown"),
                        "price": item.get("price", 0),
                        "rating": item.get("rating", 0),
                        "brand": item.get("brand", "Unknown"),
                        "image": item.get("thumbnail", ""),
                        "description": item.get("description", ""),
                        "category": item.get("category", "Unknown"),
                        "stock": item.get("stock", 0),
                        "availability": item.get(
                            "availabilityStatus", "Unknown"
                        ),
                        "source": "DummyJSON Test API"
                    }

        return list(products.values())

    except requests.RequestException as error:

        print(f"Product API Error: {error}")

        return list(products.values())

    except (ValueError, KeyError, TypeError) as error:

        print(f"Product Data Error: {error}")

        return list(products.values())