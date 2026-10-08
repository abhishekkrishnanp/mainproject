from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class ParentAccount(Base):
    __tablename__ = "parent_accounts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), index=True, nullable=False)  # student_id string or user id
    parent_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. ACGS-PAR-8F29K
    parent_pin_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
