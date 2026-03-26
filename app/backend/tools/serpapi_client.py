import os
import re
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()


def build_product(item: dict, platform: str) -> dict:
    """Build standardized product dict from SerpAPI result"""
    price_raw = item.get("price", "")
    price_num = None

    if price_raw:
        price_str = str(price_raw).replace(
            "₹", ""
        ).replace(",", "").strip()
        numbers = re.findall(r'\d+\.?\d*', price_str)
        if numbers:
            price_num = float(numbers[0])

    return {
        "title": item.get("title", "N/A"),
        "price": price_raw if price_raw else "Price not available",
        "price_num": price_num,
        "image": item.get("thumbnail", ""),
        "link": item.get("link", ""),
        "rating": str(item.get("rating", "N/A")),
        "platform": platform
    }


def filter_by_budget(products: list, budget_max: float) -> list:
    """Filter products by budget"""
    if not budget_max:
        return products
    return [
        p for p in products
        if p["price_num"] is None or p["price_num"] <= budget_max
    ]