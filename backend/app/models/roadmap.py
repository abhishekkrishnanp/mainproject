from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base


class SkillGap(Base):
    """Skill gap analysis result for a user's selected career."""
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False)

    strong_skills = Column(JSON, nullable=True)        # [{"skill": "Python", "status": "Strong"}]
    skills_to_improve = Column(JSON, nullable=True)    # [{"skill": "Statistics", "status": "Intermediate"}]
    missing_skills = Column(JSON, nullable=True)       # [{"skill": "TensorFlow", "status": "Missing"}]
    overall_readiness = Column(Float, nullable=True)   # 0-100 percentage

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
    career = relationship("Career")


class StudentSkill(Base):
    """Individual skills associated with a student."""
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String(150), nullable=False)
    proficiency = Column(String(50), nullable=True)  # "Beginner" / "Intermediate" / "Advanced"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class Roadmap(Base):
    """Career roadmap generated for a user."""
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False)
    total_stages = Column(Integer, default=0)
    completed_stages = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="roadmaps")
    career = relationship("Career")
    items = relationship("RoadmapItem", back_populates="roadmap", cascade="all, delete-orphan",
                         order_by="RoadmapItem.stage_number")


class RoadmapItem(Base):
    """Individual stage/item within a career roadmap."""
    __tablename__ = "roadmap_items"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    stage_number = Column(Integer, nullable=False)
    stage_title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    skills = Column(JSON, nullable=True)              # ["Python", "NumPy"]
    topics = Column(JSON, nullable=True)              # ["Basics", "OOP", ...]
    projects = Column(JSON, nullable=True)            # ["Todo App", "Calculator"]
    resources = Column(JSON, nullable=True)           # [{"name": "...", "url": "..."}]
    estimated_duration = Column(String(100), nullable=True)  # "4-6 weeks"

    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    roadmap = relationship("Roadmap", back_populates="items")
