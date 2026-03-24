from typing import TypedDict, Optional, List

class ShopSenseState(TypedDict):
    user_query: str
    category: Optional[str]
    color: Optional[str]
    size: Optional[str]
    occasion: Optional[str]
    budget_max: Optional[float]
    brand: Optional[str]
    products: Optional[List[dict]]
    final_response: Optional[str]
    error: Optional[str]