from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
from app.backend.agents.graph import shopping_graph

router = APIRouter()


class ChatRequest(BaseModel):
    user_id: Optional[str] = "guest"
    session_id: Optional[str] = "default"
    query: str
    platforms: Optional[list] = ["amazon", "flipkart", "myntra"]
    budget_min: Optional[float] = 0
    budget_max: Optional[float] = 0
    gender: Optional[str] = ""
    stream: Optional[bool] = False


@router.post("/chat")
async def chat(request: ChatRequest):
    print(f"\n💬  Chat: {request.query}")
    try:
        enriched_query = request.query
        if (
            request.gender and
            request.gender.lower() not in request.query.lower()
        ):
            enriched_query = f"{request.gender}'s {enriched_query}"

        print(f"   → Query: {enriched_query}")
        print(
            f"   → Budget: ₹{request.budget_min} — ₹{request.budget_max}"
        )
        print(f"   → Gender: {request.gender}")

        initial_state = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "user_query": enriched_query,
            "intent": None,
            "is_valid": None,
            "conversation_history": [],
            "category": None,
            "color": None,
            "size": None,
            "skin_tone": None,
            "occasion": None,
            "budget_min": request.budget_min,
            "budget_max": request.budget_max,
            "gender": request.gender,
            "brand": None,
            "platforms": request.platforms,
            "raw_products": None,
            "ranked_products": None,
            "reflection_passed": None,
            "reflection_attempts": 0,
            "alert_id": None,
            "target_price": None,
            "discount_pct": None,
            "in_stock_alert": None,
            "new_arrival_alert": None,
            "final_response": None,
            "error": None
        }

        if request.stream:
            async def stream_response():
                yield json.dumps({
                    "type": "status",
                    "message": "🔍 Searching products..."
                }) + "\n"

                result = await shopping_graph.ainvoke(initial_state)
                products = result.get("ranked_products") or []

                for product in products:
                    yield json.dumps({
                        "type": "product",
                        "data": product
                    }) + "\n"

                yield json.dumps({
                    "type": "done",
                    "total": len(products),
                    "intent": result.get("intent"),
                    "response": result.get("final_response")
                }) + "\n"

            return StreamingResponse(
                stream_response(),
                media_type="application/x-ndjson"
            )

        result = await shopping_graph.ainvoke(initial_state)
        products = result.get("ranked_products") or []

        return {
            "status": "success",
            "intent": result.get("intent"),
            "is_valid": result.get("is_valid"),
            "preferences": {
                "category": result.get("category"),
                "color": result.get("color"),
                "size": result.get("size"),
                "occasion": result.get("occasion"),
                "budget_max": result.get("budget_max"),
                "brand": result.get("brand"),
            },
            "products": products,
            "products_count": len(products),
            "reflection_attempts": result.get("reflection_attempts", 0),
            "alert_id": result.get("alert_id"),
            "response": result.get("final_response", "Done!")
        }

    except Exception as e:
        print(f"❌  Chat error: {e}")
        return {"status": "error", "message": str(e)}