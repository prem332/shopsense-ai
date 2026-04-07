import json
import re
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


# ── PII Detection ──────────────────────────────────────────────

def detect_pii(query: str) -> dict:
    """
    Detect Personal Identifiable Information (PII) in query.
    Protects against data leakage of user/third party info.

    Detects:
    - Aadhaar number (12 digits)
    - PAN card (ABCDE1234F format)
    - Phone numbers (10 digit Indian)
    - Email addresses
    - Credit/Debit card numbers
    - Bank account numbers
    """
    pii_patterns = {
        "aadhaar": r'\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b',
        "pan_card": r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
        "phone": r'\b[6-9]\d{9}\b',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        "bank_account": r'\b\d{9,18}\b',
        "ifsc_code": r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
        "passport": r'\b[A-Z]{1}[0-9]{7}\b',
        "voter_id": r'\b[A-Z]{3}[0-9]{7}\b',
    }

    detected = []
    for pii_type, pattern in pii_patterns.items():
        if re.search(pattern, query, re.IGNORECASE):
            detected.append(pii_type)

    return {
        "has_pii": len(detected) > 0,
        "detected_types": detected
    }


# ── Harmful Content Detection ──────────────────────────────────

def detect_harmful_intent(query: str) -> dict:
    """
    Detect harmful intent in shopping queries.
    Blocks requests for dangerous/illegal products.
    """
    harmful_patterns = [
        # Weapons
        "weapon", "gun", "pistol", "rifle", "ammunition",
        "bomb", "explosive", "grenade", "knife attack",
        "illegal weapon",

        # Drugs
        "drug", "cocaine", "heroin", "marijuana", "weed",
        "narcotic", "mdma", "methamphetamine",

        # Hate speech
        "hate", "racist", "terrorism", "terrorist",
        "extremist", "genocide",

        # Adult content
        "pornography", "porn", "adult content",
        "explicit content",

        # Illegal activities
        "stolen", "counterfeit", "fake id",
        "illegal", "smuggle", "trafficking",
    ]

    query_lower = query.lower()
    found = [p for p in harmful_patterns if p in query_lower]

    return {
        "is_harmful": len(found) > 0,
        "harmful_terms": found
    }


# ── Validate Input ─────────────────────────────────────────────

async def validate_input(payload: dict) -> dict:
    query = payload.get("user_query", "")
    query_lower = query.lower()

    # ── Step 1: Check for PII ──────────────────────────────────
    pii_result = detect_pii(query)
    if pii_result["has_pii"]:
        pii_types = ", ".join(pii_result["detected_types"])
        print(f"   → 🚫 PII detected: {pii_types}")
        return {
            "is_valid": False,
            "rejection_reason": (
                f"⚠️ Your message contains personal information "
                f"({pii_types}). Please don't share personal "
                f"data like Aadhaar, PAN, phone numbers or "
                f"email addresses."
            )
        }

    # ── Step 2: Check for Harmful Intent ──────────────────────
    harmful_result = detect_harmful_intent(query)
    if harmful_result["is_harmful"]:
        print(f"   → 🚫 Harmful intent: {harmful_result['harmful_terms']}")
        return {
            "is_valid": False,
            "rejection_reason": (
                "❌ I can only help with legal shopping queries. "
                "Please ask about clothing, accessories, or "
                "other legal products."
            )
        }

    # ── Step 3: Check for Prompt Injection ────────────────────
    injection_result = await detect_injection({"user_query": query})
    if injection_result["is_injection"]:
        print(f"   → 🚫 Prompt injection detected")
        return {
            "is_valid": False,
            "rejection_reason": (
                "❌ Invalid request detected."
            )
        }

    # ── Step 4: Check Shopping Keywords ───────────────────────
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
        "sweater", "cardigan", "shorts", "trackpant",

        # Gender keywords
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

        # Colors
        "navy", "lavender", "black", "white", "red",
        "blue", "green", "yellow", "pink", "grey",

        # General shopping
        "collection", "wear", "outfit", "clothing",
        "fashion", "accessories", "latest", "new",
        "trending", "bestseller", "popular"
    ]

    is_valid = any(word in query_lower for word in shopping_keywords)

    gender_prefixes = [
        "female's", "male's", "women's", "men's",
        "girl's", "boy's", "ladies'"
    ]
    if any(prefix in query_lower for prefix in gender_prefixes):
        is_valid = True

    print(f"   → Valid: {is_valid} | Query: {query_lower[:50]}")

    return {
        "is_valid": is_valid,
        "rejection_reason": (
            None if is_valid
            else "Query is not shopping related"
        )
    }


# ── Detect Injection ───────────────────────────────────────────

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
        "override",
        "disregard",
        "new instructions",
        "pretend you are",
        "simulate",
        "bypass",
        "disable safety",
        "ignore safety",
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


# ── Health ─────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "GuardrailsAgent",
        "port": 8001
    }