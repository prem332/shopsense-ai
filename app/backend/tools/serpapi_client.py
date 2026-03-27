import re
from dotenv import load_dotenv

load_dotenv()


def build_product(item: dict, platform: str) -> dict:
    """
    Build standardized product dict from SerpAPI result.
    Works for Amazon, Flipkart, and Myntra results.
    """
    price_raw = item.get("price", "")
    price_num = None

    if price_raw:
        price_str = str(price_raw)

        # ✅ Remove all currency symbols and text
        price_str = price_str.replace("₹", "")
        price_str = price_str.replace("Rs.", "")
        price_str = price_str.replace("Rs", "")
        price_str = price_str.replace("INR", "")
        price_str = price_str.replace(",", "")
        price_str = price_str.strip()

        # Extract first number found
        numbers = re.findall(r'\d+\.?\d*', price_str)
        if numbers:
            try:
                price_num = float(numbers[0])
                # ✅ Sanity check — ignore unrealistic prices
                if price_num > 100000:
                    price_num = None
                if price_num <= 0:
                    price_num = None
            except Exception:
                price_num = None

    return {
        "title": item.get("title", "N/A"),
        "price": price_raw if price_raw else "Price not available",
        "price_num": price_num,
        "image": item.get("thumbnail", ""),
        "link": item.get("link", ""),
        "rating": str(item.get("rating", "N/A")),
        "platform": platform
    }


def filter_by_budget(
    products: list,
    budget_max: float
) -> list:
    """
    Filter products by max budget only.
    Note: Kept for backward compatibility.
    Main filtering now happens inside each tool.
    Products with no price are included by default.
    """
    if not budget_max or budget_max <= 0:
        return products

    return [
        p for p in products
        if p["price_num"] is None or p["price_num"] <= budget_max
    ]


def filter_by_budget_range(
    products: list,
    budget_min: float = None,
    budget_max: float = None
) -> list:
    """
    Filter products by min AND max budget range.
    Products with no price are included by default.
    """
    filtered = []

    for p in products:
        price_num = p.get("price_num")

        # Include products with unknown price
        if price_num is None:
            filtered.append(p)
            continue

        # Check min price
        if budget_min and budget_min > 0:
            if price_num < budget_min:
                continue

        # Check max price
        if budget_max and budget_max > 0:
            if price_num > budget_max:
                continue

        filtered.append(p)

    return filtered


def sort_by_price(
    products: list,
    ascending: bool = True
) -> list:
    """Sort products by price"""
    priced = [p for p in products if p.get("price_num")]
    unpriced = [p for p in products if not p.get("price_num")]

    priced.sort(
        key=lambda x: x["price_num"],
        reverse=not ascending
    )

    return priced + unpriced


def sort_by_rating(products: list) -> list:
    """Sort products by rating descending"""
    def get_rating(p):
        try:
            return float(
                str(p.get("rating", "0")).replace("N/A", "0")
            )
        except Exception:
            return 0.0

    return sorted(products, key=get_rating, reverse=True)