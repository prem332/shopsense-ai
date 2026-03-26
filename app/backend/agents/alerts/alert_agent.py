from app.backend.agents.alerts.registration_node import registration_node
from app.backend.agents.alerts.checker_node import checker_node
from app.backend.agents.alerts.evaluator_node import evaluator_node
from app.backend.notifications.notifier import notifier


def run_alert_registration(
    user_id: str,
    user_query: str
) -> dict:
    """
    Run full alert registration flow:
    1. Extract conditions from query
    2. Save to Supabase
    3. Return alert details
    """
    print("\n🔔 Alert Agent: Starting registration...")

    result = registration_node(user_id, user_query)

    print(f"✅ Alert Agent: Registration complete — {result['alert_id']}")

    return result


def run_alert_check(alert: dict) -> dict:
    """
    Run full alert check flow:
    1. Fetch current prices via SerpAPI
    2. Evaluate all conditions
    3. Fire notification if conditions met
    """
    print(f"\n🔍 Alert Agent: Checking alert {alert.get('id')}")

    # Check current prices
    check_result = checker_node(alert)

    # Evaluate conditions
    eval_result = evaluator_node(
        alert=alert,
        current_products=check_result["current_products"]
    )

    # Fire notification if triggered
    if eval_result["triggered"] and eval_result["triggered_product"]:
        notifier.notify(
            alert=alert,
            product=eval_result["triggered_product"]
        )
        print(f"✅ Alert fired for: {eval_result['triggered_product'].get('title', 'N/A')[:50]}")

    return eval_result