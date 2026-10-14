"""
Gemini AI Endpoints for Career Guidance System
────────────────────────────────────────────────────────────────────────────
Exposes dedicated REST API endpoints for:
1. Career Recommendations based on interests and skills
2. Personalized Career Roadmap Generation
3. Skill-Gap Analysis
4. Career Question Answering (Students and Parents)
5. Career Myth Clarification
6. Gemini Status / Healthcheck (Never reveals API key)
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.llm_service import llm_service

router = APIRouter(prefix="/gemini", tags=["Gemini Career Guidance"])


# ──────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas for Validation
# ──────────────────────────────────────────────────────────────────────────────

class GeminiStatusResponse(BaseModel):
    configured: bool
    model: str
    sdk_installed: bool
    provider: str


class RecommendationsRequest(BaseModel):
    interests: List[str] = Field(default=[], description="List of user interests or domains")
    skills: List[str] = Field(default=[], description="List of current skills")
    education_level: Optional[str] = Field(default="Undergraduate", max_length=100)
    aspirations: Optional[str] = Field(default=None, max_length=500)


class RoadmapRequest(BaseModel):
    target_career: str = Field(..., min_length=2, max_length=150, description="Target career title")
    current_skills: List[str] = Field(default=[], description="Skills student already possesses")
    timeline_months: int = Field(default=6, ge=1, le=24, description="Target duration in months")


class SkillGapRequest(BaseModel):
    target_career: str = Field(..., min_length=2, max_length=150)
    student_skills: List[str] = Field(default=[])


class CareerQARequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    role: Optional[str] = Field(default="student", pattern="^(student|parent)$")
    education_level: Optional[str] = Field(default="College Student", max_length=100)
    branch: Optional[str] = Field(default=None, max_length=100)


class MythClarificationRequest(BaseModel):
    career_or_topic: str = Field(..., min_length=2, max_length=150)


# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/status", response_model=GeminiStatusResponse)
async def get_gemini_status():
    """
    Check if the Gemini integration is active, configured, and what model is selected.
    Safe endpoint: Does not expose the GEMINI_API_KEY.
    """
    return llm_service.get_status()


@router.post("/recommendations")
async def generate_career_recommendations(req: RecommendationsRequest):
    """
    Feature 1: Career recommendations based on student interests and skills.
    Powered by Google Gemini with graceful heuristic fallback.
    """
    try:
        result = await llm_service.recommend_careers_with_llm(
            interests=req.interests,
            skills=req.skills,
            education_level=req.education_level or "Undergraduate",
            aspirations=req.aspirations
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/roadmap")
async def generate_personalized_roadmap(req: RoadmapRequest):
    """
    Feature 2: Personalized career roadmap generation.
    Generates structured milestone plans for a given career and timeline.
    """
    try:
        result = await llm_service.generate_roadmap_with_llm(
            target_career=req.target_career,
            current_skills=req.current_skills,
            timeline_months=req.timeline_months
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate roadmap: {str(e)}"
        )


@router.post("/skill-gap")
async def generate_skill_gap_analysis(req: SkillGapRequest):
    """
    Feature 3: Skill-gap analysis.
    Identifies missing required competencies vs nice-to-haves and provides priority order.
    """
    try:
        result = await llm_service.analyze_skill_gap_with_llm(
            target_career=req.target_career,
            student_skills=req.student_skills
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze skill gap: {str(e)}"
        )


@router.post("/qa")
async def career_question_answering(req: CareerQARequest):
    """
    Feature 4: Career-related question answering.
    Context-aware guidance for students and empathetic guidance for parents.
    """
    try:
        result = await llm_service.answer_career_question(
            question=req.question,
            user_role=req.role or "student",
            student_context={
                "education_level": req.education_level,
                "branch": req.branch
            }
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process career question: {str(e)}"
        )


@router.post("/myth-buster")
async def clarify_career_myths(req: MythClarificationRequest):
    """
    Feature 5: Career information and myth clarification.
    Debunks misconceptions and provides evidence-based takeaways.
    """
    try:
        result = await llm_service.clarify_career_myths(
            career_or_topic=req.career_or_topic
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clarify career myths: {str(e)}"
        )
