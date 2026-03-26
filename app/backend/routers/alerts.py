from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional, List
from app.backend.database import get_db
from app.backend.agents.alerts.registration_node import registration_node

router = APIRouter()


# ── Request Models ─────────────────────────────────────────────

class AlertCreateRequest(BaseModel):
    user_id: str = "guest"
    user_query: str
    product_name: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    platform: Optional[List[str]] = ["amazon", "flipkart", "myntra"]
    target_price: Optional[float] = None
    discount_pct: Optional[int] = None
    in_stock: Optional[bool] = False
    new_arrival: Optional[bool] = False


# ── Endpoints ──────────────────────────────────────────────────

@router.post("/alerts")
async def create_alert(
    request: AlertCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new price/stock alert"""
    try:
        result = registration_node(
            user_id=str(request.user_id),
            user_query=request.user_query
        )

        return {
            "status": "success",
            "alert_id": result["alert_id"],
            "conditions": result["alert_details"],
            "message": "✅ Alert registered! We'll notify you when conditions are met."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/{user_id}")
async def get_alerts(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all alerts for a user"""
    try:
        result = db.execute(text("""
            SELECT
                id, product_name, brand, color, size,
                platform, target_price, discount_pct,
                in_stock, new_arrival, is_active,
                triggered_at, created_at
            FROM alerts
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """), {"user_id": str(user_id)})

        alerts = []
        for row in result:
            alerts.append({
                "id": str(row.id),
                "product_name": row.product_name,
                "brand": row.brand,
                "color": row.color,
                "size": row.size,
                "platform": row.platform,
                "target_price": float(row.target_price) if row.target_price else None,
                "discount_pct": row.discount_pct,
                "in_stock": row.in_stock,
                "new_arrival": row.new_arrival,
                "is_active": row.is_active,
                "triggered_at": str(row.triggered_at) if row.triggered_at else None,
                "created_at": str(row.created_at)
            })

        return {
            "status": "success",
            "user_id": user_id,
            "total": len(alerts),
            "alerts": alerts
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """Delete an alert"""
    try:
        db.execute(text("""
            DELETE FROM alerts WHERE id = :id
        """), {"id": alert_id})
        db.commit()

        return {
            "status": "success",
            "message": f"Alert {alert_id} deleted"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/alerts/{alert_id}/pause")
async def pause_alert(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """Pause or unpause an alert"""
    try:
        result = db.execute(text("""
            UPDATE alerts
            SET is_active = NOT is_active
            WHERE id = :id
            RETURNING is_active
        """), {"id": alert_id})
        db.commit()

        row = result.fetchone()
        status = "active" if row and row.is_active else "paused"

        return {
            "status": "success",
            "alert_id": alert_id,
            "alert_status": status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))