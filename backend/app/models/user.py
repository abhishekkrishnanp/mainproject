import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    education_level = Column(String(100), nullable=True)
    course_degree = Column(String(255), nullable=True)
    college = Column(String(255), nullable=True)
    current_skills = Column(Text, nullable=True)          # Comma-separated or JSON
    interests = Column(Text, nullable=True)               # Comma-separated or JSON
    preferred_work_env = Column(String(100), nullable=True) # Remote, Hybrid, On-site, Lab
    location = Column(String(150), nullable=True)
    career_preferences = Column(Text, nullable=True)
    parent_access_code = Column(String(64), unique=True, default=lambda: f"PAR-{uuid.uuid4().hex[:8].upper()}")
    user_id = Column(String(100), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(50), default="student", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessments = relationship("AssessmentResult", back_populates="user", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")
    simulations = relationship("SimulationRun", back_populates="user", cascade="all, delete-orphan")
