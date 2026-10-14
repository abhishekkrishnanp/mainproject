"""
Chat Session & Message Models
─────────────────────────────────────────────────────────────────────────────
Stores persistent multi-turn Gemini chat history per user session.
Uses the same SQLAlchemy Base as all other models so
Base.metadata.create_all() in main.py picks them up automatically.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class ChatSession(Base):
    """One conversation session per user (can have many turns)."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mode = Column(String(20), default="student", nullable=False)  # "student" | "parent"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.id",
    )


class ChatMessage(Base):
    """A single message turn within a ChatSession."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)      # "user" | "assistant"
    content = Column(Text, nullable=False)
    # Whether Tavily market data was injected for this turn
    had_market_context = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
