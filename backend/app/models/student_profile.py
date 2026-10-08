from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    parent_whatsapp = Column(String(50), nullable=True)
    education_level = Column(String(100), nullable=True)       # School / College / Post Graduate / Working Professional
    current_class_or_year = Column(String(100), nullable=True) # e.g. "12th Grade", "B.Tech 3rd Year"
    stream = Column(String(100), nullable=True)                # Science, Commerce, Arts, etc.
    branch = Column(String(100), nullable=True)                # CS, AI & Data Science, Mech, etc.
    department = Column(String(100), nullable=True)
    university = Column(String(255), nullable=True)
    cgpa_percentage = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="student_profile")
