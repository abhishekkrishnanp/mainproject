"""
ACGS Deep Endpoints for Phase 1 (First 35-40%)
Includes Authentication, Student Mode, Parent Mode (Read-Only),
Deep Conversational Self-Assessment Chatbot, and Agent Placeholders.
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.parent_account import ParentAccount
from app.models.deep_assessment import (
    Assessment,
    AssessmentResponse,
    CareerProfile,
    CareerRecommendationRecord,
)
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_student_id,
    generate_parent_id,
    generate_parent_pin,
)
from app.schemas.deep_schemas import (
    StudentRegisterRequest,
    StudentRegisterResponse,
    StudentLoginRequest,
    ParentLoginRequest,
    StudentProfileOut,
    StudentProfileUpdate,
    AssessmentStartResponse,
    AssessmentMessageRequest,
    AssessmentMessageResponse,
    AssessmentStatusResponse,
    AssessmentHistoryResponse,
    CareerProfileResponse,
    ParentStudentSummaryResponse,
)
from app.agents.self_assessment_agent import self_assessment_agent
from app.agents.market_agent import MarketIntelligenceAgent
from app.agents.skill_gap_agent import SkillGapAgent
from app.agents.roadmap_agent import RoadmapAgent
from app.agents.feasibility_agent import FeasibilityAgent

router = APIRouter()

market_agent = MarketIntelligenceAgent()
skill_gap_agent = SkillGapAgent()
roadmap_agent = RoadmapAgent()
feasibility_agent = FeasibilityAgent()


# ─── Auth Resolution Helper ───

def get_current_student_id(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> str:
    """Extract authenticated student_id from JWT token or fallback."""
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication token required.")
    
    token = authorization.split("Bearer ")[-1].strip()
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

    role = payload.get("role", "student")
    if role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student privileges required.")

    student_id = payload.get("student_id")
    if student_id:
        return str(student_id)

    # If sub was numeric user ID, look up student profile
    sub = payload.get("sub")
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == int(sub)).first()
    if profile:
        return profile.student_id

    return f"ACGS-STU-{sub}"


# ─── MODULE 2: Student Authentication ───

@router.post("/auth/register", response_model=StudentRegisterResponse, status_code=status.HTTP_201_CREATED)
def register_student(req: StudentRegisterRequest, db: Session = Depends(get_db)):
    """
    Student registration endpoint.
    Collects User ID, Password, Confirm Password, Student name, Email, Phone, Parent WhatsApp.
    Generates unique student_id, unique parent_id, and secure 6-digit parent_pin.
    """
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    # Check for existing user
    existing_user_id = db.query(User).filter(User.user_id == req.user_id).first()
    if existing_user_id:
        raise HTTPException(status_code=400, detail="User ID already exists. Please choose a different ID.")

    existing_email = db.query(User).filter(User.email == req.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email is already registered.")

    # Generate IDs and PIN
    student_id = generate_student_id()
    parent_id = generate_parent_id()
    parent_pin = generate_parent_pin(6)

    # Hash passwords
    password_hash = get_password_hash(req.password)
    parent_pin_hash = get_password_hash(parent_pin)

    # Create User record
    user = User(
        user_id=req.user_id,
        email=req.email,
        full_name=req.name,
        hashed_password=password_hash,
        password_hash=password_hash,
        role="student",
        education_level=req.education_level,
    )
    db.add(user)
    db.flush()

    # Create StudentProfile record
    profile = StudentProfile(
        user_id=user.id,
        student_id=student_id,
        name=req.name,
        email=req.email,
        phone=req.phone,
        parent_whatsapp=req.parent_whatsapp,
        education_level=req.education_level,
        current_class_or_year=req.current_class_or_year,
        stream=req.stream,
        branch=req.branch,
        department=req.department,
        university=req.university,
        cgpa_percentage=req.cgpa_percentage,
    )
    db.add(profile)

    # Create ParentAccount record
    parent_acc = ParentAccount(
        student_id=student_id,
        parent_id=parent_id,
        parent_pin_hash=parent_pin_hash,
    )
    db.add(parent_acc)
    db.commit()

    # Create JWT access token
    access_token = create_access_token(
        subject=user.id,
        role="student",
        extra_claims={"student_id": student_id, "user_id": req.user_id, "name": req.name},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return StudentRegisterResponse(
        message="Student registration successful.",
        access_token=access_token,
        student_id=student_id,
        parent_id=parent_id,
        parent_pin=parent_pin,
        user_id=req.user_id,
        name=req.name,
        email=req.email,
    )


@router.post("/auth/login")
def login_student(req: StudentLoginRequest, db: Session = Depends(get_db)):
    """
    Student login using user_id or email, and password.
    Returns JWT token and profile info.
    """
    user = db.query(User).filter(
        (User.user_id == req.user_id) | (User.email == req.user_id)
    ).first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect User ID or password.",
        )

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    student_id = profile.student_id if profile else f"ACGS-STU-{user.id}"

    # Get parent_id if exists
    parent_acc = db.query(ParentAccount).filter(ParentAccount.student_id == student_id).first()
    parent_id = parent_acc.parent_id if parent_acc else None

    access_token = create_access_token(
        subject=user.id,
        role="student",
        extra_claims={
            "student_id": student_id,
            "user_id": user.user_id or str(user.id),
            "name": user.full_name,
            "email": user.email,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": "student",
        "student_id": student_id,
        "user_id": user.user_id or str(user.id),
        "name": user.full_name,
        "email": user.email,
        "parent_id": parent_id,
        "education_level": profile.education_level if profile else user.education_level,
    }


# ─── MODULE 3: Student Profile ───

@router.get("/student/profile", response_model=StudentProfileOut)
def get_current_student_profile(
    student_id: str = Depends(get_current_student_id), db: Session = Depends(get_db)
):
    """Retrieve authenticated student's profile."""
    profile = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
    if not profile:
        user = db.query(User).filter(User.id == 1).first()
        return StudentProfileOut(
            id=1,
            user_id="student_user",
            student_id=student_id,
            name=user.full_name if user else "Student",
            email=user.email if user else "student@btech.edu",
            education_level="College Student",
        )

    user = db.query(User).filter(User.id == profile.user_id).first()
    parent_acc = db.query(ParentAccount).filter(ParentAccount.student_id == student_id).first()

    return StudentProfileOut(
        id=profile.id,
        user_id=user.user_id if user and user.user_id else str(profile.user_id),
        student_id=profile.student_id,
        name=profile.name,
        email=profile.email,
        phone=profile.phone,
        parent_whatsapp=profile.parent_whatsapp,
        education_level=profile.education_level,
        current_class_or_year=profile.current_class_or_year,
        stream=profile.stream,
        branch=profile.branch,
        department=profile.department,
        university=profile.university,
        cgpa_percentage=profile.cgpa_percentage,
        parent_id=parent_acc.parent_id if parent_acc else None,
    )


