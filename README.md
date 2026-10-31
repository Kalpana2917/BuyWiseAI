🛍️ BuyWise AI

One Search. Every Shopping Option.

BuyWise AI is a smart shopping comparison application developed using Python and Streamlit. It helps users compare online products with local shop listings, track prices, manage wishlists, and get AI-powered shopping suggestions.

Features

- Online product search
- Local shop product listings
- Online vs local price comparison
- Similar product matching
- Budget, rating and category filters
- Cheapest, highest-rated and best-value recommendations
- Wishlist management
- Price history tracking
- Price alerts
- Gemini AI Shopping Assistant

Technologies Used

- Python
- Streamlit
- SQLite
- Google Gemini API
- Requests
- CSV

Project Structure

BuyWiseAI/
│
├── app.py
├── product_api.py
├── local_shop_api.py
├── product_matcher.py
├── price_comparator.py
├── price_tracker.py
├── requirements.txt
├── data/
│   └── local_shops.csv
├── .gitignore
└── README.md

Installation

1. Clone the repository:

git clone YOUR_REPOSITORY_URL

2. Open the project folder:

cd BuyWiseAI

3. Install dependencies:

pip install -r requirements.txt

4. Create ".streamlit/secrets.toml" and add your Gemini API key:

GEMINI_API_KEY = "YOUR_API_KEY"

5. Run the application:

streamlit run app.py

Important Security Note

Never upload your ".streamlit/secrets.toml" file or API key to GitHub.

Current Limitations

- Online product results use DummyJSON test data.
- Local shop listings are sample data.
- Price alerts are checked during searches, not through continuous background monitoring.
- Product matching and value recommendations use rule-based logic.

Project Objective

To simplify shopping by bringing online and local product comparisons together in one platform.

Developer

Kalpana Singhmar