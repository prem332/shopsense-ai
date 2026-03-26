from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.backend.database import get_db
from app.backend.agents.state import AlertRequest

router = APIRouter()


@router.post("/alerts")
async def create_alert(
    request: AlertRequest,
    db: Session = Depends(get_db)
):
    return {
        "status": "success",
        "message": "Full implementation in Sprint 4",
        "alert": request.dict()
    }


@router.get("/alerts/{user_id}")
async def get_alerts(
    user_id: str,
    db: Session = Depends(get_db)
):
    return {
        "status": "success",
        "user_id": user_id,
        "alerts": []
    }