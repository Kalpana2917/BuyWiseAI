import re
from difflib import SequenceMatcher


# Compile regex patterns once
STORAGE_PATTERN = re.compile(r"(\d+)\s*(gb|tb)")
INVALID_CHARS = re.compile(r"[^a-z0-9 ]")
MODEL_PATTERN = re.compile(r"\d")
STORAGE_TOKEN = re.compile(r"\d+(gb|tb)")

COMMON_WORDS = {
    "phone", "mobile", "smartphone",
    "tablet", "new", "original"
}
VARIANT_WORDS = {
    "ultra", "plus", "pro", "max",
    "mini", "fe", "lite", "se"
}

BRANDS = {
    "samsung", "apple", "iphone", "xiaomi",
    "redmi", "realme", "oppo", "vivo",
    "oneplus", "motorola", "nokia", "google"
}


def normalize_name(name):

    name = str(name or "").lower()

    name = STORAGE_PATTERN.sub(r"\1\2", name)
    name = INVALID_CHARS.sub(" ", name)

    return " ".join(name.split())


def prepare_product(name):

    normalized = normalize_name(name)

    tokens = set(normalized.split())
    tokens -= COMMON_WORDS

    brands = tokens & BRANDS

    storage = {
        token for token in tokens
        if STORAGE_TOKEN.fullmatch(token)
    }

    models = {
        token for token in tokens
        if MODEL_PATTERN.search(token)
        and not STORAGE_TOKEN.fullmatch(token)
    }
    variants= tokens & VARIANT_WORDS

    comparison_name = " ".join(sorted(tokens))

    return {
        "normalized": normalized,
        "tokens": tokens,
        "brands": brands,
        "storage": storage,
        "variants":variants,
        "models": models,
        "comparison_name": comparison_name
    }


def _match_prepared(a, b):

    if a["normalized"] == b["normalized"]:
        return True

    # Reject different brands
    if a["brands"] != b["brands"]:
        return False

    # Reject different storage variants
    if a["storage"] != b["storage"]:
        return False

    if a["variants"]!=b["variants"]:
        return False

    # Reject different model numbers
    if a["models"] != b["models"]:
        return False

    similarity = SequenceMatcher(
        None,
        a["comparison_name"],
        b["comparison_name"]
    ).ratio()

    return similarity >= 0.75


def match_products(product_a, product_b):

    prepared_a = prepare_product(product_a)
    prepared_b = prepare_product(product_b)

    return _match_prepared(prepared_a, prepared_b)


def find_same_products(online_products, local_products):

    matches = []

    # Prepare local products only once
    prepared_local = []

    for local in local_products:

        prepared_local.append((
            local,
            prepare_product(local.get("product_name", ""))
        ))

    # Compare online products with prepared local products
    for online in online_products:

        prepared_online = prepare_product(
            online.get("name", "")
        )

        for local, prepared_shop in prepared_local:

            if _match_prepared(
                prepared_online,
                prepared_shop
            ):

                matches.append({
                    "product": online["name"],
                    "online_price": online["price"],
                    "local_price": local["price_inr"],
                    "local_shop": local["shop_name"],
                    "local_city": local["city"]
                })

    return matches

