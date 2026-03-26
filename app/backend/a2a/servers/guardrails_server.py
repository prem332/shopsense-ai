import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
from pathlib import Path

app = FastAPI(title="GuardrailsAgent A2A Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── A2A Request/Response Models ────────────────────────────────

class A2ARequest(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    method: str
    params: dict


class A2AResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    result: dict


# ── Agent Card ─────────────────────────────────────────────────

@app.get("/.well-known/agent.json")
async def get_agent_card():
    card_path = Path(__file__).parent.parent / "agent_cards/guardrails_card.json"
    with open(card_path) as f:
        return json.load(f)


# ── A2A Endpoint ───────────────────────────────────────────────

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


# ── Skill Implementations ──────────────────────────────────────

async def validate_input(payload: dict) -> dict:
    query = payload.get("user_query", "").lower()

    shopping_keywords = [
        "shirt", "pants", "shoes", "watch", "dress",
        "buy", "purchase", "price", "brand", "size",
        "color", "formal", "casual", "budget", "under",
        "alert", "notify", "cheap", "discount", "offer",
        "accessories", "jacket", "kurta", "saree"
    ]

    is_valid = any(word in query for word in shopping_keywords)

    print(f"   → Valid: {is_valid} | Query: {query[:50]}")

    return {
        "is_valid": is_valid,
        "rejection_reason": None if is_valid else "Query is not shopping related"
    }


async def detect_injection(payload: dict) -> dict:
    query = payload.get("user_query", "").lower()

    # Prompt injection patterns
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

    is_injection = any(pattern in query for pattern in injection_patterns)

    return {
        "is_injection": is_injection,
        "rejection_reason": "Prompt injection detected" if is_injection else None
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "GuardrailsAgent",
        "port": 8001
    }