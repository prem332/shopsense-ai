from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    occasion: Optional[str] = None
    budget_max: Optional[float] = None
    brand: Optional[str] = None
    platforms: Optional[List[str]] = ["amazon", "flipkart", "myntra"]


@router.post("/search")
async def search(request: SearchRequest):
    return {
        "status": "success",
        "message": "Full implementation in Sprint 3",
        "query": request.query
    }