import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AlertAgent A2A Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ─────────────────────────────────────────────────────

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
    card_path = Path(__file__).parent.parent / "agent_cards/alert_card.json"
    with open(card_path) as f:
        return json.load(f)


# ── A2A Endpoint ───────────────────────────────────────────────

@app.post("/a2a")
async def handle_task(request: A2ARequest) -> A2AResponse:
    skill_id = request.params.get("skill_id")
    payload = request.params.get("payload", {})

    print(f"🔔  AlertAgent received: {skill_id}")

    if skill_id == "register_alert":
        result = await register_alert(payload)
    elif skill_id == "check_conditions":
        result = await check_conditions(payload)
    elif skill_id == "fire_notification":
        result = await fire_notification(payload)
    else:
        result = {"error": f"Unknown skill: {skill_id}"}

    return A2AResponse(
        jsonrpc="2.0",
        id=request.id,
        result=result
    )


# ── Skill Implementations ──────────────────────────────────────

async def register_alert(payload: dict) -> dict:
    """Sprint 4 — Full DB implementation"""
    print(f"   → Registering alert: {payload}")
    return {
        "alert_id": "alert-stub-001",
        "status": "registered",
        "message": "Full DB implementation in Sprint 4",
        "conditions": {
            "brand": payload.get("brand"),
            "color": payload.get("color"),
            "size": payload.get("size"),
            "target_price": payload.get("target_price"),
            "discount_pct": payload.get("discount_pct"),
            "in_stock": payload.get("in_stock"),
            "platforms": payload.get("platforms", ["amazon", "flipkart", "myntra"])
        }
    }


async def check_conditions(payload: dict) -> dict:
    """Sprint 4 — Full condition evaluation"""
    return {
        "conditions_met": False,
        "message": "Full evaluation in Sprint 4"
    }


async def fire_notification(payload: dict) -> dict:
    """Sprint 4 — Full notification"""
    return {
        "notified": False,
        "message": "Full notification in Sprint 4"
    }


# ── Health ─────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "AlertAgent",
        "port": 8004
    }