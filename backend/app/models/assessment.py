import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class AssessmentResult(Base):
    """Stores the overall assessment result for a student."""
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Raw scores (0-100 scale per category)
    interest_scores = Column(JSON, nullable=True)       # {"programming": 85, "design": 40, ...}
    skill_scores = Column(JSON, nullable=True)           # {"python": 90, "leadership": 30, ...}
    personality_scores = Column(JSON, nullable=True)    # {"team_work": 70, "remote": 80, ...}
    goal_scores = Column(JSON, nullable=True)            # {"high_salary": 90, "research": 40, ...}
    
    # Derived profile summary
    interest_area = Column(String(100), nullable=True)       # e.g., "Technology"
    strong_skills = Column(JSON, nullable=True)              # list of skill names
    weak_skills = Column(JSON, nullable=True)                # list of skill names
    work_preference = Column(String(100), nullable=True)     # e.g., "Research"
    career_preferences = Column(JSON, nullable=True)         # list of preferred career titles
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="assessments")
    answers = relationship("AssessmentAnswer", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentAnswer(Base):
    """Stores individual question answers from the assessment."""
    __tablename__ = "assessment_answers"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessment_results.id"), nullable=False)
    question_key = Column(String(100), nullable=False)   # e.g., "interest_programming"
    answer_value = Column(Integer, nullable=False)        # 1-5 Likert scale
    category = Column(String(50), nullable=False)         # interest / skill / personality / goal
    created_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("AssessmentResult", back_populates="answers")
