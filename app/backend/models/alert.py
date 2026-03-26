from sqlalchemy import Column, String, Boolean, DateTime, Integer, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid
from app.backend.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    product_name = Column(String)
    brand = Column(String)
    color = Column(String)
    size = Column(String)
    platform = Column(ARRAY(String))
    target_price = Column(DECIMAL)
    discount_pct = Column(Integer)
    in_stock = Column(Boolean, default=False)
    new_arrival = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    triggered_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())