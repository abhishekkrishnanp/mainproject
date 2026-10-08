from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class CareerRecommendation(Base):
    """Career recommendations generated for a user."""
    __tablename__ = "career_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False)

    match_score = Column(Float, nullable=False)          # 0-100
    interest_match = Column(Float, nullable=True)        # sub-score 0-100
    skill_match = Column(Float, nullable=True)
    education_match = Column(Float, nullable=True)
    goal_match = Column(Float, nullable=True)
    work_pref_match = Column(Float, nullable=True)

    reasons = Column(JSON, nullable=True)               # list of explanation strings
    rank = Column(Integer, nullable=True)               # 1 = top recommendation

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    career = relationship("Career", back_populates="recommendations")


class SelectedCareer(Base):
    """The career that a user has explicitly selected."""
    __tablename__ = "selected_careers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False)
    selected_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    career = relationship("Career", back_populates="selected_by")
