import streamlit as st
from google import genai
from concurrent.futures import ThreadPoolExecutor
from product_api import search_products
from local_shop_api import search_local_shops
from product_matcher import find_same_products
from urllib.parse import quote_plus
import pandas as pd
from google.genai import types
import time

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


# Gemini AI with Automatic Backup Model
@st.cache_data(ttl=300, show_spinner=False)
def get_cached_ai_answer(shopping_context):

    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite"
    ]

    for model_name in models_to_try:

        for attempt in range(2):

            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=shopping_context,
                    config=types.GenerateContentConfig(
                        max_output_tokens=500
                    )
                )

                if response.text:
                    return response.text

            except Exception as error:

                error_message = str(error).upper()

                temporary_error = any(
                    code in error_message
                    for code in [
                        "503", "429", "500",
                        "UNAVAILABLE",
                        "RESOURCE_EXHAUSTED"
                    ]
                )

                if temporary_error and attempt == 0:
                    time.sleep(2)
                    continue

                break

    return (
        "AI services are temporarily unavailable. "
        "Please try again after a few minutes."
    )

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
# ==========================================
# BUYWISE AI - THEME AND CUSTOM UI
# ==========================================

#Initialize Theme State
if "light_mode" not in st.session_state:
    st.session_state.light_mode = True

# Theme Colors

if st.session_state.light_mode:

    bg_color = "#F5F7FC"
    card_color = "#FFFFFF"
    text_color = "#172033"
    muted_color = "#64748B"
    border_color = "#E2E8F0"
    input_color = "#FFFFFF"
    placeholder_color = "#94A3B8"
    link_color = "#4F46E5"

else:

    bg_color = "#0B1020"
    card_color = "#151D32"
    text_color = "#F1F5F9"
    muted_color = "#A5B4CC"
    border_color = "#293650"
    input_color = "#151D32"
    placeholder_color = "#94A3B8"
    link_color = "#A78BFA"


# Custom CSS

