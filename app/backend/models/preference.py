from sqlalchemy import Column, String, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid
from app.backend.database import Base


class Preference(Base):
    __tablename__ = "preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    category = Column(String)
    color = Column(ARRAY(String))
    size = Column(String)
    skin_tone = Column(String)
    occasion = Column(String)
    budget_max = Column(DECIMAL)
    brands = Column(ARRAY(String))
    created_at = Column(DateTime, server_default=func.now())