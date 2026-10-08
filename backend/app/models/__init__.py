# app/models/__init__.py
from app.models.user import User
from app.models.assessment import AssessmentResult, AssessmentAnswer
from app.models.career import Career, CareerSkill, Exam, Scholarship, CareerMyth, MarketInfo
from app.models.roadmap import Roadmap, RoadmapItem, SkillGap, StudentSkill
from app.models.simulation import SimulationRun, SimulationYear
from app.models.recommendation import CareerRecommendation, SelectedCareer

from app.models.student_profile import StudentProfile
from app.models.parent_account import ParentAccount
from app.models.deep_assessment import (
    Assessment,
    AssessmentResponse,
    CareerProfile,
    CareerRecommendationRecord,
)

__all__ = [
    "User",
    "StudentProfile",
    "ParentAccount",
    "Assessment",
    "AssessmentResponse",
    "CareerProfile",
    "CareerRecommendationRecord",
    "AssessmentResult", "AssessmentAnswer",
    "Career", "CareerSkill", "Exam", "Scholarship", "CareerMyth", "MarketInfo",
    "Roadmap", "RoadmapItem", "SkillGap", "StudentSkill",
    "SimulationRun", "SimulationYear",
    "CareerRecommendation", "SelectedCareer",
]
