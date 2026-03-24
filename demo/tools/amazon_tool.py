import os
import re
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()


def search_amazon(query: str, budget_max: float = None) -> list:
    print(f"🔍 Searching Amazon for: {query}")

    params = {
        "engine": "amazon",
        "amazon_domain": "amazon.in",
        "k": query,
        "api_key": os.getenv("SERPAPI_KEY")
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    products = []

    organic = results.get("organic_results", [])

    for item in organic[:10]:
        try:
            price_raw = item.get("price", "")
            price_num = None

            if price_raw:
                price_str = str(price_raw).replace(
                    "₹", ""
                ).replace(",", "").strip()
                numbers = re.findall(r'\d+\.?\d*', price_str)
                if numbers:
                    price_num = float(numbers[0])

            if budget_max and price_num and price_num > budget_max:
                continue

            product = {
                "title": item.get("title", "N/A"),
                "price": price_raw if price_raw else "Price not available",
                "price_num": price_num,
                "image": item.get("thumbnail", ""),
                "link": item.get("link", ""),
                "rating": item.get("rating", "N/A"),
                "platform": "Amazon"
            }

            if product["title"] != "N/A":
                products.append(product)

        except Exception as e:
            print(f"⚠️ Skipping product: {e}")
            continue

    print(f"✅ Found {len(products)} products on Amazon")
    return products[:5]