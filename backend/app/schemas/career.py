from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


# ─── Career ───────────────────────────────────────────────────────────────────

class CareerOut(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str] = None
    required_degree: Optional[str] = None
    required_skills: Optional[List[str]] = None
    optional_skills: Optional[List[str]] = None
    salary_beginner: Optional[float] = None
    salary_mid: Optional[float] = None
    salary_senior: Optional[float] = None
    career_growth: Optional[str] = None
    work_type: Optional[str] = None
    industries: Optional[List[str]] = None
    job_roles: Optional[List[str]] = None

    model_config = {"from_attributes": True}


# ─── Recommendations ──────────────────────────────────────────────────────────

class RecommendationOut(BaseModel):
    id: int
    career_id: int
    career_title: str
    match_score: float
    interest_match: Optional[float] = None
    skill_match: Optional[float] = None
    education_match: Optional[float] = None
    goal_match: Optional[float] = None
    work_pref_match: Optional[float] = None
    reasons: Optional[List[str]] = None
    rank: Optional[int] = None
    # Embed career details for convenience
    career: Optional[CareerOut] = None

    model_config = {"from_attributes": True}


# ─── Career Selection ─────────────────────────────────────────────────────────

class CareerSelectIn(BaseModel):
    career_id: int


class SelectedCareerOut(BaseModel):
    career_id: int
    career: CareerOut
    selected_at: datetime

    model_config = {"from_attributes": True}


# ─── Skill Gap ────────────────────────────────────────────────────────────────

class SkillEntry(BaseModel):
    skill: str
    status: str   # Strong / Intermediate / Needs Improvement / Missing


class SkillGapOut(BaseModel):
    user_id: int
    career_id: int
    career_title: str
    strong_skills: List[SkillEntry] = []
    skills_to_improve: List[SkillEntry] = []
    missing_skills: List[SkillEntry] = []
    overall_readiness: float = 0.0

    model_config = {"from_attributes": True}


# ─── Roadmap ──────────────────────────────────────────────────────────────────

class ResourceItem(BaseModel):
    name: str
    url: Optional[str] = None
    type: Optional[str] = None  # "Course" / "Book" / "Video"


class RoadmapItemOut(BaseModel):
    id: int
    stage_number: int
    stage_title: str
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    resources: Optional[List[ResourceItem]] = None
    estimated_duration: Optional[str] = None
    is_completed: bool = False

    model_config = {"from_attributes": True}


class RoadmapOut(BaseModel):
    id: int
    user_id: int
    career_id: int
    career_title: str
    total_stages: int
    completed_stages: int
    items: List[RoadmapItemOut] = []

    model_config = {"from_attributes": True}


class RoadmapProgressIn(BaseModel):
    item_id: int
    is_completed: bool


# ─── Simulation ───────────────────────────────────────────────────────────────

class SimulationYearOut(BaseModel):
    year: int
    job_title: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    skills_acquired: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    promotion_note: Optional[str] = None

    model_config = {"from_attributes": True}


class SimulationOut(BaseModel):
    career_title: str
    disclaimer: str = (
        "⚠️ This is an estimated career simulation based on industry trends and sample data. "
        "Actual career progression may vary based on individual performance, market conditions, "
        "and other factors. This is NOT a guaranteed prediction."
    )
    years: List[SimulationYearOut] = []

    model_config = {"from_attributes": True}


# ─── Market ───────────────────────────────────────────────────────────────────

class MarketInfoOut(BaseModel):
    career_title: str
    demand_level: Optional[str] = None
    demand_growth_pct: Optional[float] = None
    top_skills: Optional[List[str]] = None
    emerging_technologies: Optional[List[str]] = None
    job_openings_india: Optional[int] = None
    top_companies: Optional[List[str]] = None
    industry_trends: Optional[List[str]] = None
    avg_salary_fresher: Optional[float] = None
    avg_salary_experienced: Optional[float] = None
    is_demo_data: bool = True
    data_notice: str = "📊 This data is sample/demo data for demonstration purposes. Real-time market data can be connected via external APIs."

    model_config = {"from_attributes": True}


# ─── Exam ─────────────────────────────────────────────────────────────────────

class ExamOut(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    conducting_org: Optional[str] = None
    eligibility: Optional[str] = None
    frequency: Optional[str] = None
    official_website: Optional[str] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Scholarship ──────────────────────────────────────────────────────────────

class ScholarshipOut(BaseModel):
    id: int
    name: str
    provider: Optional[str] = None
    eligibility: Optional[str] = None
    education_level: Optional[str] = None
    application_period: Optional[str] = None
    description: Optional[str] = None
    official_website: Optional[str] = None
    amount: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Career Myth ─────────────────────────────────────────────────────────────

class CareerMythOut(BaseModel):
    id: int
    myth: str
    reality: str
    category: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Feasibility ─────────────────────────────────────────────────────────────

class FeasibilityOut(BaseModel):
    career_title: str
    overall_feasibility: str      # "High" / "Medium" / "Low"
    readiness_score: float        # 0-100
    strengths: List[str] = []
    challenges: List[str] = []
    action_items: List[str] = []
    timeline_estimate: str = ""
    summary: str = ""


# ─── Comparison ──────────────────────────────────────────────────────────────

class ComparisonCareerData(BaseModel):
    career_id: int
    career_title: str
    required_skills: List[str] = []
    required_degree: Optional[str] = None
    salary_beginner: Optional[float] = None
    salary_senior: Optional[float] = None
    career_growth: Optional[str] = None
    work_type: Optional[str] = None
    industries: List[str] = []
    skill_gap_count: int = 0


class ComparisonOut(BaseModel):
    careers: List[ComparisonCareerData] = []
