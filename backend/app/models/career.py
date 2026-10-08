from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Career(Base):
    """Master career information table."""
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), unique=True, nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    required_degree = Column(String(200), nullable=True)

    # Required / optional skills stored as JSON lists
    required_skills = Column(JSON, nullable=True)      # ["Python", "ML", ...]
    optional_skills = Column(JSON, nullable=True)      # ["TensorFlow", ...]

    # Salary info (INR lakhs per annum)
    salary_beginner = Column(Float, nullable=True)     # e.g., 6.0
    salary_mid = Column(Float, nullable=True)          # e.g., 15.0
    salary_senior = Column(Float, nullable=True)       # e.g., 35.0

    # Career metadata
    career_growth = Column(String(50), nullable=True)  # "High" / "Medium" / "Low"
    work_type = Column(String(100), nullable=True)     # "Remote/Office"
    industries = Column(JSON, nullable=True)            # ["Tech", "Finance", ...]
    job_roles = Column(JSON, nullable=True)             # ["ML Engineer", "AI Researcher", ...]
    common_myths = Column(JSON, nullable=True)          # list of myth strings (quick list)

    # Interest/personality match tags
    interest_tags = Column(JSON, nullable=True)         # ["programming", "mathematics", "research"]
    goal_tags = Column(JSON, nullable=True)             # ["high_salary", "research"]
    work_pref_tags = Column(JSON, nullable=True)        # ["individual", "research_oriented"]

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skills = relationship("CareerSkill", back_populates="career", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="career", cascade="all, delete-orphan")
    market_info = relationship("MarketInfo", back_populates="career", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("CareerRecommendation", back_populates="career", cascade="all, delete-orphan")
    selected_by = relationship("SelectedCareer", back_populates="career", cascade="all, delete-orphan")
    myths = relationship("CareerMyth", back_populates="career", cascade="all, delete-orphan")


class CareerSkill(Base):
    """Detailed skill entry linked to a career."""
    __tablename__ = "career_skills"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False)
    skill_name = Column(String(150), nullable=False)
    skill_type = Column(String(20), nullable=False)   # "required" or "optional"
    importance = Column(Integer, default=5)            # 1-10 scale

    career = relationship("Career", back_populates="skills")


class Exam(Base):
    """Relevant exams / certifications for a career."""
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=True)
    name = Column(String(300), nullable=False)
    category = Column(String(100), nullable=True)      # "Government" / "Certification" / "Entrance"
    conducting_org = Column(String(200), nullable=True)
    eligibility = Column(Text, nullable=True)
    frequency = Column(String(100), nullable=True)     # "Annual" / "Bi-Annual"
    official_website = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    career = relationship("Career", back_populates="exams")


class Scholarship(Base):
    """Scholarship opportunities."""
    __tablename__ = "scholarships"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    provider = Column(String(200), nullable=True)
    eligibility = Column(Text, nullable=True)
    education_level = Column(String(100), nullable=True)  # "B.Tech" / "M.Tech" / "Any"
    application_period = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    official_website = Column(String(500), nullable=True)
    amount = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CareerMyth(Base):
    """Career myths and their reality explanations."""
    __tablename__ = "career_myths"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=True)
    myth = Column(Text, nullable=False)
    reality = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)  # career title or "General"

    career = relationship("Career", back_populates="myths")


class MarketInfo(Base):
    """Market intelligence data for a career (demo/sample labeled)."""
    __tablename__ = "market_info"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"), unique=True, nullable=False)

    demand_level = Column(String(50), nullable=True)        # "Very High" / "High" / "Medium"
    demand_growth_pct = Column(Float, nullable=True)        # e.g., 22.5 (percent)
    top_skills = Column(JSON, nullable=True)                # ["Python", "TensorFlow", ...]
    emerging_technologies = Column(JSON, nullable=True)
    job_openings_india = Column(Integer, nullable=True)     # Approximate count
    top_companies = Column(JSON, nullable=True)             # ["Google", "Amazon", ...]
    industry_trends = Column(JSON, nullable=True)           # list of trend strings
    avg_salary_fresher = Column(Float, nullable=True)
    avg_salary_experienced = Column(Float, nullable=True)
    is_demo_data = Column(Boolean, default=True)            # always true until real API connected
    last_updated = Column(DateTime, default=datetime.utcnow)

    career = relationship("Career", back_populates="market_info")