st.markdown(f"""
<style>

/* Main Application */

.stApp {{
    background-color: {bg_color};
    color: {text_color};
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

[data-testid="stSidebar"] {{
    background-color: {card_color};
    border-right: 1px solid {border_color};
}}

/* Typography */

h1, h2, h3, h4, h5, h6,
.stMarkdown, .stText,
[data-testid="stWidgetLabel"] p {{
    color: {text_color};
}}

[data-testid="stCaptionContainer"] {{
    color: {muted_color};
}}

/* Cards */

[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: {card_color};
    border: 1px solid {border_color};
    border-radius: 16px;
    padding: 16px;
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}}

[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: #818CF8;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.10);
}}

/* Buttons */

.stButton > button {{
    background: linear-gradient(135deg, #6366F1, #7C3AED);
    color: #FFFFFF !important;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    transition: all 0.2s ease;
}}

.stButton > button:hover {{
    background: linear-gradient(135deg, #4F46E5, #6D28D9);
    color: #FFFFFF !important;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(99, 102, 241, 0.25);
}}

/* Input Fields */

div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="select"] > div {{
    background-color: {input_color} !important;
    border-color: {border_color} !important;
    border-radius: 9px !important;
}}

div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {{
    color: {text_color} !important;
    -webkit-text-fill-color: {text_color} !important;
    caret-color: {text_color} !important;
}}

div[data-baseweb="select"] *,
div[data-baseweb="input"] *,
div[data-baseweb="textarea"] * {{
    color: {text_color};
}}

input::placeholder,
textarea::placeholder {{
    color: {placeholder_color} !important;
    -webkit-text-fill-color: {placeholder_color} !important;
}}

/* Professional Light Mode Inputs */

div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="select"] > div {{
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    min-height: 44px;
    box-shadow: none !important;
}}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="select"] > div:focus-within {{
    border: 1px solid #4F46E5 !important;
    box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.12) !important;
}}

[data-testid="stWidgetLabel"] p {{
    font-weight: 600 !important;
    color: #334155 !important;
}}

/* Dropdown Menu */

[data-baseweb="popover"] {{
    background-color: {card_color} !important;
}}

[data-baseweb="menu"] {{
    background-color: {card_color} !important;
}}

[data-baseweb="menu"] * {{
    color: {text_color} !important;
}}

/* Metrics */

[data-testid="stMetric"] {{
    background-color: {card_color};
    border: 1px solid {border_color};
    padding: 18px;
    border-radius: 14px;
}}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {{
    color: {text_color} !important;
}}

/* Tables */

[data-testid="stDataFrame"],
[data-testid="stTable"] {{
    border: 1px solid {border_color};
    border-radius: 10px;
    overflow: hidden;
}}

/* Images */

[data-testid="stImage"] img {{
    border-radius: 12px;
}}

/* Sidebar Links */

[data-testid="stSidebar"] a {{
    color: {link_color} !important;
    text-decoration: none !important;
    font-weight: 600;
}}

[data-testid="stSidebar"] a:hover {{
    opacity: 0.8;
    text-decoration: underline !important;
}}

/* Dividers */

hr {{
    border-color: {border_color};
}}

/* Scroll Behaviour */

html {{
    scroll-behavior: smooth;
}}

/* Professional Sidebar */

[data-testid="stSidebar"] {{
    background-color: {card_color} !important;
    border-right: 1px solid {border_color};
}}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
    color: {text_color} !important;
    font-weight: 500;
}}

/* Main Page Spacing */

[data-testid="stMainBlockContainer"] {{
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}}

/* Professional Headings */

h1 {{
    font-size: 2.2rem !important;
    font-weight: 750 !important;
    letter-spacing: -0.8px;
}}

h2 {{
    font-weight: 700 !important;
    letter-spacing: -0.4px;
}}

h3 {{
    font-weight: 650 !important;
}}

/* Widget Labels */

[data-testid="stWidgetLabel"] p {{
    color: {text_color} !important;
    font-weight: 600 !important;
}}

/* Smooth Buttons */

.stButton > button {{
    min-height: 44px;
    border-radius: 10px;
    font-weight: 600;
}}
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("---")
st.sidebar.subheader("📌 Navigation")

st.sidebar.markdown("""
<a href="#product-search">🔎 Product Search</a><br><br>
<a href="#shopping-insights">📊 Shopping Insights</a><br><br>
<a href="#online-shopping">🌐 Online Shopping</a><br><br>
<a href="#comparison-table">📋 Comparison Table</a><br><br>
<a href="#price-history">📈 Price History</a><br><br>
<a href="#price-alerts">🔔 Price Alerts</a><br><br>
<a href="#local-shops">🏪 Local Shops</a><br><br>
<a href="#same-product">🔍 Same Product</a><br><br>
<a href="#ai-assistant">🤖 AI Assistant</a><br><br>
<a href="#wishlist">❤️ Wishlist</a>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("One Search. Every Shopping Option.")


# Search Inputs
st.markdown('<div id="product-search"></div>', unsafe_allow_html=True)
st.header("🔎 Product Search")

sort_option = st.selectbox(
    "Sort online products by",
    [
        "Default",
        "Price: Low to High",
        "Price: High to Low",
        "Rating: High to Low",
        "Best Value First"
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
    value=100000,
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

            with ThreadPoolExecutor(max_workers=2) as executor:

                online_future = executor.submit(
                    search_products,
                    product
                )

                local_future = executor.submit(
                    search_local_shops,
                    product,
                    city if city.strip() else None
                )

                online_products = online_future.result()
                local_products = local_future.result()

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

        # Calculate Smart Value Score
        if online_products:

            prices = [
                float(item.get("price_inr", 0) or 0)
                for item in online_products
            ]

            min_price = min(prices)
            max_price = max(prices)

            for item in online_products:

                price = float(item.get("price_inr", 0) or 0)
                rating = float(item.get("rating", 0) or 0)

                # Normalize Price Score
                if max_price == min_price:
                    price_score = 100
                else:
                    price_score = (
                        (max_price - price)
                        / (max_price - min_price)
                    ) * 100

                # Normalize Rating Score
                rating = max(0, min(rating, 5))
                rating_score = (rating / 5) * 100

                # Final Weighted Value Score
                item["value_score"] = round(
                    (0.4 * price_score)
                    + (0.6 * rating_score),
                    2
                )

            # Save Price History
            save_price_history(online_products)

        # Sort Online Products
        if sort_option == "Default":

            online_products.sort(
                key=lambda x: x.get("value_score", 0),
                reverse=True
            )

        elif sort_option == "Price: Low to High":

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

        elif sort_option == "Best Value First":

            online_products.sort(
                key=lambda x: x.get("value_score", 0),
                reverse=True
            )

        # Smart Product Ranking

        ranked_products = sorted(
            online_products,
            key=lambda x: x.get("value_score", 0),
            reverse=True
        )

        for rank, item in enumerate(ranked_products, start=1):
            item["rank"] = rank

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

        # Generate Online Shopping Search Links
        encoded_product = quote_plus(product.strip())

        shopping_links = {
            "Amazon": f"https://www.amazon.in/s?k={encoded_product}",
            "Flipkart": f"https://www.flipkart.com/search?q={encoded_product}",
            "Croma": f"https://www.croma.com/searchB?q={encoded_product}"
        }

        st.session_state.shopping_links = shopping_links

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
    # Online Shopping Platforms
    st.subheader("🛒 Shop Online")

    shopping_links = st.session_state.get(
        "shopping_links", {}
    )

    if shopping_links:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.link_button(
                "Amazon",
                shopping_links["Amazon"],
                use_container_width=True
            )

        with col2:
            st.link_button(
                "Flipkart",
                shopping_links["Flipkart"],
                use_container_width=True
            )

        with col3:
            st.link_button(
                "Croma",
                shopping_links["Croma"],
                use_container_width=True
            )


    # Shopping Insights Dashboard
    st.divider()
    st.markdown('<div id="shoping-insights"></div>', unsafe_allow_html=True)
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

        # Budget-Based Best Value Recommendation

        budget_products = [
            item for item in online_products
            if item["price_inr"] <= budget
        ]

        if budget_products:

            best_value = max(
                budget_products,
                key=lambda x: x.get("value_score", 0)
            )

        else:

            best_value = min(
                online_products,
                key=lambda x: x["price_inr"]
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
            f"{best_value['value_score']:.2f}/100"
        )

        # Smart Recommendation Explanation

        price_difference = (
            best_value["price_inr"] - cheapest["price_inr"]
        )

        rating_percentage = (
            best_value["rating"] / 5
        ) * 100

        st.progress(
            best_value["value_score"] / 100
        )

        st.markdown("### 🧠 Why BuyWise AI Recommends This")

        reasons = []

        if best_value["name"] == cheapest["name"]:
            reasons.append(
                "It is also the lowest-priced available option."
            )
        else:
            reasons.append(
                f"It costs ₹{price_difference:,.2f} more than the cheapest option."
            )

        reasons.append(
            f"It has a customer rating of {best_value['rating']}/5."
        )

        reasons.append(
            f"Its rating score is {rating_percentage:.1f}%."
        )

        for reason in reasons:
            st.write(f"✓ {reason}")

        # Recommendation Confidence
        st.markdown("### 📊 Recommendation Confidence")

        total_options = len(online_products)

        if total_options >= 5:
            st.success(
                f"High Confidence: Compared {total_options} products."
            )

        elif total_options >= 2:
            st.info(
                f"Medium Confidence: Compared {total_options} products."
            )

        else:
            st.warning(
                f"Limited Comparison: Only {total_options} product available.")

        # Smart Product Pros and Cons

        st.markdown("### 🔍 Smart Product Analysis")

        col_pro, col_con = st.columns(2)

        with col_pro:
            st.markdown("#### ✅ Advantages")

            st.write(
                f"• Best value score: "
                f"{best_value['value_score']:.2f}/100"
            )

            st.write(
                f"• Customer rating: "
                f"{best_value['rating']}/5"
            )

            if best_value["name"] == cheapest["name"]:
                st.write("• Lowest-priced available option")
            else:
                st.write("• Offers an alternative to the cheapest option")

        with col_con:
            st.markdown("#### ⚠️ Things to Consider")

            if best_value["price_inr"] > cheapest["price_inr"]:
                st.write(
                    f"• Costs ₹{price_difference:,.2f} "
                    "more than the cheapest option"
                )
            else:
                st.write("• No price disadvantage among available options")

            if best_value["rating"] < 4:
                st.write("• Customer rating is below 4/5")
            else:
                st.write("• Check product specifications before purchasing")

        st.markdown("### 🎯 Best For")

        st.write(
            "Users looking for a balance between price "
            "and customer rating."
        )

        # Final Smart Verdict

        st.markdown("### 🏆 BuyWise AI Final Verdict")

        if best_value["value_score"] >= 80:
            st.success(
                "Strong Recommendation: This product offers "
                "a good balance of price and rating."
            )

        elif best_value["value_score"] >= 60:
            st.info(
                "Good Recommendation: This product is worth "
                "considering."
            )

        else:
            st.warning(
                "Compare More Options: Check other products "
                "before making your purchase."
            )

        st.caption(
            "Recommendation is based on available demo product "
            "data, not verified live retailer information."
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

    st.markdown(
        '<div id="online-shoping"></div>',
        unsafe_allow_html=True
    )

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

                    rank = item.get("rank", 0)

                    if rank == 1:
                        st.success("🥇 #1 Best Value")

                    elif rank == 2:
                        st.info("🥈 #2 Second Best")

                    elif rank == 3:
                        st.info("🥉 #3 Third Best")

                    else:
                        st.caption(f"Rank: {rank}")

                    st.caption(
                        f"{item.get('brand', 'Unknown')}  |  "
                        f"{item.get('category', 'Not available')}"
                    )

                    price_col, rating_col = st.columns(2)

                    with price_col:

                        st.metric(
                            "Demo Reference Price",
                            f"₹{item['price_inr']:,.0f}"
                        )

                    with rating_col:

                        st.metric(
                            "Customer Rating",
                            f"⭐ {item['rating']}/5"
                        )

                    score = min(
                        max(
                            float(item.get("value_score", 0)),
                            0
                        ),
                        100
                    )

                    st.write("🏆 **Smart Value Score**")

                    st.progress(score / 100)

                    st.caption(
                        f"{score:.2f}/100"
                    )

                    if score >= 80:
                        st.success("Excellent Value for Money")

                    elif score >= 60:
                        st.info("Good Value for Money")

                    elif score >= 40:
                        st.warning("Average Value")

                    else:
                        st.caption("Low Value Score")

                with st.expander("📋 Product Details"):

                    st.write(
                        f"**Description:** "
                        f"{item.get('description', 'Not available')}"
                    )

                    st.write(
                        f"**Category:** "
                        f"{item.get('category', 'Not available')}"
                    )

                    st.write(
                        f"**Stock:** "
                        f"{item.get('stock', 'Not available')} units"
                    )

                    st.write(
                        f"**Availability:** "
                        f"{item.get('availability', 'Not available')}"
                    )

                    st.caption(
                        f"Original DummyJSON Price: ${item['price']}"
                    )

                    st.caption(
                        "Source: DummyJSON Test API | Demo data only"
                    )

                # Shopping Platform Links

                search_query = quote_plus(item["name"])

                amazon_url = (
                    f"https://www.amazon.in/s?k={search_query}"
                )

                flipkart_url = (
                    f"https://www.flipkart.com/search?q={search_query}"
                )

                croma_url = (
                    f"https://www.croma.com/searchB?q={search_query}"
                )

                reliance_url = (
                    f"https://www.reliancedigital.in/search?q={search_query}"
                )

                st.markdown("**🛒 Compare on Shopping Platforms**")

                platform_col1, platform_col2 = st.columns(2)

                with platform_col1:

                    st.markdown(
                        f"[Amazon ↗]({amazon_url})"
                    )

                    st.markdown(
                        f"[Flipkart ↗]({flipkart_url})"
                    )

                with platform_col2:

                    st.markdown(
                        f"[Croma ↗]({croma_url})"
                    )

                    st.markdown(
                        f"[Reliance Digital ↗]({reliance_url})"
                    )

                st.divider()

                if st.button(
                    "♡ Add to Wishlist",
                    key=f"wishlist_{item['id']}",
                    use_container_width=True
                ):

                    save_to_wishlist(item)

                    st.success(
                        "Product added to Wishlist!"
                    )

    else:

        st.info(
            "No online products found in demo data. "
            "You can still search on shopping platforms below."
        )

        st.subheader("🛍️ Search on Shopping Platforms")

        search_query = quote_plus(product)

        platforms = {
            "Amazon": f"https://www.amazon.in/s?k={search_query}",
            "Flipkart": f"https://www.flipkart.com/search?q={search_query}",
            "Croma": f"https://www.croma.com/searchB?q={search_query}",
            "Reliance Digital": (
                f"https://www.reliancedigital.in/search?q={search_query}"
            )
        }

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                f"[🛒 Search on Amazon]({platforms['Amazon']})"
            )

            st.markdown(
                f"[🛒 Search on Flipkart]({platforms['Flipkart']})"
            )

        with col2:

            st.markdown(
                f"[🛒 Search on Croma]({platforms['Croma']})"
            )

            st.markdown(
                f"[🛒 Search on Reliance Digital]({platforms['Reliance Digital']})"
            )

    # Product Comparison Table
    st.markdown('<div id="comparison-table"></div>', unsafe_allow_html=True)
    st.header("📊 Product Comparison Table")

    comparison_data = []

    # Online Products
    for item in online_products:

        comparison_data.append({

            "Product": item.get("name", "Unknown"),

            "Brand": item.get("brand", "Unknown"),

            "Category": item.get("category", "Unknown"),

            "Description": item.get("description", "Not Available"),

            "Seller": item.get("source", "Online Demo"),

            "Price (₹)": round(
                item.get("price_inr", 0), 2
            ),

            "Rating": item.get("rating", 0),

            "Availability": item.get(
                "availability", "Unknown"
            ),

            "Value Score": round(
                item.get("value_score", 0)
            ),

            "Rank": item.get("rank", "N/A")
        })

    # Local Shop Products
    for item in local_products:

        comparison_data.append({

            "Product": item.get("product_name", "Unknown"),

            "Brand": item.get("brand", "Not Available"),

            "Category": item.get("category", "Unknown"),

            "Description": "Not Available",

            "Seller": item.get("shop_name", "Local Shop"),

            "Price (₹)": round(
                item.get("price_inr", 0), 2
            ),

            "Rating": "Not Available",

            "Availability": item.get(
                "stock_status", "Unknown"
            ),

            "Value Score": "Not Available",

            "Rank": "Not Ranked"
        })

    # Display Interactive Comparison Table
    if comparison_data:

        comparison_df = pd.DataFrame(comparison_data)
        filter_options_df = comparison_df.copy()

        # Clear All Filters

        if st.button("🔄 Clear All Filters"):

            st.session_state["comparison_category"] = "All Categories"
            st.session_state["comparison_brand"] = "All Brands"
            st.session_state["comparison_seller"] = "All Sellers"
            st.session_state["comparison_sort"] = "Rank"

            st.session_state["comparison_search"] = ""
            st.session_state["comparison_min_rating"] = 0.0

            reset_prices = pd.to_numeric(
                filter_options_df["Price (₹)"],
                errors="coerce"
            ).dropna()

            if not reset_prices.empty:
                reset_min = float(reset_prices.min())
                reset_max = float(reset_prices.max())

                if reset_min < reset_max:
                    st.session_state["comparison_price_range"] = (
                        reset_min,
                        reset_max
                    )

            st.rerun()

        # Category-Based Filter

        categories = ["All Categories"] + sorted(
            filter_options_df["Category"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_category = st.selectbox(
            "📂 Filter by Category",
            categories,
            key="comparison_category"
        )

        if selected_category != "All Categories":
            comparison_df = comparison_df[
                comparison_df["Category"].astype(str)
                == selected_category
            ]

        # Brand-Based Filter

        brands = ["All Brands"] + sorted(
            filter_options_df["Brand"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_brand = st.selectbox(
            "🏷️ Filter by Brand",
            brands,
            key="comparison_brand"
        )

        if selected_brand != "All Brands":
            comparison_df = comparison_df[
                comparison_df["Brand"].astype(str)
                == selected_brand
            ]

        # Seller-Based Filter

        sellers = ["All Sellers"] + sorted(
            filter_options_df["Seller"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_seller = st.selectbox(
            "🏪 Filter by Seller",
            sellers,
            key="comparison_seller"
        )

        if selected_seller != "All Sellers":
            comparison_df = comparison_df[
                comparison_df["Seller"].astype(str)
                == selected_seller
            ]

        # Price Range Filter

        price_values = pd.to_numeric(
            filter_options_df["Price (₹)"],
            errors="coerce"
        ).dropna()

        if not comparison_df.empty and not price_values.empty:

            min_price = float(price_values.min())
            max_price = float(price_values.max())

            if min_price < max_price:

                selected_price = st.slider(
                    "💰 Filter by Price Range",
                    min_value=min_price,
                    max_value=max_price,
                    value=(min_price, max_price),
                    step=100.0,
                    key="comparison_price_range"
                )

                comparison_df = comparison_df[
                    pd.to_numeric(
                        comparison_df["Price (₹)"],
                        errors="coerce"
                    ).between(
                        selected_price[0],
                        selected_price[1]
                    )
                ]

            else:
                st.caption(
                    f"All matching products are priced at ₹{min_price:,.2f}"
                )

        # Minimum Rating Filter

        min_rating = 0.0

        rating_values = pd.to_numeric(
            filter_options_df["Rating"],
            errors="coerce"
        )

        if rating_values.notna().any():

            min_rating = st.slider(
                "⭐ Minimum Rating",
                min_value=0.0,
                max_value=5.0,
                value=0.0,
                step=0.5,
                key="comparison_min_rating"
            )

            if min_rating > 0:

                comparison_df = comparison_df[
                    pd.to_numeric(
                        comparison_df["Rating"],
                        errors="coerce"
                    ) >= min_rating
                ]

        # Search Filter for Comparison Table

        search_query = st.text_input(
            "🔎 Search Products in Comparison Table",
            placeholder="Search by product, brand or seller...",
            key="comparison_search"
        )

        if search_query:
            comparison_df = comparison_df[
                comparison_df.astype(str).apply(
                    lambda row: row.str.contains(
                        search_query,
                        case=False,
                        na=False,
                        regex=False
                    ).any(),
                    axis=1
                )
            ]

        # Active Filters Summary

        active_filters = []

        if selected_category != "All Categories":
            active_filters.append(f"Category: {selected_category}")

        if selected_brand != "All Brands":
            active_filters.append(f"Brand: {selected_brand}")

        if selected_seller != "All Sellers":
            active_filters.append(f"Seller: {selected_seller}")

        if min_rating > 0:
            active_filters.append(f"Minimum Rating: {min_rating}")

        if "selected_price" in locals():
            if selected_price != (min_price, max_price):
                active_filters.append(
                    f"Price: ₹{selected_price[0]:,.0f} - ₹{selected_price[1]:,.0f}"
                )

        if search_query:
            active_filters.append(f"Search: {search_query}")

        if active_filters:
            st.caption(f"🎯 {len(active_filters)} filter(s) currently applied")

            st.info(
                "🔎 Active Filters: " + " | ".join(active_filters)
            )
        else:
            st.caption("No filters applied. Showing all products.")

        # Search Results Count
        st.caption(
            f"📦 Showing {len(comparison_df)} out of "
            f"{len(filter_options_df)} products"
        )

        if comparison_df.empty:

            st.warning(
                "😕 No products match your selected filters."
            )

            st.caption(
                "Try changing your search keyword, price range, "
                "category, brand or rating filter."
            )  

        if not comparison_df.empty:

            sort_column = st.selectbox(
                "Sort Comparison Table By",
                [
                    "Rank",
                    "Price (₹)",
                    "Rating",
                    "Value Score"
                ],
                key="comparison_sort"
            )

            if sort_column == "Rank":

                comparison_df["_sort"] = pd.to_numeric(
                    comparison_df["Rank"],
                    errors="coerce"
                )

                comparison_df = comparison_df.sort_values(
                    "_sort",
                    ascending=True,
                    na_position="last"
                ).drop(columns=["_sort"])

            elif sort_column == "Rating":

                comparison_df["_sort"] = pd.to_numeric(
                    comparison_df["Rating"],
                    errors="coerce"
                )

                comparison_df = comparison_df.sort_values(
                    "_sort",
                    ascending=False,
                    na_position="last"
                ).drop(columns=["_sort"])

            elif sort_column == "Value Score":

                comparison_df["_sort"] = pd.to_numeric(
                    comparison_df["Value Score"],
                    errors="coerce"
                )

                comparison_df = comparison_df.sort_values(
                    "_sort",
                    ascending=False,
                    na_position="last"
                ).drop(columns=["_sort"])

            else:

                comparison_df = comparison_df.sort_values(
                    "Price (₹)",
                    ascending=True
                )

            # Highlight Best Ranked Product

            best_product = comparison_df[
                comparison_df["Rank"] == 1
            ]

            if not best_product.empty:

                st.success(
                    f"🏆 Best Product: "
                    f"{best_product.iloc[0]['Product']}"
                )

                st.caption(
                    "Rank 1 product is selected based on Smart Value Score."
                )

            # Product Comparison Summary

            st.markdown("### 📋 Product Comparison Summary")

            total_products = len(comparison_df)

            st.write(
                f"**Total Products Compared:** {total_products}"
            )

            col1, col2, col3 = st.columns(3)

            # Cheapest Price

            with col1:

                cheapest_price = comparison_df["Price (₹)"].min()

                st.metric(
                    "💰 Cheapest Price",
                    f"₹{cheapest_price:,.2f}"
                )

            # Highest Rating

            with col2:

                rating_values = pd.to_numeric(
                    comparison_df["Rating"],
                    errors="coerce"
                ).dropna()

                highest_rating = (
                    f"{rating_values.max():.1f}/5"
                    if not rating_values.empty
                    else "N/A"
                )

                st.metric(
                    "⭐ Highest Rating",
                    highest_rating
                )

            # Best Value Score

            with col3:

                score_values = pd.to_numeric(
                    comparison_df["Value Score"],
                    errors="coerce"
                ).dropna()

                highest_score = (
                    f"{score_values.max():.0f}/100"
                    if not score_values.empty
                    else "N/A"
                )

                st.metric(
                    "🏆 Best Value Score",
                    highest_score
                )

            # Display Comparison Table

            st.dataframe(
                comparison_df.style.apply(
                    lambda row: [
                        "background-color: #d1fae5; color: #065f46; font-weight: bold"
                        if row["Rank"] == 1
                        else ""
                        for _ in row
                    ],
                    axis=1
                ),
                use_container_width=True,
                hide_index=True
            )

        # Download Comparison Report

        csv_data = comparison_df.to_csv(
            index=False,
            encoding="utf-8-sig"
        ).encode("utf-8-sig")

        st.download_button(
            label="📥 Download Comparison Report",
            data=csv_data,
            file_name="BuyWise_Product_Comparison.csv",
            mime="text/csv"
        )

        # Ranking Legend

        st.markdown("### 🏅 Ranking Guide")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.success("🥇 Rank 1 - Best Value")

        with col2:
            st.info("🥈 Rank 2 - Second Best")

        with col3:
            st.info("🥉 Rank 3 - Third Best")

        st.caption(
            "Rankings are based on Smart Value Score. "
            "Local shop listings are not ranked."
        )

        # Potential Savings

        st.markdown("### 💰 Price Difference")

        prices = pd.to_numeric(
            comparison_df["Price (₹)"],
            errors="coerce"
        ).dropna()

        if len(prices) >= 2:

            savings = prices.max() - prices.min()

            st.metric(
                "Difference Between Highest and Lowest Price",
                f"₹{savings:,.2f}"
            )

        else:
            st.caption(
                "At least two products are required to calculate the price difference."
            )

        # Lowest Price

        if not comparison_df.empty:

            valid_prices = pd.to_numeric(
                comparison_df["Price (₹)"],
                errors="coerce"
            ).dropna()

            if not valid_prices.empty:

                cheapest_index = valid_prices.idxmin()

                cheapest_product = comparison_df.loc[
                    cheapest_index
                ]

                st.success(
                    f"💰 Lowest Price: ₹{cheapest_product['Price (₹)']:,.2f} "
                    f"at {cheapest_product['Seller']}"
                )

            else:

                st.caption("No valid prices available.")

        else:

            st.caption("No products available after applying filters.")

    else:

        st.info(
            "No products available for comparison."
        )


    # Price History Tracker
    st.markdown('<div id="price-history"></div>', unsafe_allow_html=True)
    st.header("📈 Product Price History")

    st.caption(
        "Compare product prices, ratings, availability and smart value scores. "
        "Rankings are calculated using price and rating."
    )

    if online_products:

        selected_product = st.selectbox(
            "Select a product to view price history",
            [item["name"] for item in online_products],
            key="price_history_product"
        )

        history = get_price_history(selected_product)

        if history:

            history_data = [
                {
                    "Checked At": row[2],
                    "Price (₹)": row[1]
                }
                for row in history
            ]

            history_df = pd.DataFrame(history_data)

            history_df["Checked At"] = pd.to_datetime(
                history_df["Checked At"]
            )

            history_df = history_df.sort_values("Checked At")

            st.line_chart(
                history_df.set_index("Checked At")["Price (₹)"]
            )

            st.dataframe(
                history_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No price history available for this product yet."
            )

    else:

        st.info("Search for a product to view its price history.")

    # Price Drop Alert

    st.divider()
    st.markdown(
        '<div id="price-alerts"></div>',
        unsafe_allow_html=True
    )
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
            "Search for a product first to set a price alert."
        )

    # Display Saved Price Alerts

    saved_alerts = get_price_alerts()

    if saved_alerts:

        st.subheader("📋 Your Saved Alerts")

        current_products = {
            item["name"]: item
            for item in online_products
        }

        for product_name, target_price, created_at in saved_alerts:

            st.write(f"**{product_name}**")
            st.write(
                f"Target Price: ₹{target_price:,.2f}"
            )

            current_item = current_products.get(
                product_name
            )

            if current_item:

                latest_price = current_item["price_inr"]

                if latest_price <= target_price:

                    st.success(
                        f"🎉 Target reached! Current price: "
                        f"₹{latest_price:,.2f}"
                    )

                else:

                    st.info(
                        f"Current price: ₹{latest_price:,.2f}. "
                        f"Waiting for price drop."
                    )

            else:

                st.caption(
                    "Search this product again to check its current price."
                )

            st.caption(f"Alert created: {created_at}")
            st.divider()

        # Remove Price Alert

        st.subheader("🗑️ Manage Price Alerts")

        alert_to_remove = st.selectbox(
            "Select an alert to remove",
            [alert[0] for alert in saved_alerts],
            key="remove_alert_select"
        )

        if st.button(
            "Remove Selected Alert",
            key="remove_alert_button"
        ):

            remove_price_alert(alert_to_remove)

            st.success("Price alert removed successfully!")

    else:

        st.info("You have no saved price alerts yet.")


    # Local Offline Shops
    st.markdown('<div id="local-shops"></div>', unsafe_allow_html=True)
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
st.markdown('<div id="same-product"></div>', unsafe_allow_html=True)
st.header("🔍 Same Product Comparison")

st.caption(
    "Search a product separately to compare its online "
    "and local shop prices."
)

# Separate Product Search

same_search_query = st.text_input(
    "Enter Product Name",
    placeholder="Example: Samsung Galaxy S24",
    key="same_product_search"
)

same_search_city = st.text_input(
    "Enter City",
    value="Jind",
    key="same_product_city"
)

if st.button(
    "🔍 Compare Product Prices",
    key="same_product_search_button"
):

    if not same_search_query.strip():

        st.warning("Please enter a product name.")

    else:

        with st.spinner("Searching online and local shops..."):

            same_online_results = search_products(
                same_search_query
            )

            same_local_results = search_local_shops(
                same_search_query,
                same_search_city
            )

            comparison_matches = find_same_products(
                same_online_results,
                same_local_results
            )

            st.session_state["same_product_online_results"]=(
                same_online_results
            )

            st.session_state["same_product_matches"] = (
                comparison_matches
            )

            st.session_state["same_product_local_results"] = (
                same_local_results
            )

            st.session_state["same_product_searched"] = True

# Display Search Results

if st.session_state.get("same_product_searched", False):

    comparison_matches = st.session_state.get(
        "same_product_matches", []
    )

    if comparison_matches:

        st.caption(
            "Online prices use DummyJSON demo data converted to INR. "
            "Local shop prices are sample entries, not verified live prices."
        )

        for item in comparison_matches:

            with st.container(border=True):

                st.subheader(item["product"])

                col1, col2 = st.columns(2)

                with col1:

                    st.write("🌐 Online Store")

                    online_inr = (
                        item["online_price"] * USD_TO_INR
                    )

                    st.write(f"Price: ₹{online_inr:,.2f}")

                with col2:

                    st.write("🏪 Local Shop")

                    st.write(f"Shop: {item['local_shop']}")

                    st.write(
                        f"Price: ₹{item['local_price']:,.0f}"
                    )

                local_inr = item["local_price"]

                difference = abs(online_inr - local_inr)

                if online_inr < local_inr:

                    st.success("🏆 Online Shopping is Cheaper!")

                    st.write(
                        f"You save ₹{difference:,.2f} online."
                    )

                elif local_inr < online_inr:

                    st.success("🏆 Local Shop is Cheaper!")

                    st.write(
                        f"You save ₹{difference:,.2f} locally."
                    )

                else:

                    st.info(
                        "Both options have the same price."
                    )

    else:

        local_results = st.session_state.get(
            "same_product_local_results", []
        )

        if local_results:

            st.info(
                "No exact online match found. Showing available local shops."
            )

            st.subheader("🏪 Available Local Shop Products")

            st.caption(
                "Explore products listed by local shops in your city."
            )

            for item in local_results:

                with st.container(border=True):

                    col1, col2 = st.columns([2, 1])

                    with col1:

                        st.markdown(
                            f"### {item.get('product_name', 'Unknown')}"
                        )

                        st.write(
                            f"🏪 **{item.get('shop_name', 'Unknown')}**"
                        )

                        st.caption(
                            f"📍 {item.get('city', 'Unknown')}"
                        )

                    with col2:

                        st.metric(
                            "Listed Price",
                            f"₹{item.get('price_inr', 0):,.2f}"
                        )

                        stock = item.get(
                            'stock_status', 'Unknown'
                        )

                        st.caption(
                            f"📦 Availability: {stock}"
                        )

        else:

            st.info(
                "No exact online and local product match found."
            )

        online_results = st.session_state.get(
            "same_product_online_results", []
        )

        if online_results:

            st.subheader("🌐 Online Alternative Products")

            st.caption(
                "These are alternatives, not verified exact matches."
            )

            for item in online_results[:5]:

                with st.container(border=True):

                    st.write(
                        f"**{item.get('name', 'Unknown')}**"
                    )

                    st.write(
                        f"Brand: {item.get('brand', 'Unknown')}"
                    )

                    online_price = (
                        float(item.get("price", 0)) * USD_TO_INR
                    )

                    st.write(
                        f"Demo Price: ₹{online_price:,.2f}"
                    )

                    st.write(
                        f"Rating: {item.get('rating', 0)} / 5"
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
st.markdown('<div id="ai-assistant"></div>', unsafe_allow_html=True)
st.header("🤖 AI Shopping Assistant")

st.write(
    "Ask questions and get smart shopping recommendations."
)

user_question = st.text_area(
    "🤖 Tell BuyWise AI what you need",
    placeholder=(
        "Example: I need a laptop under ₹50,000 "
        "for MCA, Python programming and AI development. "
        "Compare performance, RAM, storage and value for money."
    ),
    height=100
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
        You are BuyWise AI, an intelligent shopping recommendation
        engine.

        Your job is to help users make smart and cost-effective
        purchasing decisions.

        ONLINE PRODUCTS:
        {online_data[:10]}

        LOCAL SHOP PRODUCTS:
        {local_data[:10]}

        USER REQUIREMENTS:
        {user_question}

        ANALYSIS INSTRUCTIONS:

        1. Understand the user's actual requirements and priorities.

        2. Compare available products based on:
            - Price
            - Customer rating
            - Brand
            - Product specifications
            - Availability
            - Value for money

        3. Identify the best overall option based on the user's needs.

        4. Identify the most budget-friendly option when possible.

        5. Explain the advantages and disadvantages of the
        recommended products.

        6. Compare online and local shopping options whenever
        matching products are available.

        7. If no suitable product is available, clearly explain
        why instead of making up recommendations.

        8. Never invent prices, ratings, specifications,
        discounts or availability.

        9. Online prices come from demo data and local shop
        listings are sample testing data. Clearly disclose
        this limitation.

        10. Do not automatically recommend the cheapest product.
            Consider quality, ratings and user requirements.

        11. Use the calculated value_score (0-100) to
        evaluate value for money.

        12. Consider value_score along with price, rating
        and user requirements.

        13. Explain why a product has a higher or lower
        value score whenever relevant.

        RESPONSE FORMAT:

        ### 🎯 Best Recommendation
        Name the best available product and explain why.

        ### 💰 Budget-Friendly Choice
        Suggest the most affordable suitable option.

        ### ⚖️ Product Comparison
        Compare the relevant available options.

        ### ✅ Final Verdict
        Give a clear, practical recommendation.

        Use simple, professional language.
        Base every recommendation only on the supplied data.
        """
        try:

            with st.spinner(
                "AI is analysing your shopping options..."
            ):

                st.session_state.ai_answer = get_cached_ai_answer(
                    shopping_context
                )

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
st.markdown('<div id="wishlist"></div>', unsafe_allow_html=True)
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

                st.write(f"Brand: {item[1]}")

                st.write(
                    f"Saved Price: ₹{item[2]:,.2f}"
                )

                st.caption(
                    f"Saved At: {item[4]}"
                )

                if st.button(
                    "🗑️ Remove from Wishlist",
                    key=f"remove_wishlist_{item[0]}"
                ):

                    remove_from_wishlist(item[0])

                    st.success("Product removed from Wishlist!")

                    st.rerun()

else:

    st.info(
        "Your Wishlist is empty. Add products to your Wishlist to see them here."
    )