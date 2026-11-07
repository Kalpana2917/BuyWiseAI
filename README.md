🛍️ BuyWise AI

One Search. Every Shopping Option.

BuyWise AI is an AI-powered shopping comparison platform designed to help users make smarter purchasing decisions by comparing online product options and locally listed shop products in one place.

Instead of checking multiple platforms manually, users can explore product information, compare prices, evaluate value for money, and track product prices through a single interface.

🚀 Live Demo

"Open BuyWise AI" (https://buywiseai-gmkhqexig7sgzd4vyak4y8.streamlit.app/)

💡 Problem Statement

Online shoppers often spend considerable time comparing prices, product ratings, and specifications across different shopping platforms. Local shop options are also difficult to compare with online listings.

BuyWise AI aims to simplify this process by bringing product discovery, comparison, and price tracking together.

✨ Key Features

- Product Search: Search for products through an easy-to-use interface.
- Online Shopping Comparison: Explore online product results and compare prices and ratings.
- Local Shop Discovery: View locally stored shop listings and compare their prices.
- Same Product Comparison: Compare matching online and local products.
- Smart Value Score: Evaluate products using price and rating-based scoring.
- Product Ranking: Identify products with better value scores.
- Advanced Filters: Filter by category, brand, seller, rating, and price.
- Sorting: Sort products by price, rating, rank, and value score.
- AI Shopping Assistant: Get shopping-related assistance using Google Gemini.
- Price History Tracker: View previously recorded product prices.
- Wishlist: Save products for later.
- Price Drop Alerts: Set target prices and check whether saved products meet those targets.

🧠 Technology Stack

Technology| Purpose
Python| Core programming
Streamlit| Web application
Pandas| Data processing
SQLite| Price history, wishlist and alerts
Google Gemini API| AI shopping assistant
DummyJSON API| Demo online product data
HTML and CSS| UI customization
Git and GitHub| Version control

🏗️ Project Structure

BuyWiseAI/
│
├── app.py
├── product_api.py
├── local_shop_api.py
├── product_matcher.py
├── price_comparator.py
├── price_tracker.py
│
├── data/
│   └── local_shops.csv
│
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml
│
├── requirements.txt
├── README.md
└── .gitignore

⚙️ Installation and Setup

1. Clone the repository

git clone https://github.com/Kalpana2917/BuyWiseAI.git

2. Open the project directory

cd BuyWiseAI

3. Install dependencies

pip install -r requirements.txt

4. Configure Gemini API Key

Create ".streamlit/secrets.toml" and add:

GEMINI_API_KEY = "your_gemini_api_key"

Never upload your API key or secrets file to GitHub.

5. Run the application

streamlit run app.py

🔍 How It Works

1. Enter a product name and shopping preferences.
2. Explore available online and local shop listings.
3. Compare prices, ratings, and value scores.
4. Review matching products and alternatives.
5. Save products to your wishlist.
6. Track recorded prices and set target-price alerts.
7. Use the AI assistant for shopping-related guidance.

⚠️ Data Transparency

BuyWise AI is currently a working prototype.

- Online product information is sourced from DummyJSON demo data.
- Online demo prices are converted from USD to INR for display.
- Local shop listings are sample entries stored in a CSV file.
- Shopping platform links redirect users to product search pages.
- Live Amazon, Flipkart, and local retailer inventory and pricing integrations are not yet implemented.
- Price alerts are checked when the application has current product data available. They are not background push notifications.

🔮 Future Scope

- Live marketplace integrations.
- Verified local retailer listings.
- More accurate product matching.
- AI-based personalized recommendations.
- Real-time price monitoring and notifications.
- Secure shopping and payment integrations.

👩‍💻 Developer

Kalpana

- GitHub: "Kalpana2917" (https://github.com/Kalpana2917)
- LinkedIn: "Kalpana Singhmar" (https://www.linkedin.com/in/kalpana-singhmar/)

---

BuyWise AI: Making smarter shopping decisions simpler.
