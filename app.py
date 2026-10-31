import streamlit as st
from google import genai

from product_api import search_products
from local_shop_api import search_local_shops
from product_matcher import find_same_products

from price_tracker import (
    save_price_history,
    get_price_history,
    save_to_wishlist,
    get_wishlist,
    remove_from_wishlist,
    save_price_alert,
    get_price_alerts,
    remove_price_alert
)


# Page Configuration
st.set_page_config(
    page_title="BuyWise AI",
    page_icon="🛍️",
    layout="wide"
)


# Gemini AI Setup
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)


# Application Title
st.title("🛍️ BuyWise AI")
st.subheader("One Search. Every Shopping Option.")

st.write(
    "Compare online products and nearby offline shops "
    "in one place."
)


USD_TO_INR = 88  # Demo conversion rate


# Initialize Session State
if "search_results" not in st.session_state:
    st.session_state.search_results = None

if "ai_answer" not in st.session_state:
    st.session_state.ai_answer = None


# Search Inputs
st.header("🔎 Product Search")

sort_option = st.selectbox(
    "Sort online products by",
    [
        "Default",
        "Price: Low to High",
        "Price: High to Low",
        "Rating: High to Low"
    ]
)

product = st.text_input(
    "What are you looking for?",
    placeholder="e.g. laptop, Samsung, shoes"
)

city = st.text_input(
    "Your city",
    placeholder="e.g. Jind"
)

budget = st.number_input(
    "Your maximum budget (₹)",
    min_value=100,
    max_value=1000000,
    value=50000,
    step=1000
)

min_rating = st.slider(
    "Minimum Product Rating",
    min_value=0.0,
    max_value=5.0,
    value=0.0,
    step=0.5
)

category_filter = st.selectbox(
    "Select Product Category",
    [
        "All Categories",
        "smartphones",
        "laptops",
        "tablets",
        "mobile-accessories"
    ]
)

local_sort = st.selectbox(
    "Sort Local Shops By",
    [
        "Default",
        "Price: Low to High",
        "Price: High to Low"
    ]
)


# Compare All Options
if st.button("Compare All Options", type="primary"):

    if not product.strip():

        st.warning("Please enter a product name.")

    else:

        with st.spinner("Finding shopping options..."):

            online_products = search_products(product)

            local_products = search_local_shops(
                product,
                city if city.strip() else None
            )

        # Convert USD to INR
        for item in online_products:

            item["price_inr"] = (
                item["price"] * USD_TO_INR
            )

        # Filter Online Products by Budget
        online_products = [
            item for item in online_products
            if item["price_inr"] <= budget
        ]

        # Filter by Rating
        online_products = [
            item for item in online_products
            if item.get("rating", 0) >= min_rating
        ]

        # Filter by Category
        if category_filter != "All Categories":

            online_products = [
                item for item in online_products
                if item.get("category", "").lower()
                == category_filter
            ]

        # Filter Local Products by Budget
        local_products = [
            item for item in local_products
            if item["price_inr"] <= budget
        ]

        # Sort Online Products
        if sort_option == "Price: Low to High":

            online_products.sort(
                key=lambda x: x["price_inr"]
            )

        elif sort_option == "Price: High to Low":

            online_products.sort(
                key=lambda x: x["price_inr"],
                reverse=True
            )

        elif sort_option == "Rating: High to Low":

            online_products.sort(
                key=lambda x: x["rating"],
                reverse=True
            )

        # Sort Local Products
        if local_sort == "Price: Low to High":

            local_products.sort(
                key=lambda x: x["price_inr"]
            )

        elif local_sort == "Price: High to Low":

            local_products.sort(
                key=lambda x: x["price_inr"],
                reverse=True
            )

        # Calculate Value Score
        if online_products:

            max_price = max(
                item["price_inr"]
                for item in online_products
            )

            if max_price <= 0:
                max_price = 1

            for item in online_products:

                price_score = 1 - (
                    item["price_inr"] / max_price
                )

                rating_score = (
                    item["rating"] / 5
                )

                item["value_score"] = (
                    0.4 * price_score
                    + 0.6 * rating_score
                )

            # Save Price History
            save_price_history(online_products)

        # Find Same Products
        same_products = find_same_products(
            online_products,
            local_products
        )

        # Store Search Results
        st.session_state.search_results = {
            "online": online_products,
            "local": local_products,
            "same": same_products
        }

        # Clear Previous AI Answer
        st.session_state.ai_answer = None


# Initialize Display Variables
online_products = []
local_products = []
same_products = []


