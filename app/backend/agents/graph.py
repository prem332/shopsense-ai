import os
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from app.backend.agents.state import ShopSenseState

load_dotenv()


def guardrails_node(state: ShopSenseState) -> ShopSenseState:
    """Sprint 3 — Full Guardrails Agent"""
    print("🛡️  Guardrails Node: Validating input...")
    return {**state, "is_valid": True}


def intent_classifier_node(state: ShopSenseState) -> ShopSenseState:
    """Sprint 2 — Intent Classification"""
    print("🧭  Intent Classifier: Detecting intent...")
    query = state.get("user_query", "").lower()
    alert_keywords = [
        "alert", "notify", "notification",
        "when price", "drops to", "below",
        "inform me", "let me know"
    ]
    intent = "alert" if any(
        word in query for word in alert_keywords
    ) else "recommendation"
    print(f"   → Intent: {intent}")
    return {**state, "intent": intent}


def preference_node(state: ShopSenseState) -> ShopSenseState:
    """Sprint 3 — Full Preference Agent"""
    print("🧠  Preference Node: [STUB]")
    return {**state, "category": "shirts"}


def search_node(state: ShopSenseState) -> ShopSenseState:
    """Sprint 3 — Full Search & Rank Agent"""
    print("🔍  Search Node: [STUB]")
    return {
        **state,
        "ranked_products": [],
        "final_response": "Search coming in Sprint 3!"
    }


def alert_node(state: ShopSenseState) -> ShopSenseState:
    """Sprint 4 — Full Alert Agent"""
    print("🔔  Alert Node: [STUB]")
    return {
        **state,
        "alert_id": "stub-alert-001",
        "final_response": "Alert system coming in Sprint 4!"
    }


def route_by_validity(state: ShopSenseState) -> str:
    if not state.get("is_valid", True):
        return END
    return "intent_classifier_node"


def route_by_intent(state: ShopSenseState) -> str:
    intent = state.get("intent", "recommendation")
    return "alert_node" if intent == "alert" else "preference_node"


def create_graph():
    print("🔧  Building ShopSense LangGraph...")

    graph = StateGraph(ShopSenseState)

    graph.add_node("guardrails_node", guardrails_node)
    graph.add_node("intent_classifier_node", intent_classifier_node)
    graph.add_node("preference_node", preference_node)
    graph.add_node("search_node", search_node)
    graph.add_node("alert_node", alert_node)

    graph.set_entry_point("guardrails_node")

    graph.add_conditional_edges(
        "guardrails_node",
        route_by_validity,
        {
            "intent_classifier_node": "intent_classifier_node",
            END: END
        }
    )

    graph.add_conditional_edges(
        "intent_classifier_node",
        route_by_intent,
        {
            "preference_node": "preference_node",
            "alert_node": "alert_node"
        }
    )

    graph.add_edge("preference_node", "search_node")
    graph.add_edge("search_node", END)
    graph.add_edge("alert_node", END)

    app = graph.compile()
    print("✅  LangGraph compiled!")
    return app


shopping_graph = create_graph()