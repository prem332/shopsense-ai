import os
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from app.backend.agents.state import ShopSenseState

load_dotenv()


def guardrails_node(state: ShopSenseState) -> ShopSenseState:
    print("🛡️  Guardrails Node: Validating input...")
    query = state.get("user_query", "").lower()

    shopping_keywords = [
        # Clothing items
        "shirt", "shirts", "pants", "pant", "shoes", "shoe",
        "watch", "watches", "dress", "dresses",
        "kurta", "kurtas", "kurti", "kurtis",
        "saree", "sarees", "jacket", "jackets",
        "jeans", "top", "tops", "skirt", "suit", "suits",
        "blazer", "blazers", "sandal", "sandals",
        "slipper", "slippers", "sneaker", "sneakers",
        "heel", "heels", "bag", "bags", "purse",
        "wallet", "belt", "belts", "legging", "leggings",
        "dupatta", "salwar", "churidar", "trouser", "trousers",
        "tshirt", "t-shirt", "polo", "sweatshirt", "hoodie",
        "cap", "hat", "scarf", "sweater", "cardigan",
        "shorts", "trackpant", "tracksuit",

        # Gender keywords
        "female", "male", "women", "men", "woman", "man",
        "girl", "girls", "boy", "boys", "ladies", "gents",
        "unisex", "her", "his",

        # Gender possessives
        "female's", "male's", "women's", "men's",
        "girl's", "boy's", "ladies'",

        # Actions
        "suggest", "recommend", "find", "show", "need",
        "want", "looking", "search", "get", "buy",
        "purchase", "help me", "give me", "i need",
        "i want",

        # Attributes
        "price", "brand", "size", "color", "colour",
        "formal", "casual", "budget", "under", "between",
        "cheap", "discount", "offer", "sale", "affordable",
        "premium", "luxury", "quality",

        # Occasions
        "wedding", "party", "office", "sports", "gym",
        "ethnic", "western", "traditional", "festive",
        "anniversary", "birthday", "function",

        # Alerts
        "alert", "notify", "notification", "drop",
        "stock", "available", "arrival", "inform",
        "let me know", "tell me when", "remind",

        # Materials
        "cotton", "silk", "linen", "polyester", "wool",
        "leather", "denim", "chiffon", "georgette",

        # Colors
        "navy", "lavender", "black", "white", "red",
        "blue", "green", "yellow", "pink", "grey",
        "beige", "maroon", "orange", "purple",

        # General shopping
        "collection", "wear", "outfit", "clothing",
        "fashion", "accessories", "latest", "new",
        "trending", "bestseller", "popular",
        "comfortable", "stylish", "elegant"
    ]

    is_valid = any(word in query for word in shopping_keywords)


    gender_prefixes = [
        "female's", "male's", "women's", "men's",
        "girl's", "boy's", "ladies'"
    ]
    if any(prefix in query for prefix in gender_prefixes):
        is_valid = True

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
        "remind me", "watch price", "price drop",
        "back in stock", "when available", "new arrival"
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