# Display Search Results
if st.session_state.search_results is not None:

    online_products = (
        st.session_state.search_results["online"]
    )

    local_products = (
        st.session_state.search_results["local"]
    )

    same_products = (
        st.session_state.search_results["same"]
    )


    # Shopping Insights Dashboard
    st.divider()
    st.header("📊 Shopping Insights Dashboard")

    if online_products:

        total_products = len(online_products)

        cheapest_product = min(
            online_products,
            key=lambda x: x["price_inr"]
        )

        average_rating = sum(
            item["rating"]
            for item in online_products
        ) / total_products

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Products Found",
                total_products
            )

        with col2:

            st.metric(
                "Lowest Price",
                f"₹{cheapest_product['price_inr']:,.2f}"
            )

        with col3:

            st.metric(
                "Average Rating",
                f"{average_rating:.2f}/5"
            )

        st.info(
            f"Best Budget Option: {cheapest_product['name']}"
        )

    else:

        st.info(
            "No online products found within your filters."
        )


    # BuyWise AI Recommendations
    st.header("💡 BuyWise AI Recommendations")

    if online_products:

        cheapest = min(
            online_products,
            key=lambda x: x["price_inr"]
        )

        highest_rated = max(
            online_products,
            key=lambda x: x["rating"]
        )

        best_value = max(
            online_products,
            key=lambda x: x["value_score"]
        )

        st.info("💡 Best Value Recommendation")

        st.subheader(best_value["name"])

        st.write(
            f"Price: ₹{best_value['price_inr']:,.2f}"
        )

        st.write(
            f"Rating: ⭐ {best_value['rating']}/5"
        )

        st.write(
            f"Value Score: "
            f"{best_value['value_score'] * 100:.2f}/100"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.success("🏷️ Lowest Price")

            st.write(cheapest["name"])

            st.write(
                f"₹{cheapest['price_inr']:,.2f}"
            )

        with col2:

            st.success("⭐ Highest Rated")

            st.write(highest_rated["name"])

            st.write(
                f"Rating: {highest_rated['rating']}/5"
            )


    # Online Shopping
    st.header("🌐 Online Shopping")

    if online_products:

        for item in online_products:

            with st.container(border=True):

                col1, col2 = st.columns([1, 3])

                with col1:

                    if item.get("image"):

                        st.image(
                            item["image"],
                            use_container_width=True
                        )

                with col2:

                    st.subheader(item["name"])

                    st.write(
                        f"Brand: {item['brand']}"
                    )

                    st.write(
                        f"Price: ₹{item['price_inr']:,.2f}"
                    )

                    st.caption(
                        f"Original Price: ${item['price']}"
                    )

                    st.write(
                        f"Rating: ⭐ {item['rating']}/5"
                    )

                    st.write(
                        f"Description: "
                        f"{item.get('description', 'Not available')}"
                    )

                    st.write(
                        f"Category: "
                        f"{item.get('category', 'Not available')}"
                    )

                    st.write(
                        f"Stock: {item.get('stock', 'Not available')} units"
                    )

                    st.write(
                        f"Availability: "
                        f"{item.get('availability', 'Not available')}"
                    )

                    st.caption(
                        "Source: DummyJSON test API"
                    )

                    if st.button(
                        "♡ Add to Wishlist",
                        key=f"wishlist_{item['id']}"
                    ):

                        save_to_wishlist(item)

                        st.success(
                            "Product added to Wishlist!"
                        )

    else:

        st.info(
            "No online products found within your budget."
        )


    # Product Comparison Table
    st.header("📊 Product Comparison Table")

    if online_products:

        comparison_data = []

        for item in online_products:

            comparison_data.append({

                "Product": item["name"],

                "Brand": item["brand"],

                "Price (₹)": round(
                    item["price_inr"], 2
                ),

                "Rating": item["rating"],

                "Value Score": round(
                    item["value_score"] * 100, 2
                )
            })

        st.dataframe(
            comparison_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No products available for comparison."
        )


    # Price History Tracker
    st.header("📈 Product Price History")

    if online_products:

        selected_product = st.selectbox(
            "Select a product to view price history",
            [item["name"] for item in online_products]
        )

        history = get_price_history(
            selected_product
        )

        if history:

            st.line_chart({

                "Price (₹)": [
                    row[1] for row in history
                ]

            })

            st.dataframe(
                [
                    {
                        "Product": row[0],
                        "Price (₹)": row[1],
                        "Checked At": row[2]
                    }
                    for row in history
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No price history available."
            )


    # Price Drop Alert
    st.divider()
    st.header("🔔 Price Drop Alerts")

    if online_products:

        alert_product = st.selectbox(
            "Select product for price alert",
            [item["name"] for item in online_products],
            key="alert_product"
        )

        selected_item = next(
            item for item in online_products
            if item["name"] == alert_product
        )

        current_price = selected_item["price_inr"]

        st.write(
            f"Current Price: ₹{current_price:,.2f}"
        )

        target_price = st.number_input(
            "Enter your target price (₹)",
            min_value=1.0,
            max_value=1000000.0,
            value=float(
                max(1, int(current_price * 0.9))
            ),
            step=100.0,
            key="target_price"
        )

        if st.button("🔔 Set Price Alert"):

            save_price_alert(
                alert_product,
                target_price
            )

            st.success(
                "Price alert saved successfully!"
            )

    else:

        st.info(
            "Search a product first to set a price alert."
        )


    # Local Offline Shops
    st.header("🏪 Local Offline Shops")

    if local_products:

        for item in local_products:

            with st.container(border=True):

                st.subheader(
                    item["product_name"]
                )

                st.write(
                    f"Shop: {item['shop_name']}"
                )

                st.write(
                    f"City: {item['city']}"
                )

                st.write(
                    f"Price: ₹{item['price_inr']:,.0f}"
                )

                st.write(
                    f"Availability: {item['stock_status']}"
                )

                st.write(
                    f"Verified: {item['verified']}"
                )

                st.caption(
                    "Sample testing listing. Contact and verify "
                    "the shop before visiting."
                )

    else:

        st.info(
            "No local shop listings found."
        )


    # Same Product Comparison
    st.header("🔍 Same Product Comparison")

    if same_products:

        for item in same_products:

            with st.container(border=True):

                st.subheader(
                    item["product"]
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.write("🌐 Online Store")

                    online_inr = (
                        item["online_price"] * USD_TO_INR
                    )

                    st.write(
                        f"Price: ₹{online_inr:,.2f}"
                    )

                with col2:

                    st.write("🏪 Local Shop")

                    st.write(
                        f"Shop: {item['local_shop']}"
                    )

                    st.write(
                        f"Price: ₹{item['local_price']:,.0f}"
                    )

                local_inr = item["local_price"]

                difference = abs(
                    online_inr - local_inr
                )

                if online_inr < local_inr:

                    st.success(
                        "🏆 Online Shopping is Cheaper!"
                    )

                    st.write(
                        f"You save ₹{difference:,.2f} online."
                    )

                elif local_inr < online_inr:

                    st.success(
                        "🏆 Local Shop is Cheaper!"
                    )

                    st.write(
                        f"You save ₹{difference:,.2f} locally."
                    )

                else:

                    st.info(
                        "Both options have the same price."
                    )

    else:

        st.info(
            "No exact product matches found."
        )


    st.divider()

    st.caption(
        "BuyWise AI prototype: Online demo data and "
        "locally stored shop listings. Live marketplace "
        "integration is still under development."
    )


# Saved Price Alerts
st.divider()
st.subheader("📋 Your Saved Price Alerts")

saved_alerts = get_price_alerts()

if saved_alerts:

    current_prices = {
        item["name"]: item["price_inr"]
        for item in online_products
    }

    for alert in saved_alerts:

        alert_name = alert[0]
        target = alert[1]

        with st.container(border=True):

            st.write(
                f"Product: {alert_name}"
            )

            st.write(
                f"Target Price: ₹{target:,.2f}"
            )

            if alert_name in current_prices:

                current = current_prices[alert_name]

                st.write(
                    f"Current Price: ₹{current:,.2f}"
                )

                if current <= target:

                    st.success(
                        "🎉 Price Drop Alert! Target price reached."
                    )

                else:

                    st.info(
                        "Price has not reached your target yet."
                    )

            else:

                st.caption(
                    "Search this product again to check its current demo price."
                )

            if st.button(
                "Remove Alert",
                key=f"remove_alert_{alert_name}"
            ):

                remove_price_alert(alert_name)

                st.rerun()

else:

    st.info(
        "No price alerts saved yet."
    )


# AI Shopping Assistant
st.divider()
st.header("🤖 AI Shopping Assistant")

st.write(
    "Ask questions and get smart shopping recommendations."
)

user_question = st.text_input(
    "Ask your shopping question",
    placeholder="e.g. Which product is best for my budget?"
)

if st.button("Ask AI Assistant"):

    if not user_question.strip():

        st.warning(
            "Please enter your question."
        )

    elif st.session_state.search_results is None:

        st.warning(
            "Please search for products first."
        )

    else:

        online_data = (
            st.session_state.search_results["online"]
        )

        local_data = (
            st.session_state.search_results["local"]
        )

        shopping_context = f"""
        You are BuyWise AI Shopping Assistant.

        Online Products:
        {online_data[:10]}

        Local Shop Products:
        {local_data[:10]}

        User Question:
        {user_question}

        Instructions:
        - Recommend products based only on provided data.
        - Compare prices, ratings and value for money.
        - Never invent product prices or availability.
        - Clearly mention when information is missing.
        - Online prices are demo data.
        - Local shop listings are sample testing data.
        - Explain your recommendation in simple language.
        """

        try:

            with st.spinner(
                "AI is analysing your shopping options..."
            ):

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=shopping_context
                )

            st.session_state.ai_answer = response.text

        except Exception as error:

            st.error(
                f"AI Error: {error}"
            )


# Display AI Answer
if st.session_state.ai_answer:

    st.subheader("💡 AI Recommendation")

    st.write(
        st.session_state.ai_answer
    )


# My Wishlist
st.divider()
st.header("❤️ My Wishlist")

wishlist_items = get_wishlist()

if wishlist_items:

    for item in wishlist_items:

        with st.container(border=True):

            col1, col2 = st.columns([1, 3])

            with col1:

                if item[3]:

                    st.image(
                        item[3],
                        use_container_width=True
                    )

            with col2:

                st.subheader(item[0])