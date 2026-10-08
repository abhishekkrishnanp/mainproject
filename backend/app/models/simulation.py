from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SimulationRun(Base):
    """10-year career simulation for a user."""
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="simulations")
    career = relationship("Career")
    years = relationship("SimulationYear", back_populates="simulation",
                         cascade="all, delete-orphan", order_by="SimulationYear.year")


class SimulationYear(Base):
    """Single year entry within a career simulation."""
    __tablename__ = "simulation_years"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulation_runs.id"), nullable=False)
    year = Column(Integer, nullable=False)              # 1-10
    job_title = Column(String(200), nullable=True)
    experience_level = Column(String(100), nullable=True)  # "Fresher", "Junior", ...
    salary_min = Column(Float, nullable=True)           # INR lakhs
    salary_max = Column(Float, nullable=True)           # INR lakhs
    skills_acquired = Column(JSON, nullable=True)       # list of skills
    responsibilities = Column(JSON, nullable=True)      # list of responsibility strings
    promotion_note = Column(Text, nullable=True)        # qualitative note

    simulation = relationship("SimulationRun", back_populates="years")
