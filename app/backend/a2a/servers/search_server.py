import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv

from app.backend.tools.amazon_tool import search_amazon
from app.backend.tools.flipkart_tool import search_flipkart
from app.backend.tools.myntra_tool import search_myntra
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
    card_path = Path(__file__).parent.parent / "agent_cards/search_card.json"
    with open(card_path) as f:
        import json
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
    platforms = payload.get("platforms", ["amazon", "flipkart", "myntra"])
    budget_max = preferences.get("budget_max")

    query_parts = []
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
    print(f"   → Platforms: {platforms}")

    tasks = []

    if "amazon" in platforms:
        tasks.append(
            asyncio.to_thread(search_amazon, query, budget_max)
        )
    if "flipkart" in platforms:
        tasks.append(
            asyncio.to_thread(search_flipkart, query, budget_max)
        )
    if "myntra" in platforms:
        tasks.append(
            asyncio.to_thread(search_myntra, query, budget_max)
        )

    # Run all searches in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Combine all results
    all_products = []
    for result in results:
        if isinstance(result, list):
            all_products.extend(result)

    print(f"   → Total products found: {len(all_products)}")

    # Store in Pinecone
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

    # Score each product
    scored = []
    for p in products:
        score = 0
        title_lower = p.get("title", "").lower()

        # Brand match = highest priority
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

        # Rating bonus
        try:
            rating = float(str(p.get("rating", "0")).replace("N/A", "0"))
            if rating >= 4.0:
                score += 2
            elif rating >= 3.5:
                score += 1
        except:
            pass

        # Budget bonus (cheaper = better within budget)
        price_num = p.get("price_num")
        budget_max = preferences.get("budget_max")
        if price_num and budget_max:
            if price_num <= budget_max * 0.7:
                score += 1

        p["score"] = score
        scored.append(p)

    # Sort by score descending
    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
    print(f"   → Ranked {len(ranked)} products")

    return {
        "ranked_products": ranked[:10],
        "total": len(ranked)
    }


async def reflect_results(payload: dict) -> dict:
    """
    Self-reflection loop:
    Evaluates if results are good enough.
    If not, suggests refined query.
    """
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
            if preferences["brand"].lower() in p.get("title", "").lower()
        ]
        if not brand_matches:
            issues.append(f"No {preferences['brand']} products found")

    passed = len(issues) == 0 or attempts >= max_attempts

    refined_query = None
    if not passed and issues:
        # Broaden search by removing brand constraint
        query_parts = []
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
        "reason": ", ".join(issues) if issues else "Quality check passed"
    }


# ── Health ─────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "SearchRankAgent",
        "port": 8003,
        "platforms": ["amazon", "flipkart", "myntra"]
    }