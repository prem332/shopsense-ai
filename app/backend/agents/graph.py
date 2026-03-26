import os
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from app.backend.agents.state import ShopSenseState

load_dotenv()


def guardrails_node(state: ShopSenseState) -> ShopSenseState:
    print("🛡️  Guardrails Node: Validating input...")
    query = state.get("user_query", "").lower()

    shopping_keywords = [
        "shirt", "pants", "shoes", "watch", "dress",
        "buy", "price", "brand", "size", "color",
        "formal", "casual", "budget", "under", "alert",
        "notify", "discount", "offer", "accessories"
    ]

    is_valid = any(word in query for word in shopping_keywords)

    if not is_valid:
        print("   → ❌ Invalid — not shopping related")
        return {
            **state,
            "is_valid": False,
            "rejection_reason": "Query is not shopping related",
            "final_response": "❌ Please ask about shopping products only!"
        }

    print("   → ✅ Valid shopping query")
    return {**state, "is_valid": True}


def intent_classifier_node(state: ShopSenseState) -> ShopSenseState:
    print("🧭  Intent Classifier: Detecting intent...")
    query = state.get("user_query", "").lower()

    alert_keywords = [
        "alert", "notify", "notification",
        "when price", "drops to", "below",
        "inform me", "let me know", "tell me when",
        "set alert", "price alert", "stock alert",
        "remind me", "watch price"
    ]

    intent = "alert" if any(
        word in query for word in alert_keywords
    ) else "recommendation"

    print(f"   → Intent detected: {intent}")
    return {**state, "intent": intent}

async def supervisor_node(state: ShopSenseState) -> ShopSenseState:
    from app.backend.agents.supervisor.supervisor_agent import run_supervisor
    return await run_supervisor(state)

def route_by_validity(state: ShopSenseState) -> str:
    if not state.get("is_valid", True):
        print("   → Routing to END (invalid query)")
        return END
    print("   → Routing to intent_classifier")
    return "intent_classifier_node"


def route_after_intent(state: ShopSenseState) -> str:
    print("   → Routing to supervisor")
    return "supervisor_node"


def create_graph():
    print("\n🔧  Building ShopSense LangGraph...")
    print("    Sprint 1: Guardrails + Intent Classification")
    print("    Sprint 2: A2A Supervisor Orchestration")

    graph = StateGraph(ShopSenseState)

    # ── Nodes ──────────────────────────────────────────────────
    graph.add_node("guardrails_node", guardrails_node)
    graph.add_node("intent_classifier_node", intent_classifier_node)
    graph.add_node("supervisor_node", supervisor_node)

    # ── Entry ──────────────────────────────────────────────────
    graph.set_entry_point("guardrails_node")

    # ── Edges ──────────────────────────────────────────────────
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
        route_after_intent,
        {
            "supervisor_node": "supervisor_node"
        }
    )

    graph.add_edge("supervisor_node", END)

    app = graph.compile()
    print("✅  LangGraph compiled!\n")
    return app


# ── Global Instance ────────────────────────────────────────────
shopping_graph = create_graph()