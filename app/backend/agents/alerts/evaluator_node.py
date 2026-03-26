from datetime import datetime
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def evaluate_conditions(
    alert: dict,
    product: dict
) -> dict:
    """
    Evaluate ALL alert conditions against a product.
    Returns evaluation result with details.
    """
    conditions_met = []
    conditions_failed = []

    # Check price condition
    if alert.get("target_price"):
        price_num = product.get("price_num")
        if price_num and price_num <= float(alert["target_price"]):
            conditions_met.append(
                f"Price ₹{price_num} ≤ ₹{alert['target_price']}"
            )
        else:
            conditions_failed.append(
                f"Price ₹{price_num} > ₹{alert['target_price']}"
            )

    # Check discount condition
    if alert.get("discount_pct"):
        # Try to extract discount from title
        title_lower = product.get("title", "").lower()
        discount_found = False
        import re
        discounts = re.findall(r'(\d+)%\s*off', title_lower)
        if discounts:
            max_discount = max([int(d) for d in discounts])
            if max_discount >= int(alert["discount_pct"]):
                conditions_met.append(
                    f"Discount {max_discount}% ≥ {alert['discount_pct']}%"
                )
                discount_found = True

        if not discount_found and alert.get("discount_pct"):
            conditions_failed.append(
                f"Discount < {alert['discount_pct']}%"
            )

    if alert.get("in_stock"):
        if product.get("price_num"):
            conditions_met.append("Product in stock")
        else:
            conditions_failed.append("Product out of stock")

    if alert.get("new_arrival"):
        title_lower = product.get("title", "").lower()
        new_keywords = ["new", "2024", "2025", "latest", "fresh"]
        if any(kw in title_lower for kw in new_keywords):
            conditions_met.append("New arrival detected")
        else:
            conditions_failed.append("Not a new arrival")

    if not any([
        alert.get("target_price"),
        alert.get("discount_pct"),
        alert.get("in_stock"),
        alert.get("new_arrival")
    ]):
        conditions_met.append("Product found")

    all_met = len(conditions_failed) == 0 and len(conditions_met) > 0

    return {
        "all_conditions_met": all_met,
        "conditions_met": conditions_met,
        "conditions_failed": conditions_failed,
        "product": product
    }


def mark_alert_triggered(alert_id: str):
    """Mark alert as triggered in database"""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                UPDATE alerts
                SET triggered_at = :triggered_at,
                    is_active = false
                WHERE id = :id
            """), {
                "id": alert_id,
                "triggered_at": datetime.now()
            })
            conn.commit()
        print(f"✅ Alert {alert_id} marked as triggered")
    except Exception as e:
        print(f"❌ Mark triggered failed: {e}")


def evaluator_node(
    alert: dict,
    current_products: list
) -> dict:
    """
    Evaluator Node:
    Checks all conditions for each product.
    Fires notification if conditions met.
    """
    print(f"📊 Evaluator Node: Evaluating {len(current_products)} products")

    triggered_product = None

    for product in current_products:
        evaluation = evaluate_conditions(alert, product)

        if evaluation["all_conditions_met"]:
            print(f"   → ✅ ALL CONDITIONS MET!")
            print(f"      Product: {product.get('title', 'N/A')[:50]}")
            print(f"      Met: {evaluation['conditions_met']}")

            triggered_product = product

            # Mark alert triggered in DB
            if alert.get("id"):
                mark_alert_triggered(str(alert["id"]))

            break
        else:
            print(f"   → ❌ Conditions not met: {evaluation['conditions_failed']}")

    return {
        "triggered": triggered_product is not None,
        "triggered_product": triggered_product,
        "alert_id": alert.get("id")
    }