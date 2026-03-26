import os
import re
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()


def check_product_price(
    alert: dict,
    platform: str = "amazon"
) -> list:
    """
    Check current price/stock for a product on a platform.
    Returns list of matching products with current data.
    """
    # Build search query from alert
    query_parts = []
    if alert.get("brand"):
        query_parts.append(alert["brand"])
    if alert.get("color"):
        query_parts.append(alert["color"])
    if alert.get("product_name"):
        query_parts.append(alert["product_name"])
    if alert.get("size"):
        query_parts.append(f"size {alert['size']}")

    query = " ".join(query_parts) if query_parts else "product"
    print(f"   → Checking: {query} on {platform}")

    params = {
        "api_key": os.getenv("SERPAPI_KEY"),
        "k": query
    }

    if platform == "amazon":
        params["engine"] = "amazon"
        params["amazon_domain"] = "amazon.in"
    else:
        params["engine"] = "google_shopping"
        params["q"] = f"{query} site:{platform}.com"
        params["gl"] = "in"
        params["hl"] = "en"

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        items = results.get("organic_results", []) or \
                results.get("shopping_results", [])

        products = []
        for item in items[:5]:
            price_raw = item.get("price", "")
            price_num = None

            if price_raw:
                price_str = str(price_raw).replace(
                    "₹", ""
                ).replace(",", "").strip()
                numbers = re.findall(r'\d+\.?\d*', price_str)
                if numbers:
                    price_num = float(numbers[0])

            products.append({
                "title": item.get("title", "N/A"),
                "price": price_raw or "N/A",
                "price_num": price_num,
                "link": item.get("link", ""),
                "image": item.get("thumbnail", ""),
                "rating": str(item.get("rating", "N/A")),
                "platform": platform.title()
            })

        return products

    except Exception as e:
        print(f"   → {platform} check error: {e}")
        return []


def checker_node(alert: dict) -> dict:
    """
    Checker Node:
    Polls all platforms in the alert for current product data.
    """
    print(f"🔍 Checker Node: Checking alert {alert.get('id')}")

    platforms = alert.get(
        "platform",
        ["amazon", "flipkart", "myntra"]
    )

    all_products = []
    for platform in platforms:
        products = check_product_price(alert, platform)
        all_products.extend(products)

    print(f"   → Found {len(all_products)} products to evaluate")

    return {
        "alert_id": alert.get("id"),
        "current_products": all_products,
        "alert": alert
    }