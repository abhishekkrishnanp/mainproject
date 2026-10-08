"""
AI Powered Agentic Career Guidance System - Backend Application
────────────────────────────────────────────────────────────────────────────
FastAPI backend providing REST endpoints for:
- Student Registration, Authentication & Profile Management
- Self-Assessment Agent Processing
- Career Recommendation Agent Matching
- Grounded RAG Pipeline & Vector Search
- Skill Gap Analysis
- Personalized Roadmap Generation
"""
from contextlib import asynccontextmanager
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, SessionLocal, get_db
from app.models.user import User
from app.models.career import Career
from app.models.assessment import AssessmentResult
from app.models.recommendation import CareerRecommendation, SelectedCareer
from app.schemas.user import UserCreate, UserLogin, UserOut, UserUpdate, Token
from app.schemas.assessment import AssessmentCreate, AssessmentOut
from app.schemas.career import RecommendationOut, SkillGapOut, RoadmapOut
from app.api.auth import register as auth_register, login as auth_login
from app.api.assessment import submit_assessment as auth_submit_assessment
from app.api import auth, assessment, career, deep_routes
from app.services.career_service import seed_careers
from app.rag.vector_store import vector_store, RAGPipeline
from app.agents.coordinator import coordinator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("career_guidance")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    # Safe migration check for SQLite tables
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        if "users" in inspector.get_table_names():
            user_cols = [c["name"] for c in inspector.get_columns("users")]
            with engine.connect() as conn:
                if "user_id" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN user_id VARCHAR(100)"))
                if "password_hash" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
                if "role" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'student'"))
                if "updated_at" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN updated_at DATETIME"))
                conn.commit()
    except Exception as e:
        logger.warning(f"Database column inspection note: {e}")

    # Seed career knowledge base if empty
    db = SessionLocal()
    try:
        seed_careers(db)
        # Initialize RAG vector store with seeded careers
        careers = db.query(Career).all()
        vector_store.build_index(careers)
        logger.info(f"Vector Store initialized with {len(careers)} careers.")
    except Exception as e:
        logger.error(f"Error during database startup / seeding: {e}")
    finally:
        db.close()

    yield
    logger.info("Shutting down career guidance backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Powered Agentic Career Guidance System API for BTech AI & Data Science Project",
    lifespan=lifespan,
)

# ─── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Prefixed API Routers ──────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication & Profile"])
app.include_router(assessment.router, prefix="/api/v1/assessment", tags=["Self-Assessment Agent"])
app.include_router(career.router, prefix="/api/v1/career", tags=["Career Agent, RAG & Roadmap"])
app.include_router(deep_routes.router, tags=["ACGS Core Deep Modules"])
app.include_router(deep_routes.router, prefix="/api/v1", tags=["ACGS Core Deep Modules (v1)"])


# ─── Root Level Endpoints (as specified in Milestone Requirements) ─────────────
@app.get("/", tags=["Health"])
def root_status():
    return {
        "status": "online",
        "system": "AI Powered Agentic Career Guidance System",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


@app.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, tags=["Milestone Endpoints"])
def register_student(user_in: UserCreate, db: Session = Depends(get_db)):
    """Student Registration (Milestone Alias)."""
    return auth_register(user_in, db)


@app.post("/login", response_model=Token, tags=["Milestone Endpoints"])
def login_student(credentials: UserLogin, db: Session = Depends(get_db)):
    """Student Login (Milestone Alias)."""
    return auth_login(credentials, db)


@app.get("/profile/{student_id}", response_model=UserOut, tags=["Milestone Endpoints"])
def get_student_profile(student_id: int, db: Session = Depends(get_db)):
    """Get student profile by ID."""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    return student


@app.put("/profile/{student_id}", response_model=UserOut, tags=["Milestone Endpoints"])
def update_student_profile(student_id: int, update_in: UserUpdate, db: Session = Depends(get_db)):
    """Update student profile details."""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    update_data = update_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(student, field, val)

    db.commit()
    db.refresh(student)
    return student


from fastapi import FastAPI, Depends, HTTPException, status, Header
from app.core.security import decode_access_token


