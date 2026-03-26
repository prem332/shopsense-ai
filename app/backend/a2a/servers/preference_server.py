import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PreferenceAgent A2A Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1
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
    card_path = Path(__file__).parent.parent / "agent_cards/preference_card.json"
    with open(card_path) as f:
        return json.load(f)


# ── A2A Endpoint ───────────────────────────────────────────────

@app.post("/a2a")
async def handle_task(request: A2ARequest) -> A2AResponse:
    skill_id = request.params.get("skill_id")
    payload = request.params.get("payload", {})

    print(f"🧠  PreferenceAgent received: {skill_id}")

    if skill_id == "extract_preferences":
        result = await extract_preferences(payload)
    elif skill_id == "fetch_history":
        result = await fetch_history(payload)
    else:
        result = {"error": f"Unknown skill: {skill_id}"}

    return A2AResponse(
        jsonrpc="2.0",
        id=request.id,
        result=result
    )


# ── Skill Implementations ──────────────────────────────────────

async def extract_preferences(payload: dict) -> dict:
    user_query = payload.get("user_query", "")

    system_prompt = """You are a shopping assistant that extracts
    structured preferences from user queries.

    Extract these fields:
    - category: product type (shirts, shoes, watches, pants etc.)
    - color: preferred color
    - size: clothing or shoe size
    - occasion: formal, casual, wedding, party, sports etc.
    - budget_max: maximum budget in INR (number only)
    - brand: preferred brand name
    - skin_tone: fair, medium, dark (if mentioned)

    Return ONLY a valid JSON object. No explanation. No markdown.
    If a field is not mentioned, set it to null.

    Example:
    {
        "category": "shirts",
        "color": "navy blue",
        "size": "L",
        "occasion": "formal",
        "budget_max": 1500,
        "brand": "Allen Solly",
        "skin_tone": null
    }"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query)
    ]

    response = llm.invoke(messages)

    try:
        raw = response.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        preferences = json.loads(raw)
        print(f"   → Extracted: {preferences}")
        return {"preferences": preferences, "status": "success"}
    except Exception as e:
        print(f"   → Extraction failed: {e}")
        return {"preferences": {}, "status": "error", "error": str(e)}


async def fetch_history(payload: dict) -> dict:
    # pgvector history fetch
    user_id = payload.get("user_id")
    return {
        "history": [],
        "user_id": user_id,
        "message": "History fetch — Sprint 3"
    }


# ── Health ─────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "PreferenceAgent",
        "port": 8002
    }