@router.put("/student/profile", response_model=StudentProfileOut)
def update_current_student_profile(
    update_data: StudentProfileUpdate,
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db),
):
    """Update student profile details."""
    profile = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    for field, val in update_data.model_dump(exclude_unset=True).items():
        setattr(profile, field, val)

    db.commit()
    db.refresh(profile)

    user = db.query(User).filter(User.id == profile.user_id).first()
    parent_acc = db.query(ParentAccount).filter(ParentAccount.student_id == student_id).first()

    return StudentProfileOut(
        id=profile.id,
        user_id=user.user_id if user and user.user_id else str(profile.user_id),
        student_id=profile.student_id,
        name=profile.name,
        email=profile.email,
        phone=profile.phone,
        parent_whatsapp=profile.parent_whatsapp,
        education_level=profile.education_level,
        current_class_or_year=profile.current_class_or_year,
        stream=profile.stream,
        branch=profile.branch,
        department=profile.department,
        university=profile.university,
        cgpa_percentage=profile.cgpa_percentage,
        parent_id=parent_acc.parent_id if parent_acc else None,
    )


# ─── MODULE 4: Parent Mode (Strictly READ ONLY) ───

@router.post("/parent/login")
def login_parent(req: ParentLoginRequest, db: Session = Depends(get_db)):
    """
    Parent authentication using Parent ID and secure Parent PIN.
    Returns read-only parent JWT token.
    """
    account = db.query(ParentAccount).filter(ParentAccount.parent_id == req.parent_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Parent ID or Parent PIN.",
        )

    if not verify_password(req.parent_pin, account.parent_pin_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Parent ID or Parent PIN.",
        )

    # Get student name
    profile = db.query(StudentProfile).filter(StudentProfile.student_id == account.student_id).first()
    student_name = profile.name if profile else "Student"

    access_token = create_access_token(
        subject=account.parent_id,
        role="parent",
        extra_claims={
            "parent_id": account.parent_id,
            "student_id": account.student_id,
            "student_name": student_name,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": "parent",
        "is_read_only": True,
        "parent_id": account.parent_id,
        "student_id": account.student_id,
        "student_name": student_name,
    }


@router.get("/parent/student-summary", response_model=ParentStudentSummaryResponse)
def get_parent_student_summary(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    """
    Parent Dashboard Data (READ ONLY).
    Parents CANNOT edit assessment answers, modify student profile, or take the assessment.
    """
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(status_code=401, detail="Parent authorization token required.")

    token = authorization.split("Bearer ")[-1].strip()
    payload = decode_access_token(token)
    if not payload or payload.get("role") != "parent":
        raise HTTPException(status_code=403, detail="Parent READ ONLY access required.")

    student_id = payload.get("student_id")
    parent_id = payload.get("parent_id")

    profile = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
    student_name = profile.name if profile else "Student"

    # Get Assessment info
    assessment = db.query(Assessment).filter(Assessment.student_id == student_id).order_by(Assessment.id.desc()).first()
    assessment_status = assessment.status if assessment else "not_started"
    current_q = assessment.current_question if assessment else 0
    total_q = assessment.total_questions if assessment else 25

    # Get CareerProfile
    career_profile = db.query(CareerProfile).filter(CareerProfile.student_id == student_id).first()
    recs = db.query(CareerRecommendationRecord).filter(CareerRecommendationRecord.student_id == student_id).order_by(CareerRecommendationRecord.match_score.desc()).all()

    rec_list = []
    for r in recs:
        rec_list.append({
            "career_name": r.career_name,
            "match_score": r.match_score,
            "reason": r.reason,
            "supporting_evidence": r.supporting_evidence or [],
            "concerns": r.concerns or [],
            "skills_needed": r.skills_needed or [],
        })

    return ParentStudentSummaryResponse(
        is_read_only=True,
        student_name=student_name,
        student_id=student_id,
        parent_id=parent_id,
        education_level=profile.education_level if profile else None,
        current_class_or_year=profile.current_class_or_year if profile else None,
        stream_or_branch=profile.branch or profile.stream if profile else None,
        university=profile.university if profile else None,
        assessment_status=assessment_status,
        assessment_progress={
            "current_question": current_q,
            "total_questions": total_q,
            "percent_complete": round((current_q / max(total_q, 1)) * 100) if assessment else 0,
        },
        personality_profile=career_profile.personality_profile if career_profile else None,
        skills_profile=career_profile.skills_profile if career_profile else None,
        interest_profile=career_profile.interest_profile if career_profile else None,
        career_recommendations=rec_list if rec_list else None,
    )


# ─── MODULE 5 & 6 & 8: Deep Conversational Self-Assessment Chatbot ───

@router.post("/assessment/start", response_model=AssessmentStartResponse)
def start_deep_assessment(
    student_id: str = Depends(get_current_student_id), db: Session = Depends(get_db)
):
    """
    Start or resume a deep conversational career assessment session.
    """
    # Look for existing active session
    active = db.query(Assessment).filter(
        Assessment.student_id == student_id, Assessment.status == "in_progress"
    ).order_by(Assessment.id.desc()).first()

    if active and active.assessment_state:
        # Resume active session
        state = active.assessment_state
        next_q = self_assessment_agent.engine.get_next_question(state)
        return AssessmentStartResponse(
            assessment_id=active.id,
            student_id=student_id,
            status=active.status,
            current_question=next_q,
            total_questions=active.total_questions,
            message="Resuming your in-progress self-discovery assessment interview.",
        )

    # Initialize new session
    session_data = self_assessment_agent.start_new_session(student_id)
    state = session_data["state"]
    first_q = session_data["current_question"]

    assessment = Assessment(
        student_id=student_id,
        status="in_progress",
        current_question=0,
        total_questions=state.get("total_questions_planned", 25),
        assessment_state=state,
        started_at=datetime.utcnow(),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return AssessmentStartResponse(
        assessment_id=assessment.id,
        student_id=student_id,
        status=assessment.status,
        current_question=first_q,
        total_questions=assessment.total_questions,
        message=session_data["message"],
    )


@router.post("/assessment/message", response_model=AssessmentMessageResponse)
async def send_assessment_message(
    req: AssessmentMessageRequest,
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db),
):
    """
    Processes an answer from the student, saves it, and retrieves the next adaptive question.
    If assessment is complete, synthesizes the Personality & Interest profiles and top 5 career matches.
    """
    assessment = None
    if req.assessment_id:
        assessment = db.query(Assessment).filter(Assessment.id == req.assessment_id).first()

    if not assessment:
        assessment = db.query(Assessment).filter(
            Assessment.student_id == student_id, Assessment.status == "in_progress"
        ).order_by(Assessment.id.desc()).first()

    if not assessment:
        raise HTTPException(status_code=400, detail="No active assessment found. Please start assessment first.")

    state = assessment.assessment_state or self_assessment_agent.engine.get_initial_state(student_id)

    # Reconstruct question_def from bank or req
    current_q_def = self_assessment_agent.engine.get_next_question(state)
    if not current_q_def:
        current_q_def = {
            "question_id": req.question_id or f"q_{len(state.get('previous_answers', []))}",
            "question_text": req.question_text or "Answer",
            "phase": "general",
        }

    # Save answer to database table ASSESSMENT_RESPONSES
    response_rec = AssessmentResponse(
        assessment_id=assessment.id,
        question_id=current_q_def.get("question_id", "q"),
        question_text=current_q_def.get("question_text", ""),
        answer=req.answer,
        answer_type="option" if current_q_def.get("options") else "text",
        phase=current_q_def.get("phase", "general"),
    )
    db.add(response_rec)

    # Process with SelfAssessmentAgent
    result = await self_assessment_agent.handle_student_response(
        student_id=student_id,
        current_state=state,
        answer_text=req.answer,
        question_def=current_q_def,
    )

    new_state = result["state"]
    is_completed = result["is_completed"]
    next_q = result["next_question"]
    profile_data = result["profile"]

    from sqlalchemy.orm.attributes import flag_modified
    import copy

    # Update Assessment session in DB
    assessment.assessment_state = copy.deepcopy(new_state)
    flag_modified(assessment, "assessment_state")
    assessment.current_question = len(new_state.get("previous_answers", []))
    assessment.total_questions = new_state.get("total_questions_planned", 25)

    if is_completed:
        assessment.status = "completed"
        assessment.completed_at = datetime.utcnow()

        # Persist CareerProfile table
        if profile_data:
            existing_prof = db.query(CareerProfile).filter(CareerProfile.student_id == student_id).first()
            if not existing_prof:
                existing_prof = CareerProfile(student_id=student_id)
                db.add(existing_prof)

            existing_prof.personality_profile = profile_data.get("personality_profile")
            existing_prof.interest_profile = profile_data.get("interest_profile")
            existing_prof.skills_profile = profile_data.get("skills_profile")
            existing_prof.values_profile = profile_data.get("values_profile")
            existing_prof.confidence_profile = profile_data.get("confidence_profile")

            # Persist Top 5 Career Recommendations
            db.query(CareerRecommendationRecord).filter(CareerRecommendationRecord.student_id == student_id).delete()
            for rec in profile_data.get("career_recommendations", []):
                rec_row = CareerRecommendationRecord(
                    student_id=student_id,
                    career_name=rec.get("career_name"),
                    match_score=rec.get("match_score", 0.0),
                    reason=rec.get("reason", ""),
                    supporting_evidence=rec.get("supporting_evidence", []),
                    concerns=rec.get("concerns", []),
                    skills_needed=rec.get("skills_needed", []),
                )
                db.add(rec_row)

    db.commit()
    db.refresh(assessment)

    return AssessmentMessageResponse(
        assessment_id=assessment.id,
        status=assessment.status,
        is_completed=is_completed,
        conversational_prefix=result.get("conversational_prefix", ""),
        next_question=next_q,
        current_step=len(new_state.get("previous_answers", [])),
        total_steps=new_state.get("total_questions_planned", 25),
        profile=profile_data,
    )


@router.get("/assessment/status", response_model=AssessmentStatusResponse)
def get_assessment_status(
    student_id: str = Depends(get_current_student_id), db: Session = Depends(get_db)
):
    """Retrieve current assessment progress and status."""
    assessment = db.query(Assessment).filter(Assessment.student_id == student_id).order_by(Assessment.id.desc()).first()
    career_prof = db.query(CareerProfile).filter(CareerProfile.student_id == student_id).first()

    if not assessment:
        return AssessmentStatusResponse(
            student_id=student_id,
            status="not_started",
            current_step=0,
            total_steps=25,
            has_profile=bool(career_prof),
        )

    return AssessmentStatusResponse(
        assessment_id=assessment.id,
        student_id=student_id,
        status=assessment.status,
        current_step=assessment.current_question,
        total_steps=assessment.total_questions,
        has_profile=bool(career_prof),
        started_at=assessment.started_at.isoformat() if assessment.started_at else None,
        completed_at=assessment.completed_at.isoformat() if assessment.completed_at else None,
    )


@router.get("/assessment/history", response_model=AssessmentHistoryResponse)
def get_assessment_history(
    student_id: str = Depends(get_current_student_id), db: Session = Depends(get_db)
):
    """Retrieve full history of questions and responses answered by the student."""
    assessment = db.query(Assessment).filter(Assessment.student_id == student_id).order_by(Assessment.id.desc()).first()
    if not assessment:
        return AssessmentHistoryResponse(
            student_id=student_id,
            status="not_started",
            total_responses=0,
            responses=[],
        )

    responses = db.query(AssessmentResponse).filter(AssessmentResponse.assessment_id == assessment.id).order_by(AssessmentResponse.id.asc()).all()

    resp_list = []
    for r in responses:
        resp_list.append({
            "question_id": r.question_id,
            "question_text": r.question_text,
            "answer": r.answer,
            "phase": r.phase,
            "created_at": r.created_at.isoformat(),
        })

    return AssessmentHistoryResponse(
        student_id=student_id,
        assessment_id=assessment.id,
        status=assessment.status,
        total_responses=len(resp_list),
        responses=resp_list,
    )


@router.get("/career-profile", response_model=CareerProfileResponse)
def get_student_career_profile(
    student_id: str = Depends(get_current_student_id), db: Session = Depends(get_db)
):
    """Retrieve the generated 10-dimension Personality Profile and Top 5 matches."""
    profile = db.query(CareerProfile).filter(CareerProfile.student_id == student_id).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Career profile not generated yet. Please complete the self-assessment first.",
        )

    recs = db.query(CareerRecommendationRecord).filter(
        CareerRecommendationRecord.student_id == student_id
    ).order_by(CareerRecommendationRecord.match_score.desc()).all()

    rec_list = []
    for r in recs:
        rec_list.append({
            "career_name": r.career_name,
            "match_score": r.match_score,
            "reason": r.reason,
            "supporting_evidence": r.supporting_evidence or [],
            "concerns": r.concerns or [],
            "skills_needed": r.skills_needed or [],
        })

    return CareerProfileResponse(
        student_id=student_id,
        personality_profile=profile.personality_profile,
        interest_profile=profile.interest_profile,
        skills_profile=profile.skills_profile,
        values_profile=profile.values_profile,
        confidence_profile=profile.confidence_profile,
        career_recommendations=rec_list,
    )


# ─── MODULE 10: Future Agent API Placeholders ───

@router.post("/market-analysis", tags=["Future Agents"])
def placeholder_market_analysis(data: Dict[str, Any] = {}):
    """Placeholder interface for Market Intelligence Agent (Phase 2)."""
    return {
        "status": "placeholder_ready_for_phase_2",
        "agent": "MarketIntelligenceAgent",
        "message": "Market Intelligence with live Tavily search will be enabled in Phase 2.",
        "input_echo": data,
    }


@router.post("/skill-gap", tags=["Future Agents"])
def placeholder_skill_gap(data: Dict[str, Any] = {}):
    """Placeholder interface for Skill Gap Analyst Agent (Phase 3)."""
    return {
        "status": "placeholder_ready_for_phase_3",
        "agent": "SkillGapAgent",
        "message": "Skill Gap Analyst Agent curriculum mapping will be expanded in Phase 3.",
        "input_echo": data,
    }


@router.post("/roadmap", tags=["Future Agents"])
def placeholder_roadmap(data: Dict[str, Any] = {}):
    """Placeholder interface for Career Roadmap Generator Agent (Phase 4)."""
    return {
        "status": "placeholder_ready_for_phase_4",
        "agent": "RoadmapAgent",
        "message": "12-24 month dynamic roadmap generation will be fully expanded in Phase 4.",
        "input_echo": data,
    }


@router.post("/feasibility", tags=["Future Agents"])
def placeholder_feasibility(data: Dict[str, Any] = {}):
    """Placeholder interface for Feasibility Evaluator Agent (Phase 5)."""
    return {
        "status": "placeholder_ready_for_phase_5",
        "agent": "FeasibilityAgent",
        "message": "Feasibility evaluation and risk modeling will be fully expanded in Phase 5.",
        "input_echo": data,
    }


# ─── Dual-Mode Assistant Chatbot (Student & Parent) ───

from pydantic import BaseModel as PydanticBase


class AssistantChatRequest(PydanticBase):
    message: str
    mode: str = "student"  # "student" or "parent"
    student_name: Optional[str] = None
    education_level: Optional[str] = None
    current_page: Optional[str] = None


@router.post("/assistant/chat", tags=["AI Assistant"])
async def assistant_chat_endpoint(req: AssistantChatRequest):
    """
    Intelligent Assistant Chatbot for both Students and Parents.
    Provides empathetic, domain-rich career guidance, platform navigation,
    and parental advisory. Supports Kerala, Indian, and Global context.
    """
    user_msg = req.message.strip()
    mode = req.mode.lower()
    lowered = user_msg.lower()

    # 1. Try Gemini LLM if configured
    from app.services.llm_service import llm_service
    if llm_service.is_configured():
        if mode == "parent":
            sys_inst = (
                "You are the ACGS Parent Advisory Assistant for the AI-Powered Agentic Career Guidance System. "
                "Your role is to support parents with empathy and clear, non-technical explanations. "
                "Help them understand modern careers (AI, Data Science, Software, Cloud, Core Engineering), "
                "advise them on supporting their child without undue pressure, explain the job market in Kerala "
                "(Technopark Thiruvananthapuram, Infopark Kochi) and India, and remind them that the guidance is student-first. "
                "Keep responses warm, concise, and structured (under 120 words)."
            )
        else:
            sys_inst = (
                "You are the ACGS Student Guidance Assistant for the AI-Powered Agentic Career Guidance System. "
                "Your role is to empower students (school, college, postgrad) with career insights, explain the self-assessment interview, "
                "recommend skills (Python, SQL, DSA, AI), suggest paths after B.Tech/School, discuss higher studies (GATE/MS/MBA), "
                "and explain job ecosystems in Kerala (Technopark, Infopark) and globally. "
                "Keep responses encouraging, practical, and clear (under 120 words)."
            )

        prompt = f"User asks: {user_msg}\nStudent details: Name: {req.student_name or 'Student'}, Level: {req.education_level or 'College'}"
        llm_reply = await llm_service.generate_response(prompt, sys_inst)
        if llm_reply:
            return {"reply": llm_reply.strip(), "mode": mode, "source": "gemini"}

    # 2. Intelligent Contextual Fallback Engine
    reply = ""
    if mode == "parent":
        if any(w in lowered for w in ["read only", "edit", "change", "alter"]):
            reply = (
                "🔒 **Parent Access is Read-Only by Design**:\n"
                "To ensure authentic self-discovery, students answer the discovery interview independently. "
                "As a parent, you can view your child's personality profile, skills, and top career matches, "
                "which provides a transparent foundation for constructive, supportive family discussions."
            )
        elif any(w in lowered for w in ["ai", "data science", "machine learning"]):
            reply = (
                "🤖 **Understanding AI & Data Careers**:\n"
                "Artificial Intelligence and Data Science are among the fastest-growing fields globally and in India. "
                "Professionals in these roles analyze patterns, automate complex decisions, and build smart software. "
                "In Kerala, major firms in Technopark (Thiruvananthapuram) and Infopark (Kochi) actively hire for these roles."
            )
        elif any(w in lowered for w in ["job", "salary", "market", "demand", "kerala", "placement"]):
            reply = (
                "💼 **Job Market & Career Security**:\n"
                "Technology and data careers offer strong long-term growth and competitive compensation. "
                "Kerala's IT hubs (Technopark & Infopark) host over 800+ tech companies, while hubs like Bangalore and Hyderabad "
                "offer vast product opportunities. The best career security comes from strong foundational problem-solving skills."
            )
        elif any(w in lowered for w in ["score", "dimension", "personality", "meaning"]):
            reply = (
                "📊 **Understanding Personality Scores**:\n"
                "The 10-dimension personality profile reflects working styles and cognitive preferences (e.g., Analytical, Creative, Collaboration), "
                "NOT psychological diagnoses. A higher analytical score indicates affinity for logic and data, while high collaboration suggests teamwork strength."
            )
        elif any(w in lowered for w in ["support", "help", "guide", "pressure"]):
            reply = (
                "🌱 **How Parents Can Best Support**:\n"
                "1. **Listen first**: Ask your child what excited them about their top career matches.\n"
                "2. **Encourage exploration**: Support building practical projects and internships.\n"
                "3. **Focus on effort**: Career readiness takes continuous learning rather than immediate perfection."
            )
        else:
            reply = (
                "👋 **Parent Guidance Assistant**:\n"
                "I am here to help you understand your child's career options, the job market (in Kerala and globally), "
                "and how to interpret the assessment results. Feel free to ask about any specific career field, salary trends, or how to support your child!"
            )
    else:  # Student mode
        if any(w in lowered for w in ["assessment", "interview", "start", "how"]):
            reply = (
                "🧭 **How the Discovery Interview Works**:\n"
                "Our autonomous Self-Assessment Agent conducts a deep 25–40 interaction interview. "
                "It starts by understanding whether you are in school, college, or working, then asks follow-ups about your favorite subjects, "
                "project interests, problem-solving style, and career goals to synthesize your personalized profile."
            )
        elif any(w in lowered for w in ["kerala", "technopark", "infopark", "local"]):
            reply = (
                "🌴 **Tech Opportunities in Kerala**:\n"
                "Kerala has an expanding tech ecosystem with Technopark in Thiruvananthapuram, Infopark in Kochi, and Cyberpark in Kozhikode. "
                "Leading MNCs (UST, TCS, Infosys, IBS) as well as product startups offer excellent entry points in Full-Stack, Cloud, and AI."
            )
        elif any(w in lowered for w in ["skill", "python", "learn", "prepare"]):
            reply = (
                "⚡ **Top Skills to Build Right Now**:\n"
                "1. **Programming**: Master Python or JavaScript with data structures fundamentals.\n"
                "2. **Data & SQL**: Practice relational querying and basic data analysis.\n"
                "3. **Projects**: Build and publish 2-3 end-to-end projects on GitHub to prove your capabilities."
            )
        elif any(w in lowered for w in ["gate", "higher study", "ms", "cat", "mba"]):
            reply = (
                "🎓 **Higher Studies vs Placements**:\n"
                "- **M.Tech via GATE**: Ideal for deep specialization and research in premier institutes (IITs/IISc/NITs).\n"
                "- **MS Abroad**: Great for global exposure and research in AI or Systems.\n"
                "- **MBA via CAT**: Best if you lean toward tech product management or consulting.\n"
                "- **Campus Placements**: Excellent for immediate practical industry experience."
            )
        elif any(w in lowered for w in ["confused", "which career", "recommend"]):
            reply = (
                "💡 **Finding Your Direction**:\n"
                "Career confusion is completely natural! The best step is to complete the 25-question Self-Assessment interview. "
                "It evaluates your analytical, creative, and interpersonal strengths to generate your Top 5 matched career pathways."
            )
        else:
            reply = (
                "🚀 **Student Guidance Assistant**:\n"
                "I'm your AI career companion! You can ask me about different tech careers, skills to learn, how the assessment works, "
                "higher studies vs campus jobs, or opportunities across Kerala and India."
            )

    return {"reply": reply, "mode": mode, "source": "knowledge_engine"}