def resolve_student_id(explicit_id: Optional[int], authorization: Optional[str]) -> int:
    """Resolve student ID from explicit argument or JWT Authorization header."""
    if authorization and "Bearer " in authorization:
        token = authorization.split("Bearer ")[-1].strip()
        payload = decode_access_token(token)
        if isinstance(payload, dict) and "sub" in payload:
            try:
                return int(payload["sub"])
            except (ValueError, TypeError):
                return explicit_id or 1
        elif isinstance(payload, (int, str)):
            try:
                return int(payload)
            except (ValueError, TypeError):
                return explicit_id or 1
    return explicit_id or 1


@app.post("/assessment", response_model=AssessmentOut, status_code=status.HTTP_201_CREATED, tags=["Milestone Endpoints"])
def run_assessment(
    assessment_in: AssessmentCreate,
    student_id: Optional[int] = None,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Self-Assessment questionnaire processing and student profiling."""
    target_id = resolve_student_id(student_id, authorization)
    user = db.query(User).filter(User.id == target_id).first()
    if not user:
        user = User(
            id=target_id,
            email=f"student.{target_id}@btech.edu",
            hashed_password="mockhashedpassword123",
            full_name=f"Student {target_id}",
            education_level="B.Tech AI & Data Science",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    from app.services.assessment_service import process_assessment
    answers_dicts = [a.model_dump() for a in assessment_in.answers]
    return process_assessment(db, user.id, answers_dicts)


@app.get("/assessment/{student_id}", response_model=AssessmentOut, tags=["Milestone Endpoints"])
def get_student_assessment(student_id: int, db: Session = Depends(get_db)):
    """Retrieve completed assessment for a student."""
    result = db.query(AssessmentResult).filter_by(user_id=student_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Assessment not found for this student.")
    return result


class CareerRecommendIn(BaseModel):
    student_id: Optional[int] = 1


@app.post("/career/recommend", response_model=List[RecommendationOut], tags=["Milestone Endpoints"])
def recommend_careers(
    payload: Optional[CareerRecommendIn] = None,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Recommend top 5 careers for a student profile using Career Recommendation Agent."""
    explicit_id = payload.student_id if payload else None
    student_id = resolve_student_id(explicit_id, authorization)
    assessment = db.query(AssessmentResult).filter_by(user_id=student_id).first()
    if not assessment:
        raise HTTPException(status_code=400, detail="Please complete self-assessment before generating recommendations.")

    from app.api.career import _generate_recommendations
    saved = _generate_recommendations(db, student_id, assessment)

    result = []
    for rec in saved[:5]:  # Top 5
        career_obj = db.query(Career).filter(Career.id == rec.career_id).first()
        from app.schemas.career import CareerOut
        result.append(RecommendationOut(
            id=rec.id,
            career_id=rec.career_id,
            career_title=career_obj.title if career_obj else "Unknown",
            match_score=rec.match_score,
            interest_match=rec.interest_match,
            skill_match=rec.skill_match,
            education_match=rec.education_match,
            goal_match=rec.goal_match,
            work_pref_match=rec.work_pref_match,
            reasons=rec.reasons,
            rank=rec.rank,
            career=CareerOut.model_validate(career_obj) if career_obj else None,
        ))
    return result


class SkillGapRequest(BaseModel):
    student_id: Optional[int] = None
    career_id: Optional[int] = None


@app.post("/career/skill-gap", response_model=SkillGapOut, tags=["Milestone Endpoints"])
def analyze_skill_gap(
    payload: Optional[SkillGapRequest] = None,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Run Skill Gap Analysis between student skills and required career skills."""
    explicit_id = payload.student_id if payload else None
    student_id = resolve_student_id(explicit_id, authorization)
    target_id = payload.career_id if payload else None
    if not target_id:
        sel = db.query(SelectedCareer).filter_by(user_id=student_id).first()
        if sel:
            target_id = sel.career_id
        else:
            top_rec = db.query(CareerRecommendation).filter_by(user_id=student_id).order_by(CareerRecommendation.rank).first()
            target_id = top_rec.career_id if top_rec else 1

    career_obj = db.query(Career).filter(Career.id == target_id).first()
    if not career_obj:
        raise HTTPException(status_code=404, detail="Career not found.")

    assessment = db.query(AssessmentResult).filter_by(user_id=student_id).first()
    student_skills: Dict[str, float] = (assessment.skill_scores or {}) if assessment else {}

    student = db.query(User).filter(User.id == student_id).first()
    if student and student.current_skills:
        for s in student.current_skills.split(","):
            s_clean = s.strip()
            if s_clean and s_clean.lower() not in student_skills:
                student_skills[s_clean.lower()] = 80.0

    gap_data = coordinator.run_skill_gap(student_skills, career_obj)

    from app.models.roadmap import SkillGap
    sg = db.query(SkillGap).filter_by(user_id=student_id, career_id=target_id).first()
    if not sg:
        db.query(SkillGap).filter_by(user_id=student_id).delete()
        sg = SkillGap(user_id=student_id, career_id=target_id)
        db.add(sg)

    sg.strong_skills = gap_data.get("strong_skills", [])
    sg.skills_to_improve = gap_data.get("skills_to_improve", [])
    sg.missing_skills = gap_data.get("missing_skills", [])
    sg.overall_readiness = gap_data.get("overall_readiness", 0.0)
    db.commit()
    db.refresh(sg)

    return SkillGapOut(
        user_id=student_id,
        career_id=career_obj.id,
        career_title=career_obj.title,
        strong_skills=sg.strong_skills or [],
        skills_to_improve=sg.skills_to_improve or [],
        missing_skills=sg.missing_skills or [],
        overall_readiness=sg.overall_readiness or 0.0,
    )


class RoadmapRequest(BaseModel):
    student_id: Optional[int] = None
    career_id: Optional[int] = None


@app.post("/career/roadmap", response_model=RoadmapOut, tags=["Milestone Endpoints"])
def generate_career_roadmap(
    payload: Optional[RoadmapRequest] = None,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Generate personalized learning roadmap for student based on skill gaps."""
    explicit_id = payload.student_id if payload else None
    student_id = resolve_student_id(explicit_id, authorization)
    target_id = payload.career_id if payload else None
    if not target_id:
        sel = db.query(SelectedCareer).filter_by(user_id=student_id).first()
        if sel:
            target_id = sel.career_id
        else:
            top_rec = db.query(CareerRecommendation).filter_by(user_id=student_id).order_by(CareerRecommendation.rank).first()
            target_id = top_rec.career_id if top_rec else 1

    career_obj = db.query(Career).filter(Career.id == target_id).first()
    if not career_obj:
        raise HTTPException(status_code=404, detail="Career not found.")

    assessment = db.query(AssessmentResult).filter_by(user_id=student_id).first()
    student_skills: Dict[str, float] = (assessment.skill_scores or {}) if assessment else {}
    student = db.query(User).filter(User.id == student_id).first()
    if student and student.current_skills:
        for s in student.current_skills.split(","):
            s_clean = s.strip()
            if s_clean and s_clean.lower() not in student_skills:
                student_skills[s_clean.lower()] = 80.0

    gap_data = coordinator.run_skill_gap(student_skills, career_obj)
    stages = coordinator.run_roadmap(career_obj, gap_data)

    from app.models.roadmap import Roadmap, RoadmapItem
    from app.schemas.career import RoadmapItemOut

    db.query(Roadmap).filter_by(user_id=student_id).delete()
    roadmap = Roadmap(
        user_id=student_id,
        career_id=career_obj.id,
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
        user_id=student_id,
        career_id=career_obj.id,
        career_title=career_obj.title,
        total_stages=roadmap.total_stages,
        completed_stages=roadmap.completed_stages,
        items=[RoadmapItemOut.model_validate(it) for it in saved_items],
    )


class RAGQueryIn(BaseModel):
    query: str
    top_k: int = 3


class RAGQueryOut(BaseModel):
    query: str
    response: str
    retrieved_careers: List[str]
    context: str
    sources: List[Dict[str, Any]]


@app.post("/rag/query", response_model=RAGQueryOut, tags=["Milestone Endpoints"])
def rag_query_endpoint(body: RAGQueryIn, db: Session = Depends(get_db)):
    """RAG endpoint to retrieve grounded career information and generate AI response."""
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
