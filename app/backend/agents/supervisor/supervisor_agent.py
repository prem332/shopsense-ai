import os
from app.backend.a2a.client.supervisor_client import supervisor_client
from app.backend.agents.state import ShopSenseState
from dotenv import load_dotenv

load_dotenv()


async def run_supervisor(state: ShopSenseState) -> ShopSenseState:
    """
    Supervisor Agent — A2A CLIENT
    Orchestrates all agents via A2A protocol
    """
    print("\n🎯  Supervisor: Starting orchestration...")
    user_query = state.get("user_query", "")

    #Guardrails via A2A
    print("📡  A2A → GuardrailsAgent: validate_input")
    guardrails_result = await supervisor_client.delegate_task(
        agent_name="GuardrailsAgent",
        skill_id="validate_input",
        payload={"user_query": user_query}
    )

    is_valid = guardrails_result.get("is_valid", True)
    if not is_valid:
        return {
            **state,
            "is_valid": False,
            "rejection_reason": guardrails_result.get("rejection_reason"),
            "final_response": "❌ " + guardrails_result.get(
                "rejection_reason", "Invalid query"
            )
        }

    # Get intent from state
    intent = state.get("intent", "recommendation")

    if intent == "recommendation":
        # Preference extraction via A2A
        print("📡  A2A → PreferenceAgent: extract_preferences")
        pref_result = await supervisor_client.delegate_task(
            agent_name="PreferenceAgent",
            skill_id="extract_preferences",
            payload={"user_query": user_query}
        )

        preferences = pref_result.get("preferences", {})

        print("📡  A2A → SearchRankAgent: search_products")
        search_result = await supervisor_client.delegate_task(
            agent_name="SearchRankAgent",
            skill_id="search_products",
            payload={
                "preferences": preferences,
                "user_query": user_query
            }
        )

        products = search_result.get("products", [])

        print("📡  A2A → SearchRankAgent: rank_products")
        rank_result = await supervisor_client.delegate_task(
            agent_name="SearchRankAgent",
            skill_id="rank_products",
            payload={
                "products": products,
                "preferences": preferences
            }
        )

        ranked = rank_result.get("ranked_products", [])
        print(f"✅  Supervisor: Got {len(ranked)} ranked products")

        return {
            **state,
            "is_valid": True,
            "category": preferences.get("category"),
            "color": preferences.get("color"),
            "size": preferences.get("size"),
            "occasion": preferences.get("occasion"),
            "budget_max": preferences.get("budget_max"),
            "brand": preferences.get("brand"),
            "ranked_products": ranked,
            "final_response": f"Found {len(ranked)} products!"
        }

    elif intent == "alert":
        # Alert registration via A2A
        print("📡  A2A → AlertAgent: register_alert")
        alert_result = await supervisor_client.delegate_task(
            agent_name="AlertAgent",
            skill_id="register_alert",
            payload={
                "user_query": user_query,
                "user_id": state.get("user_id", "guest")
            }
        )

        return {
            **state,
            "is_valid": True,
            "alert_id": alert_result.get("alert_id"),
            "final_response": "✅ Alert registered! We'll notify you when conditions are met."
        }

    return {**state, "final_response": "Request processed!"}