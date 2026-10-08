from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.career import Career
from app.models.assessment import AssessmentResult
from app.models.recommendation import CareerRecommendation, SelectedCareer
from app.models.roadmap import SkillGap, Roadmap, RoadmapItem
from app.schemas.career import (
    CareerOut, RecommendationOut, CareerSelectIn, SelectedCareerOut,
    ComparisonOut, ComparisonCareerData, SkillGapOut, RoadmapOut, RoadmapItemOut
)
from app.agents.coordinator import coordinator
from app.core.deps import get_current_active_user

router = APIRouter()


# ─── List all careers ─────────────────────────────────────────────────────────
@router.get("", response_model=List[CareerOut])
def list_careers(db: Session = Depends(get_db)):
    """Return all careers in the database."""
    return db.query(Career).all()


# ─── Single career ────────────────────────────────────────────────────────────
@router.get("/{career_id}", response_model=CareerOut)
def get_career(career_id: int, db: Session = Depends(get_db)):
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found.")
    return career


# ─── Recommendations ─────────────────────────────────────────────────────────
@router.get("/recommendations/list", response_model=List[RecommendationOut])
def get_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get career recommendations for the current user.
    Re-generates from the latest assessment profile if not cached,
    or returns cached recommendations.
    """
    # Check for cached recommendations
    existing = (
        db.query(CareerRecommendation)
        .filter_by(user_id=current_user.id)
        .order_by(CareerRecommendation.rank)
        .all()
    )

    # Check if assessment exists
    assessment = db.query(AssessmentResult).filter_by(user_id=current_user.id).first()
    if not assessment:
        raise HTTPException(
            status_code=400,
            detail="Please complete the self-assessment before viewing recommendations."
        )

    # Regenerate if no cached recommendations
    if not existing:
        existing = _generate_recommendations(db, current_user.id, assessment)

    result = []
    for rec in existing:
        career = db.query(Career).filter(Career.id == rec.career_id).first()
        rec_out = RecommendationOut(
            id=rec.id,
            career_id=rec.career_id,
            career_title=career.title if career else "Unknown",
            match_score=rec.match_score,
            interest_match=rec.interest_match,
            skill_match=rec.skill_match,
            education_match=rec.education_match,
            goal_match=rec.goal_match,
            work_pref_match=rec.work_pref_match,
            reasons=rec.reasons,
            rank=rec.rank,
            career=CareerOut.model_validate(career) if career else None,
        )
        result.append(rec_out)
    return result


def _generate_recommendations(db: Session, user_id: int, assessment: AssessmentResult):
    """Internal: Run career agent and persist recommendations."""
    profile = {
        "interest_scores": assessment.interest_scores or {},
        "skill_scores": assessment.skill_scores or {},
        "personality_scores": assessment.personality_scores or {},
        "goal_scores": assessment.goal_scores or {},
        "interest_area": assessment.interest_area,
        "career_preferences": assessment.career_preferences or [],
        "education_level": "b.tech",  # default; user profile can override
    }

    careers = db.query(Career).all()
    recommendations = coordinator.run_career_recommendations(profile, careers)

    # Delete old
    db.query(CareerRecommendation).filter_by(user_id=user_id).delete()

    saved = []
    for rec in recommendations[:10]:  # top 10
        r = CareerRecommendation(
            user_id=user_id,
            career_id=rec["career_id"],
            match_score=rec["match_score"],
            interest_match=rec.get("interest_match"),
            skill_match=rec.get("skill_match"),
            education_match=rec.get("education_match"),
            goal_match=rec.get("goal_match"),
            work_pref_match=rec.get("work_pref_match"),
            reasons=rec.get("reasons", []),
            rank=rec.get("rank", 0),
        )
        db.add(r)
        saved.append(r)

    db.commit()
    return saved


# ─── Select career ────────────────────────────────────────────────────────────
@router.post("/select", status_code=status.HTTP_200_OK)
def select_career(
    career_in: CareerSelectIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Set the user's selected career. Clears old skill gap, roadmap, simulation."""
    career = db.query(Career).filter(Career.id == career_in.career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found.")

    # Upsert selected career
    existing = db.query(SelectedCareer).filter_by(user_id=current_user.id).first()
    if existing:
        if existing.career_id != career_in.career_id:
            # Career changed — clear downstream data
            from app.models.roadmap import SkillGap, Roadmap
            from app.models.simulation import SimulationRun
            db.query(SkillGap).filter_by(user_id=current_user.id).delete()
            db.query(Roadmap).filter_by(user_id=current_user.id).delete()
            db.query(SimulationRun).filter_by(user_id=current_user.id).delete()
        existing.career_id = career_in.career_id
    else:
        sel = SelectedCareer(user_id=current_user.id, career_id=career_in.career_id)
        db.add(sel)

    db.commit()
    return {"message": f"Career '{career.title}' selected successfully.", "career_id": career.id}


@router.get("/selected/me", response_model=SelectedCareerOut)
def get_selected_career(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Return the user's currently selected career."""
    sel = db.query(SelectedCareer).filter_by(user_id=current_user.id).first()
    if not sel:
        raise HTTPException(status_code=404, detail="No career selected yet.")
    career = db.query(Career).filter(Career.id == sel.career_id).first()
    return SelectedCareerOut(
        career_id=sel.career_id,
        career=CareerOut.model_validate(career),
        selected_at=sel.selected_at,
    )


# ─── Career Comparison ────────────────────────────────────────────────────────
@router.get("/compare/careers", response_model=ComparisonOut)
def compare_careers(
    ids: str = Query(..., description="Comma-separated career IDs, e.g. 1,2,3"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Compare multiple careers side by side."""
    from app.models.roadmap import SkillGap
    try:
        career_ids = [int(x.strip()) for x in ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid career IDs format. Use comma-separated integers.")

    result = []
    assessment = db.query(AssessmentResult).filter_by(user_id=current_user.id).first()
    student_skills = (assessment.skill_scores or {}) if assessment else {}

    for cid in career_ids:
        career = db.query(Career).filter(Career.id == cid).first()
        if not career:
            continue
        gap = coordinator.run_skill_gap(student_skills, career)
        result.append(ComparisonCareerData(
            career_id=career.id,
            career_title=career.title,
            required_skills=career.required_skills or [],
            required_degree=career.required_degree,
            salary_beginner=career.salary_beginner,
            salary_senior=career.salary_senior,
            career_growth=career.career_growth,
            work_type=career.work_type,
            industries=career.industries or [],
            skill_gap_count=len(gap.get("missing_skills", [])),
        ))

    return ComparisonOut(careers=result)


# ─── Skill Gap Analysis ───────────────────────────────────────────────────────
class CareerSkillGapIn(BaseModel):
    career_id: Optional[int] = None

@router.get("/skill-gap/me", response_model=SkillGapOut)
@router.post("/skill-gap", response_model=SkillGapOut)
def get_skill_gap(
    payload: Optional[CareerSkillGapIn] = None,
    career_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Calculate and return skill gap analysis for selected or specified career."""
    target_id = None
    if payload and payload.career_id:
        target_id = payload.career_id
    elif career_id:
        target_id = career_id
    else:
        sel = db.query(SelectedCareer).filter_by(user_id=current_user.id).first()
        if sel:
            target_id = sel.career_id
        else:
            top_rec = db.query(CareerRecommendation).filter_by(user_id=current_user.id).order_by(CareerRecommendation.rank).first()
            if top_rec:
                target_id = top_rec.career_id
            else:
                first_c = db.query(Career).first()
                if first_c:
                    target_id = first_c.id
                else:
                    raise HTTPException(status_code=404, detail="No careers found.")

    career = db.query(Career).filter(Career.id == target_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found.")

    assessment = db.query(AssessmentResult).filter_by(user_id=current_user.id).first()
    student_skills: Dict[str, float] = (assessment.skill_scores or {}) if assessment else {}

    if current_user.current_skills:
        for s in current_user.current_skills.split(","):
            s_clean = s.strip()
            if s_clean and s_clean.lower() not in student_skills:
                student_skills[s_clean.lower()] = 80.0

    gap_data = coordinator.run_skill_gap(student_skills, career)

    sg = db.query(SkillGap).filter_by(user_id=current_user.id, career_id=target_id).first()
    if not sg:
        db.query(SkillGap).filter_by(user_id=current_user.id).delete()
        sg = SkillGap(user_id=current_user.id, career_id=target_id)
        db.add(sg)

    sg.strong_skills = gap_data.get("strong_skills", [])
    sg.skills_to_improve = gap_data.get("skills_to_improve", [])
    sg.missing_skills = gap_data.get("missing_skills", [])
    sg.overall_readiness = gap_data.get("overall_readiness", 0.0)
    db.commit()
    db.refresh(sg)

    return SkillGapOut(
        user_id=current_user.id,
        career_id=career.id,
        career_title=career.title,
        strong_skills=sg.strong_skills or [],
        skills_to_improve=sg.skills_to_improve or [],
        missing_skills=sg.missing_skills or [],
        overall_readiness=sg.overall_readiness or 0.0,
    )


# ─── Personalized Roadmap ─────────────────────────────────────────────────────
class CareerRoadmapIn(BaseModel):
    career_id: Optional[int] = None

@router.get("/roadmap/me", response_model=RoadmapOut)
@router.post("/roadmap", response_model=RoadmapOut)
def get_roadmap(
    payload: Optional[CareerRoadmapIn] = None,
    career_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Generate a personalized learning roadmap based on skill gaps."""
    target_id = None
    if payload and payload.career_id:
        target_id = payload.career_id
    elif career_id:
        target_id = career_id
    else:
        sel = db.query(SelectedCareer).filter_by(user_id=current_user.id).first()
        if sel:
            target_id = sel.career_id
        else:
            top_rec = db.query(CareerRecommendation).filter_by(user_id=current_user.id).order_by(CareerRecommendation.rank).first()
            if top_rec:
                target_id = top_rec.career_id
            else:
                first_c = db.query(Career).first()
                if first_c:
                    target_id = first_c.id
                else:
                    raise HTTPException(status_code=404, detail="No careers found.")

    career = db.query(Career).filter(Career.id == target_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found.")

    assessment = db.query(AssessmentResult).filter_by(user_id=current_user.id).first()
    student_skills: Dict[str, float] = (assessment.skill_scores or {}) if assessment else {}
    if current_user.current_skills:
        for s in current_user.current_skills.split(","):
            s_clean = s.strip()
            if s_clean and s_clean.lower() not in student_skills:
                student_skills[s_clean.lower()] = 80.0

    gap_data = coordinator.run_skill_gap(student_skills, career)
    stages = coordinator.run_roadmap(career, gap_data)

    db.query(Roadmap).filter_by(user_id=current_user.id).delete()
    roadmap = Roadmap(
        user_id=current_user.id,
        career_id=career.id,
        total_stages=len(stages),
        completed_stages=0,
    )
    db.add(roadmap)
    db.flush()

    saved_items = []
    for s in stages:
        item = RoadmapItem(
            roadmap_id=roadmap.id,
            stage_number=s.get("stage_number", 1),
            stage_title=s.get("stage_title", "Stage"),
            description=s.get("description", ""),
            skills=s.get("skills", []),
            topics=s.get("topics", []),
            projects=s.get("projects", []),
            resources=s.get("resources", []),
            estimated_duration=s.get("estimated_duration", "4-6 weeks"),
            is_completed=False,
        )
        db.add(item)
        saved_items.append(item)

    db.commit()
    db.refresh(roadmap)

    return RoadmapOut(
        id=roadmap.id,
        user_id=current_user.id,
        career_id=career.id,
        career_title=career.title,
        total_stages=roadmap.total_stages,
        completed_stages=roadmap.completed_stages,
        items=[RoadmapItemOut.model_validate(it) for it in saved_items],
    )


# ─── Grounded RAG Query ───────────────────────────────────────────────────────
class RAGQueryIn(BaseModel):
    query: str
    top_k: int = 3

class RAGQueryOut(BaseModel):
    query: str
    response: str
    retrieved_careers: List[str]
    context: str
    sources: List[Dict[str, Any]]

@router.post("/rag/query", response_model=RAGQueryOut)
def rag_career_query(
    body: RAGQueryIn,
    db: Session = Depends(get_db),
):
    """Retrieve grounded career guidance from knowledge base using RAG."""
    from app.rag.vector_store import RAGPipeline, vector_store
    
    if not vector_store.documents:
        careers = db.query(Career).all()
        vector_store.build_index(careers)

    retrieved = RAGPipeline.retrieve(body.query, top_k=body.top_k)
    context = RAGPipeline.format_context(retrieved)
    answer = RAGPipeline.generate(body.query, context, retrieved)

    retrieved_titles = [item["career"]["title"] for item in retrieved]
    sources = [{"career": item["career"]["title"], "score": item["score"]} for item in retrieved]

    return RAGQueryOut(
        query=body.query,
        response=answer,
        retrieved_careers=retrieved_titles,
        context=context,
        sources=sources,
    )
