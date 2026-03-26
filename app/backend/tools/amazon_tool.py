import os
from serpapi import GoogleSearch
from app.backend.tools.serpapi_client import build_product, filter_by_budget
from dotenv import load_dotenv

load_dotenv()


def search_amazon(query: str, budget_max: float = None) -> list:
    print(f"🛒 Amazon: searching '{query}'")

    params = {
        "engine": "amazon",
        "amazon_domain": "amazon.in",
        "k": query,
        "api_key": os.getenv("SERPAPI_KEY")
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        items = results.get("organic_results", [])

        products = []
        for item in items[:8]:
            p = build_product(item, "Amazon")
            if p["title"] != "N/A":
                products.append(p)

        if budget_max:
            products = filter_by_budget(products, budget_max)

        print(f"   → Found {len(products)} on Amazon")
        return products[:5]

    except Exception as e:
        print(f"   → Amazon error: {e}")
        return []