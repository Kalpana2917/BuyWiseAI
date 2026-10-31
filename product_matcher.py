import re
from difflib import SequenceMatcher


def normalize_name(name):
    name = name.lower()

    # Standardize storage formats
    name = re.sub(
        r"(\d+)\s*(gb|tb)",
        r"\1\2",
        name
    )

    name = re.sub(r"[^a-z0-9 ]", " ", name)

    return " ".join(name.split())


def match_products(product_a, product_b):

    name_a = normalize_name(product_a)
    name_b = normalize_name(product_b)

    if name_a == name_b:
        return True

    tokens_a = set(name_a.split())
    tokens_b = set(name_b.split())

    # Ignore common generic product words
    common_words = {
        "phone", "mobile", "smartphone",
        "tablet", "new", "original"
    }

    tokens_a -= common_words
    tokens_b -= common_words

    # Check brand compatibility
    brands = {
        "samsung", "apple", "iphone", "xiaomi",
        "redmi", "realme", "oppo", "vivo",
        "oneplus", "motorola", "nokia", "google"
    }

    brand_a = tokens_a & brands
    brand_b = tokens_b & brands

    if brand_a and brand_b and brand_a != brand_b:
        return False

    # Check storage compatibility
    storage_a = {
        t for t in tokens_a
        if re.fullmatch(r"\d+(gb|tb)", t)
    }

    storage_b = {
        t for t in tokens_b
        if re.fullmatch(r"\d+(gb|tb)", t)
    }

    if storage_a and storage_b and storage_a != storage_b:
        return False

    # Check model number compatibility
    model_a = {
        t for t in tokens_a
        if re.search(r"\d", t)
        and not re.fullmatch(r"\d+(gb|tb)", t)
    }

    model_b = {
        t for t in tokens_b
        if re.search(r"\d", t)
        and not re.fullmatch(r"\d+(gb|tb)", t)
    }

    if model_a and model_b and not model_a.intersection(model_b):
        return False

    # Calculate similarity
    similarity = SequenceMatcher(
        None,
        " ".join(sorted(tokens_a)),
        " ".join(sorted(tokens_b))
    ).ratio()

    return similarity >= 0.65


def find_same_products(online_products, local_products):

    matches = []

    for online in online_products:
        for local in local_products:

            if match_products(
                online["name"],
                local["product_name"]
            ):

                matches.append({
                    "product": online["name"],
                    "online_price": online["price"],
                    "local_price": local["price_inr"],
                    "local_shop": local["shop_name"],
                    "local_city": local["city"]
                })

    return matches