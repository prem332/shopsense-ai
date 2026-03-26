from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.backend.agents.graph import shopping_graph

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: Optional[str] = "guest"
    session_id: Optional[str] = "default"
    query: str

@router.post("/chat")
async def chat(request: ChatRequest):
    print(f"\n💬  Chat: {request.query}")
    try:
        initial_state = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "user_query": request.query,
            "intent": None,
            "is_valid": None,
            "conversation_history": [],
            "category": None,
            "color": None,
            "size": None,
            "skin_tone": None,
            "occasion": None,
            "budget_max": None,
            "brand": None,
            "platforms": ["amazon", "flipkart", "myntra"],
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

        result = await shopping_graph.ainvoke(initial_state)

        return {
            "status": "success",
            "intent": result.get("intent"),
            "is_valid": result.get("is_valid"),
            "products": result.get("ranked_products", []),
            "alert_id": result.get("alert_id"),
            "response": result.get("final_response", "Done!")
        }

    except Exception as e:
        print(f"❌  Chat error: {e}")
        return {"status": "error", "message": str(e)}