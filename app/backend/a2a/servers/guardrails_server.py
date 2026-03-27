import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path


app = FastAPI(title="GuardrailsAgent A2A Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class A2ARequest(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    method: str
    params: dict


class A2AResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    result: dict


@app.get("/.well-known/agent.json")
async def get_agent_card():
    card_path = Path(__file__).parent.parent / \
        "agent_cards/guardrails_card.json"
    with open(card_path) as f:
        return json.load(f)


@app.post("/a2a")
async def handle_task(request: A2ARequest) -> A2AResponse:
    skill_id = request.params.get("skill_id")
    payload = request.params.get("payload", {})

    print(f"🛡️  GuardrailsAgent received: {skill_id}")

    if skill_id == "validate_input":
        result = await validate_input(payload)
    elif skill_id == "detect_injection":
        result = await detect_injection(payload)
    else:
        result = {"error": f"Unknown skill: {skill_id}"}

    return A2AResponse(
        jsonrpc="2.0",
        id=request.id,
        result=result
    )


async def validate_input(payload: dict) -> dict:
    query = payload.get("user_query", "").lower()

    shopping_keywords = [
        # Clothing items
        "shirt", "shirts", "pants", "pant", "shoes", "shoe",
        "watch", "watches", "dress", "dresses", "kurta", "kurtas",
        "saree", "sarees", "jacket", "jackets", "jeans", "top",
        "tops", "skirt", "suit", "suits", "blazer", "blazers",
        "sandal", "sandals", "slipper", "slippers", "sneaker",
        "sneakers", "heel", "heels", "bag", "bags", "purse",
        "wallet", "belt", "belts", "legging", "leggings",
        "kurti", "kurtis", "dupatta", "salwar", "churidar",
        "trouser", "trousers", "tshirt", "t-shirt", "polo",
        "sweatshirt", "hoodie", "cap", "hat", "scarf",

        # Gender keywords ← KEY FIX
        "female", "male", "women", "men", "woman", "man",
        "girl", "girls", "boy", "boys", "ladies", "gents",
        "unisex",

        # Action keywords
        "suggest", "recommend", "find", "show", "need",
        "want", "looking", "search", "get", "buy", "purchase",
        "help me", "give me",

        # Attributes
        "price", "brand", "size", "color", "colour",
        "formal", "casual", "budget", "under", "between",
        "cheap", "discount", "offer", "sale", "affordable",
        "premium", "luxury",

        # Occasions
        "wedding", "party", "office", "sports", "gym",
        "ethnic", "western", "traditional", "festive",

        # Alerts
        "alert", "notify", "notification", "drop",
        "stock", "available", "arrival",

        # Materials
        "cotton", "silk", "linen", "polyester", "wool",

        # Colors (common searches)
        "navy", "lavender", "black", "white", "red",
        "blue", "green", "yellow", "pink", "grey",

        # General shopping
        "collection", "wear", "outfit", "clothing",
        "fashion", "accessories", "latest", "new",
        "trending", "bestseller", "popular"
    ]

    is_valid = any(word in query for word in shopping_keywords)

    # ✅ Extra check — if query has gender prefix it's always valid
    gender_prefixes = [
        "female's", "male's", "women's", "men's",
        "girl's", "boy's", "ladies'"
    ]
    if any(prefix in query for prefix in gender_prefixes):
        is_valid = True

    print(f"   → Valid: {is_valid} | Query: {query[:50]}")

    return {
        "is_valid": is_valid,
        "rejection_reason": (
            None if is_valid
            else "Query is not shopping related"
        )
    }


async def detect_injection(payload: dict) -> dict:
    query = payload.get("user_query", "").lower()

    injection_patterns = [
        "ignore previous",
        "ignore instructions",
        "forget everything",
        "you are now",
        "act as",
        "jailbreak",
        "system prompt",
        "override"
    ]

    is_injection = any(
        pattern in query for pattern in injection_patterns
    )

    return {
        "is_injection": is_injection,
        "rejection_reason": (
            "Prompt injection detected" if is_injection else None
        )
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "GuardrailsAgent",
        "port": 8001
    }