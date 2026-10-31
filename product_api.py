import requests

API_URL = "https://dummyjson.com/products/search"


def search_products(query):

    if not query.strip():
        return []

    try:
        response = requests.get(
            API_URL,
            params={
                "q": query,
                "limit": 30
            },
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        products = []

        for item in data.get("products", []):

            products.append({
                "id": item.get("id"),
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
            })

        return products

    except requests.RequestException as error:
        print(f"API Error: {error}")
        return []