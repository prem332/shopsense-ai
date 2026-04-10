import re
import pytest


# ── Budget Extraction Logic ────────────────────────────────────

BUDGET_KEYWORDS = [
    "between", "under", "below", "budget",
    "price", "rs", "rupee", "inr", "worth",
    "range", "cost", "spend", "1000", "2000",
    "3000", "4000", "5000", "6000", "7000",
    "8000", "9000", "10000", "500", "1500",
]


def extract_budget(query: str) -> dict:
    query_lower = query.lower()

    # Check if budget mentioned in chat
    chat_has_budget = any(
        word in query_lower for word in BUDGET_KEYWORDS
    )

    budget_min = 0
    budget_max = 0

    # Extract "between X and Y" pattern
    between_match = re.search(
        r'between\s+(\d+)\s+and\s+(\d+)', query_lower
    )
    if between_match:
        budget_min = float(between_match.group(1))
        budget_max = float(between_match.group(2))

    # Extract "under X" pattern
    under_match = re.search(
        r'(?:under|below|less than)\s+(?:rs\.?\s*)?(\d+)',
        query_lower
    )
    if under_match and not between_match:
        budget_max = float(under_match.group(1))

    return {
        "chat_has_budget": chat_has_budget,
        "budget_min": budget_min,
        "budget_max": budget_max,
    }


# ── Smart Select Logic ─────────────────────────────────────────

def smart_select(products: list, count: int = 5) -> list:
    priced = [p for p in products if p.get("price_num")]
    if not priced:
        return products[:count]
    if len(priced) <= count:
        return priced

    priced.sort(key=lambda x: x["price_num"])
    min_price = priced[0]["price_num"]
    max_price = priced[-1]["price_num"]
    price_range = max_price - min_price

    if price_range < 500:
        return priced[:count]

    selected = []
    band_size = price_range / count

    for i in range(count):
        band_min = min_price + (i * band_size)
        band_max = min_price + ((i + 1) * band_size)
        band = [
            p for p in priced
            if band_min <= p["price_num"] <= band_max
            and p not in selected
        ]
        if band:
            selected.append(band[0])

    if len(selected) < count:
        for p in priced:
            if p not in selected:
                selected.append(p)
            if len(selected) >= count:
                break

    return selected


# ── Tests: Budget Extraction ───────────────────────────────────

class TestBudgetExtraction:

    def test_between_pattern(self):
        result = extract_budget("blue shirt between 1500 and 6000")
        assert result["budget_min"] == 1500
        assert result["budget_max"] == 6000

    def test_under_pattern(self):
        result = extract_budget("shirt under 2000")
        assert result["budget_max"] == 2000
        assert result["budget_min"] == 0

    def test_below_pattern(self):
        result = extract_budget("kurta below 1500")
        assert result["budget_max"] == 1500

    def test_no_budget_in_query(self):
        result = extract_budget("show me blue shirts")
        assert result["chat_has_budget"] is False

    def test_budget_keyword_detected(self):
        result = extract_budget("budget under 3000")
        assert result["chat_has_budget"] is True

    def test_rs_keyword_detected(self):
        result = extract_budget("shirt for rs 1000")
        assert result["chat_has_budget"] is True

    def test_number_keyword_detected(self):
        result = extract_budget("shirt size M 2000")
        assert result["chat_has_budget"] is True


# ── Tests: Smart Select ────────────────────────────────────────

class TestSmartSelect:

    def make_products(self, prices):
        return [
            {"title": f"Product {p}", "price_num": p}
            for p in prices
        ]

    def test_returns_correct_count(self):
        products = self.make_products(
            [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        )
        result = smart_select(products, count=5)
        assert len(result) == 5

    def test_less_than_count_returns_all(self):
        products = self.make_products([100, 200, 300])
        result = smart_select(products, count=5)
        assert len(result) == 3

    def test_empty_products(self):
        result = smart_select([])
        assert result == []

    def test_no_price_num_products(self):
        products = [
            {"title": "Product A"},
            {"title": "Product B"},
        ]
        result = smart_select(products, count=5)
        assert len(result) == 2

    def test_spread_across_price_range(self):
        products = self.make_products(
            [100, 200, 300, 400, 500,
             600, 700, 800, 900, 1000]
        )
        result = smart_select(products, count=5)
        prices = [p["price_num"] for p in result]
        # Should have products from different price ranges
        assert min(prices) < 500
        assert max(prices) > 500

    def test_filters_no_price_products(self):
        products = [
            {"title": "A", "price_num": 500},
            {"title": "B"},
            {"title": "C", "price_num": 1000},
        ]
        result = smart_select(products, count=5)
        assert all(p.get("price_num") for p in result)