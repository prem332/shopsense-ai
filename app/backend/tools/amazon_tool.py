import os
from serpapi import GoogleSearch
from app.backend.tools.serpapi_client import build_product
from dotenv import load_dotenv

load_dotenv()


def smart_select(
    products: list,
    budget_min: float = None,
    budget_max: float = None,
    count: int = 10
) -> list:
    """Spread selection across full price range"""
    if len(products) <= count:
        return products

    priced = [p for p in products if p.get("price_num")]

    if not priced:
        return products[:count]

    priced.sort(key=lambda x: x["price_num"])

    min_price = priced[0]["price_num"]
    max_price = priced[-1]["price_num"]
    price_range = max_price - min_price

    print(f"   → Price range in results: ₹{min_price} — ₹{max_price}")

    if price_range < 500:
        return priced[:count]

    selected = []
    band_size = price_range / count

    for i in range(count):
        band_min = min_price + (i * band_size)
        band_max = min_price + ((i + 1) * band_size)

        band_products = [
            p for p in priced
            if band_min <= p["price_num"] <= band_max
            and p not in selected
        ]

        if band_products:
            band_products.sort(
                key=lambda x: float(
                    str(x.get("rating", "0")).replace("N/A", "0")
                ),
                reverse=True
            )
            selected.append(band_products[0])

    if len(selected) < count:
        for p in priced:
            if p not in selected:
                selected.append(p)
            if len(selected) >= count:
                break

    print(
        f"   → Smart selected prices: "
        f"{[p['price_num'] for p in selected]}"
    )
    return selected


def search_amazon(
    query: str,
    budget_min: float = None,
    budget_max: float = None
) -> list:
    print(f"🛒 Amazon: searching '{query}'")

    # ✅ No min_price/max_price API params
    # amazon.in does not support them reliably
    # Post-filtering is done after fetching results
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
        print(f"   → Raw results from Amazon: {len(items)}")

        all_products = []
        for item in items:
            p = build_product(item, "Amazon")
            if p["title"] == "N/A":
                continue

            price_num = p.get("price_num")

            # Skip products with no price when budget is set
            if price_num is None:
                if not budget_min and not budget_max:
                    all_products.append(p)
                continue

            # Post-filter by min price
            if budget_min and budget_min > 0:
                if price_num < budget_min:
                    continue

            # Post-filter by max price
            if budget_max and budget_max > 0:
                if price_num > budget_max:
                    continue

            all_products.append(p)

        print(f"   → Products in budget range: {len(all_products)}")

        if not all_products:
            print(f"   → Found 0 on Amazon after budget filter")
            return []

        final_products = smart_select(
            all_products, budget_min, budget_max
        )

        print(f"   → Found {len(final_products)} on Amazon")
        return final_products

    except Exception as e:
        print(f"   → Amazon error: {e}")
        return []