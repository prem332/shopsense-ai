from typing import TypedDict, Optional, List
from pydantic import BaseModel


class ShopSenseState(TypedDict):
    # Conversation
    user_id: Optional[str]
    session_id: Optional[str]
    user_query: str
    intent: Optional[str]
    conversation_history: Optional[List[dict]]

    # Guardrails
    is_valid: Optional[bool]
    rejection_reason: Optional[str]

    category: Optional[str]
    color: Optional[str]
    size: Optional[str]
    skin_tone: Optional[str]
    occasion: Optional[str]
    budget_max: Optional[float]
    brand: Optional[str]
    platforms: Optional[List[str]]

    raw_products: Optional[List[dict]]
    ranked_products: Optional[List[dict]]
    reflection_passed: Optional[bool]
    reflection_attempts: Optional[int]

    alert_id: Optional[str]
    target_price: Optional[float]
    discount_pct: Optional[int]
    in_stock_alert: Optional[bool]
    new_arrival_alert: Optional[bool]

    final_response: Optional[str]
    error: Optional[str]


class ProductResult(BaseModel):
    title: str
    price: str
    price_num: Optional[float] = None
    image: Optional[str] = None
    link: str
    rating: Optional[str] = None
    platform: str
    score: Optional[float] = None


class AlertRequest(BaseModel):
    user_id: str
    product_name: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    platform: Optional[List[str]] = ["amazon", "flipkart", "myntra"]
    target_price: Optional[float] = None
    discount_pct: Optional[int] = None
    in_stock: Optional[bool] = False
    new_arrival: Optional[bool] = False