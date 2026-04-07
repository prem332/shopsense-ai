import os
import asyncio
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv

from app.backend.tools.amazon_tool import search_amazon
from app.backend.vectorstore.pinecone_store import store_products

load_dotenv()

app = FastAPI(title="SearchRankAgent A2A Server")

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
    card_path = Path(__file__).parent.parent / \
        "agent_cards/search_card.json"
    with open(card_path) as f:
        return json.load(f)


# ── A2A Endpoint ───────────────────────────────────────────────

@app.post("/a2a")
async def handle_task(request: A2ARequest) -> A2AResponse:
    skill_id = request.params.get("skill_id")
    payload = request.params.get("payload", {})

    print(f"🔍  SearchAgent received: {skill_id}")

    if skill_id == "search_products":
        result = await search_products(payload)
    elif skill_id == "rank_products":
        result = await rank_products(payload)
    elif skill_id == "reflect_results":
        result = await reflect_results(payload)
    else:
        result = {"error": f"Unknown skill: {skill_id}"}

    return A2AResponse(
        jsonrpc="2.0",
        id=request.id,
        result=result
    )


# ── Skill Implementations ──────────────────────────────────────

async def search_products(payload: dict) -> dict:
    preferences = payload.get("preferences", {})
    user_query = payload.get("user_query", "")


    budget_min = preferences.get("budget_min", 0) or 0
    budget_max = preferences.get("budget_max", 0) or 0
    gender = preferences.get("gender", "") or ""

    # ✅ Build clean search query with gender
    query_parts = []

    if gender == "female":
        query_parts.append("women's")
    elif gender == "male":
        query_parts.append("men's")

    if preferences.get("brand"):
        query_parts.append(preferences["brand"])
    if preferences.get("color"):
        query_parts.append(preferences["color"])
    if preferences.get("category"):
        query_parts.append(preferences["category"])
    if preferences.get("occasion"):
        query_parts.append(preferences["occasion"])
    if preferences.get("size"):
        query_parts.append(f"size {preferences['size']}")

    query = " ".join(query_parts) if query_parts else user_query

    print(f"   → Query: {query}")
    print(f"   → Gender: {gender}")
    print(f"   → Platform: Amazon only")
    print(f"   → Budget: ₹{budget_min} — ₹{budget_max}")

    # ✅ Search Amazon only
    amazon_products = await asyncio.to_thread(
        search_amazon,
        query,
        budget_min if budget_min > 0 else None,
        budget_max if budget_max > 0 else None
    )

    all_products = amazon_products

    print(f"   → Total products found: {len(all_products)}")

    if all_products:
        await asyncio.to_thread(store_products, all_products)

    return {
        "products": all_products,
        "total": len(all_products),
        "query": query
    }


async def rank_products(payload: dict) -> dict:
    products = payload.get("products", [])
    preferences = payload.get("preferences", {})

    if not products:
        return {"ranked_products": [], "total": 0}

    scored = []
    for p in products:
        score = 0
        title_lower = p.get("title", "").lower()

        # Brand match
        if preferences.get("brand") and \
           preferences["brand"].lower() in title_lower:
            score += 5

        # Color match
        if preferences.get("color") and \
           preferences["color"].lower() in title_lower:
            score += 3

        # Category match
        if preferences.get("category") and \
           preferences["category"].lower() in title_lower:
            score += 2

        # Occasion match
        if preferences.get("occasion") and \
           preferences["occasion"].lower() in title_lower:
            score += 2

        # Gender match
        gender = preferences.get("gender", "")
        if gender == "female":
            if any(w in title_lower for w in [
                "women", "woman", "female", "ladies", "girl"
            ]):
                score += 3
        elif gender == "male":
            if any(w in title_lower for w in [
                "men", "man", "male", "gents", "boy"
            ]):
                score += 3

        # Rating bonus
        try:
            rating = float(
                str(p.get("rating", "0")).replace("N/A", "0")
            )
            if rating >= 4.0:
                score += 2
            elif rating >= 3.5:
                score += 1
        except Exception:
            pass

        # Budget range bonus
        price_num = p.get("price_num")
        budget_min = preferences.get("budget_min", 0) or 0
        budget_max = preferences.get("budget_max", 0) or 0

        if price_num and budget_max > 0:
            if budget_min <= price_num <= budget_max:
                score += 2
            elif price_num <= budget_max * 0.7:
                score += 1

        MAX_POSSIBLE = 19
        p["score"] = round((score / MAX_POSSIBLE) * 10, 1)
        scored.append(p)

    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
    print(f"   → Ranked {len(ranked)} products")

    return {
        "ranked_products": ranked[:10],
        "total": len(ranked)
    }


async def reflect_results(payload: dict) -> dict:
    products = payload.get("products", [])
    preferences = payload.get("preferences", {})
    attempts = payload.get("attempts", 0)
    max_attempts = 2

    print(f"   → Reflection attempt {attempts + 1}/{max_attempts}")

    issues = []

    if len(products) == 0:
        issues.append("No products found")

    if len(products) < 3 and attempts < max_attempts:
        issues.append("Too few results")

    if products and preferences.get("brand"):
        brand_matches = [
            p for p in products
            if preferences["brand"].lower() in
            p.get("title", "").lower()
        ]
        if not brand_matches:
            issues.append(
                f"No {preferences['brand']} products found"
            )

    passed = len(issues) == 0 or attempts >= max_attempts

    refined_query = None
    if not passed and issues:
        query_parts = []
        gender = preferences.get("gender", "")
        if gender == "female":
            query_parts.append("women's")
        elif gender == "male":
            query_parts.append("men's")
        if preferences.get("color"):
            query_parts.append(preferences["color"])
        if preferences.get("category"):
            query_parts.append(preferences["category"])
        if preferences.get("occasion"):
            query_parts.append(preferences["occasion"])
        refined_query = " ".join(query_parts)

    print(f"   → Passed: {passed} | Issues: {issues}")

    return {
        "passed": passed,
        "issues": issues,
        "refined_query": refined_query,
        "attempts": attempts + 1,
        "reason": (
            ", ".join(issues) if issues else "Quality check passed"
        )
    }


# ── Health ─────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "SearchRankAgent",
        "port": 8003,
        "platforms": ["amazon"]
    }