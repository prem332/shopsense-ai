import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv

from app.backend.agents.alerts.alert_agent import (
    run_alert_registration,
    run_alert_check
)

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
        result = await handle_register_alert(payload)
    elif skill_id == "check_conditions":
        result = await handle_check_conditions(payload)
    elif skill_id == "fire_notification":
        result = await handle_fire_notification(payload)
    else:
        result = {"error": f"Unknown skill: {skill_id}"}

    return A2AResponse(
        jsonrpc="2.0",
        id=request.id,
        result=result
    )


# ── Skill Handlers ─────────────────────────────────────────────

async def handle_register_alert(payload: dict) -> dict:
    """Register new alert in Supabase"""
    user_query = payload.get("user_query", "")
    user_id = payload.get("user_id", "guest")

    try:
        result = run_alert_registration(user_id, user_query)
        alert_details = result.get("alert_details", {})

        return {
            "alert_id": result["alert_id"],
            "status": "registered",
            "conditions": {
                "brand": alert_details.get("brand"),
                "color": alert_details.get("color"),
                "size": alert_details.get("size"),
                "target_price": alert_details.get("target_price"),
                "discount_pct": alert_details.get("discount_pct"),
                "in_stock": alert_details.get("in_stock"),
                "platforms": alert_details.get("platform", [])
            },
            "message": "Alert registered successfully!"
        }

    except Exception as e:
        print(f"❌ Alert registration error: {e}")
        return {
            "alert_id": "error",
            "status": "error",
            "message": str(e)
        }


async def handle_check_conditions(payload: dict) -> dict:
    """Check alert conditions against current prices"""
    alert = payload.get("alert", {})

    try:
        result = run_alert_check(alert)
        return {
            "triggered": result["triggered"],
            "triggered_product": result.get("triggered_product"),
            "alert_id": result.get("alert_id")
        }

    except Exception as e:
        print(f"❌ Alert check error: {e}")
        return {"triggered": False, "error": str(e)}


async def handle_fire_notification(payload: dict) -> dict:
    """Manually fire a notification"""
    alert = payload.get("alert", {})
    product = payload.get("product", {})

    try:
        from app.backend.notifications.notifier import notifier
        success = notifier.notify(alert=alert, product=product)
        return {"notified": success}
    except Exception as e:
        return {"notified": False, "error": str(e)}


# ── Health ─────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "AlertAgent",
        "port": 8004
    }