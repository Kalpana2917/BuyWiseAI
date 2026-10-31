def compare_prices(online_price, local_price):

    if online_price is None or local_price is None:
        return None

    online_price = float(online_price)
    local_price = float(local_price)

    if online_price <= 0 or local_price <= 0:
        return None

    if online_price < local_price:
        return {
            "best_option": "Online Store",
            "best_price": online_price,
            "saving": round(local_price - online_price, 2)
        }

    elif local_price < online_price:
        return {
            "best_option": "Local Shop",
            "best_price": local_price,
            "saving": round(online_price - local_price, 2)
        }

    else:
        return {
            "best_option": "Both have the same price",
            "best_price": online_price,
            "saving": 0
        }