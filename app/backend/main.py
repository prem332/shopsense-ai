import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.backend.routers import chat, search, alerts
from app.backend.database import test_connection
from app.backend.a2a.registry import registry

load_dotenv()

app = FastAPI(
    title="ShopSense AI",
    description="AI-powered personal shopping assistant with A2A protocol",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])

# ── A2A Endpoints ──────────────────────────────────────────────
@app.get("/.well-known/agent.json", tags=["A2A"])
async def get_supervisor_card():
    card_path = "app/backend/a2a/agent_cards/supervisor_card.json"
    with open(card_path) as f:
        return json.load(f)

@app.get("/a2a/agents", tags=["A2A"])
async def list_agents():
    return registry.get_all_agents()

@app.get("/a2a/agents/{agent_name}", tags=["A2A"])
async def get_agent(agent_name: str):
    agent = registry.get_agent(agent_name)
    if not agent:
        return {"error": f"Agent '{agent_name}' not found"}
    return agent

# ── Health ─────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "service": "ShopSense AI",
        "version": "1.0.0",
        "sprint": "Sprint 5 — Frontend",
        "agents": list(registry.agents.keys()),
        "langsmith": os.getenv("LANGCHAIN_TRACING_V2")
    }

# ── Startup ────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    print("\n" + "=" * 50)
    print("🛍️   ShopSense AI — Starting Up")
    print("=" * 50)
    test_connection()
    print(f"✅  A2A Agents: {len(registry.agents)}")
    print(f"✅  LangSmith: {os.getenv('LANGCHAIN_TRACING_V2')}")
    print("=" * 50)
    print("🚀  Ready!\n")