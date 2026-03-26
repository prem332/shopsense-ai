import os
from serpapi import GoogleSearch
from app.backend.tools.serpapi_client import build_product, filter_by_budget
from dotenv import load_dotenv

load_dotenv()


def search_flipkart(query: str, budget_max: float = None) -> list:
    print(f"🛒 Flipkart: searching '{query}'")

    params = {
        "engine": "google_shopping",
        "q": f"{query} site:flipkart.com",
        "gl": "in",
        "hl": "en",
        "api_key": os.getenv("SERPAPI_KEY")
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        items = results.get("shopping_results", [])

        products = []
        for item in items[:8]:
            p = build_product(item, "Flipkart")
            if p["title"] != "N/A":
                products.append(p)

        if budget_max:
            products = filter_by_budget(products, budget_max)

        print(f"   → Found {len(products)} on Flipkart")
        return products[:5]

    except Exception as e:
        print(f"   → Flipkart error: {e}")
        return []