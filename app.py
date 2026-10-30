import streamlit as st

st.set_page_config(
    page_title="BuyWise AI",
    page_icon="🛍️",
    layout="centered"
)

st.title("🛍️ BuyWise AI")
st.subheader("Your Personal AI Shopping Assistant")

st.write(
    "Find suitable products based on your "
    "budget, preferences and requirements."
)

# Demo Product Database
PRODUCTS = [
    {
        "name": "SoundCore Life Q20",
        "category": "headphones",
        "price": 2999,
        "quality": 4,
        "battery": 5,
        "design": 3,
        "warranty": 3,
        "reviews": 4
    },
    {
        "name": "JBL Tune 510BT",
        "category": "headphones",
        "price": 2499,
        "quality": 4,
        "battery": 4,
        "design": 4,
        "warranty": 3,
        "reviews": 4
    },
    {
        "name": "Budget Wireless Headphones",
        "category": "headphones",
        "price": 1499,
        "quality": 3,
        "battery": 3,
        "design": 3,
        "warranty": 2,
        "reviews": 3
    },
    {
        "name": "Wireless Mouse",
        "category": "mouse",
        "price": 799,
        "quality": 4,
        "battery": 4,
        "design": 4,
        "warranty": 3,
        "reviews": 4
    },
    {
        "name": "Laptop Backpack",
        "category": "backpack",
        "price": 1299,
        "quality": 4,
        "battery": 0,
        "design": 4,
        "warranty": 3,
        "reviews": 4
    }
]

PRIORITY_MAP = {
    "Quality": "quality",
    "Price": "price",
    "Battery life": "battery",
    "Design": "design",
    "Warranty": "warranty",
    "Customer reviews": "reviews"
}

# User Inputs
product = st.text_input(
    "What do you want to buy?",
    placeholder="e.g. Wireless headphones"
)

budget = st.number_input(
    "Your maximum budget (₹)",
    min_value=100,
    max_value=100000,
    value=3000,
    step=500
)

priorities = st.multiselect(
    "What matters most to you?",
    list(PRIORITY_MAP.keys()),
    default=["Quality", "Price"]
)

extra = st.text_area(
    "Any other requirements?",
    placeholder="e.g. Good calling quality"
)


# Identify Product Category
def identify_category(query):

    query = query.lower()

    if any(word in query for word in [
        "headphone", "headphones",
        "earphone", "earphones", "headset"
    ]):
        return "headphones"

    if any(word in query for word in [
        "mouse", "mice"
    ]):
        return "mouse"

    if any(word in query for word in [
        "backpack", "bag"
    ]):
        return "backpack"

    return None


# Calculate Product Score
def score_product(item, selected_priorities, max_budget):

    scores = []

    for priority in selected_priorities:

        key = PRIORITY_MAP[priority]

        if key == "price":

            price_score = max(
                1,
                round(5 * (1 - item["price"] / max_budget), 1)
            )

            scores.append(price_score)

        elif item[key] > 0:

            scores.append(item[key])

    preference_score = (
        sum(scores) / len(scores)
        if scores else 3
    )

    bonus = 0.5 if item["price"] <= max_budget * 0.75 else 0

    return round(min(5, preference_score + bonus), 2)


# Recommendation Engine
if st.button("Find My Best Product", type="primary"):

    if not product.strip():

        st.warning("Please enter a product name.")

    else:

        category = identify_category(product)

        if category is None:

            st.info(
                "Currently supported categories: "
                "Headphones, Mouse and Backpack."
            )

        else:

            matches = [
                item for item in PRODUCTS
                if item["category"] == category
                and item["price"] <= budget
            ]

            if not matches:

                st.warning(
                    "No matching products found "
                    "within your budget."
                )

            else:

                for item in matches:

                    item["score"] = score_product(
                        item,
                        priorities,
                        budget
                    )

                matches.sort(
                    key=lambda item: (
                        item["score"],
                        -item["price"]
                    ),
                    reverse=True
                )

                st.success(
                    f"Found {len(matches)} matching products!"
                )

                st.caption(
                    "These are sample demo products, "
                    "not live market listings."
                )

                # Best Recommendation
                best = matches[0]

                st.subheader("🏆 Best Match")

                st.markdown(f"### {best['name']}")

                st.write(
                    f"**Price:** ₹{best['price']:,}"
                )

                st.write(
                    f"**Match Score:** {best['score']}/5"
                )

                st.write(
                    "Recommended according to "
                    "your selected priorities."
                )

                if extra.strip():

                    st.write(
                        "**Your Requirements:**",
                        extra
                    )

                # Product Comparison
                st.subheader("📊 Compare Products")

                for item in matches:

                    with st.container(border=True):

                        st.markdown(
                            f"**{item['name']}**"
                        )

                        st.write(
                            f"Price: ₹{item['price']:,}"
                        )

                        st.write(
                            f"Match Score: {item['score']}/5"
                        )

                        st.progress(
                            item["score"] / 5
                        )

                st.info(
                    "Next upgrade: Real-time product "
                    "search and buying links."
                )