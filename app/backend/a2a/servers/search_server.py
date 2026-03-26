import os
import json
import re
import hashlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from serpapi import GoogleSearch
from langchain_community.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SearchRankAgent A2A Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
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


# ── Helper Functions ───────────────────────────────────────────

def search_platform(query: str, platform: str, budget_max: float = None) -> list:
    """Search a single platform via SerpAPI"""
    params = {
        "api_key": os.getenv("SERPAPI_KEY"),
        "k": query
    }

    if platform == "amazon":
        params["engine"] = "amazon"
        params["amazon_domain"] = "amazon.in"
    elif platform == "google_shopping":
        params["engine"] = "google_shopping"
        params["q"] = query
        params["gl"] = "in"
        params["hl"] = "en"

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        products = []

        items = results.get("organic_results", []) or \
                results.get("shopping_results", [])

        for item in items[:5]:
            price_raw = item.get("price", "")
            price_num = None

            if price_raw:
                price_str = str(price_raw).replace(
                    "₹", ""
                ).replace(",", "").strip()
                numbers = re.findall(r'\d+\.?\d*', price_str)
                if numbers:
                    price_num = float(numbers[0])

            if budget_max and price_num and price_num > budget_max:
                continue

            product = {
                "title": item.get("title", "N/A"),
                "price": price_raw or "N/A",
                "price_num": price_num,
                "image": item.get("thumbnail", ""),
                "link": item.get("link", ""),
                "rating": str(item.get("rating", "N/A")),
                "platform": platform.title()
            }

            if product["title"] != "N/A":
                products.append(product)

        return products

    except Exception as e:
        print(f"⚠️  {platform} search error: {e}")
        return []


def get_pinecone_index():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME", "shopsense-products")
    existing = [i.name for i in pc.list_indexes()]

    if index_name not in existing:
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(index_name)


async def search_products(payload: dict) -> dict:
    preferences = payload.get("preferences", {})
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

    query = " ".join(query_parts) if query_parts else payload.get("user_query", "")
    print(f"   → Query: {query}")

    # Search Amazon (main platform for now)
    all_products = search_platform(query, "amazon", budget_max)

    # Store in Pinecone
    try:
        index = get_pinecone_index()
        vectors = []
        for product in all_products:
            emb = embeddings.embed_query(product["title"])
            pid = hashlib.md5(product["title"].encode()).hexdigest()
            vectors.append({
                "id": pid,
                "values": emb,
                "metadata": {
                    "title": product["title"],
                    "price": str(product["price"]),
                    "link": product["link"],
                    "platform": product["platform"]
                }
            })
        if vectors:
            index.upsert(vectors=vectors)
            print(f"   → Stored {len(vectors)} in Pinecone")
    except Exception as e:
        print(f"   → Pinecone error: {e}")

    return {
        "products": all_products,
        "total": len(all_products),
        "query": query
    }


async def rank_products(payload: dict) -> dict:
    products = payload.get("products", [])
    preferences = payload.get("preferences", {})

    # Score products against preferences
    scored = []
    for p in products:
        score = 0
        title_lower = p.get("title", "").lower()

        if preferences.get("brand") and \
           preferences["brand"].lower() in title_lower:
            score += 3
        if preferences.get("color") and \
           preferences["color"].lower() in title_lower:
            score += 2
        if preferences.get("category") and \
           preferences["category"].lower() in title_lower:
            score += 2
        if preferences.get("occasion") and \
           preferences["occasion"].lower() in title_lower:
            score += 1

        p["score"] = score
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

    # Quality check
    if len(products) >= 3:
        passed = True
        reason = "Sufficient results found"
    elif attempts >= 2:
        passed = True
        reason = "Max attempts reached"
    else:
        passed = False
        reason = "Too few results — retry needed"

    print(f"   → Reflection: {reason}")

    return {
        "passed": passed,
        "reason": reason,
        "attempts": attempts + 1
    }


# ── Health ─────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "SearchRankAgent",
        "port": 8003
    }