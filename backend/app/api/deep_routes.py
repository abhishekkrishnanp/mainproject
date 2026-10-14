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


def get_optional_student_id(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> str:
    """Extract authenticated student_id or return default demo student if unauthenticated."""
    if authorization and "Bearer " in authorization:
        try:
            return get_current_student_id(authorization, db)
        except Exception:
            pass
    first_profile = db.query(StudentProfile).first()
    if first_profile:
        return first_profile.student_id
    return "ACGS-STU-DEFAULT"


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
        id=user.id,
        student_id=student_id,
        parent_id=parent_id,
        parent_pin=parent_pin,
        user_id=req.user_id,
        name=req.name,
        full_name=req.name,
        email=req.email,
        education_level=req.education_level,
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
        "id": user.id,
        "student_id": student_id,
        "user_id": user.user_id or str(user.id),
        "name": user.full_name,
        "full_name": user.full_name,
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

    # Get Selected Career if any
    selected_career_title = None
    user_id_val = profile.user_id if profile else None
    if user_id_val:
        sel_rec = db.query(SelectedCareer).filter(SelectedCareer.user_id == user_id_val).first()
        if sel_rec:
            sel_c = db.query(Career).filter(Career.id == sel_rec.career_id).first()
            if sel_c:
                selected_career_title = sel_c.title

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
        selected_career=selected_career_title,
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
        hist = state.get("conversation_history", [])
        from app.services.dynamic_assessment_engine import INITIAL_QUESTION
        next_q = INITIAL_QUESTION
        asked = state.get("previously_asked_questions", [])
        if asked and len(asked) > len(hist):
            next_q = {
                "question_id": f"dyn_q_{len(hist) + 1}",
                "question_text": asked[-1],
                "options": [],
                "phase": "specialization",
            }
        return AssessmentStartResponse(
            assessment_id=active.id,
            student_id=student_id,
            status=active.status,
            current_question=next_q,
            total_questions=active.total_questions or 8,
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

    # Reconstruct question_def
    current_q_def = {
        "question_id": req.question_id or f"dyn_q_{len(state.get('conversation_history', []))}",
        "question_text": req.question_text or "Career Assessment Question",
        "phase": "specialization",
        "options": [],
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
    current_step_val = result.get("current_step", len(new_state.get("conversation_history", [])))
    total_steps_val = result.get("total_steps", 8)
    assessment.current_question = current_step_val
    assessment.total_questions = total_steps_val

    if is_completed:
        assessment.status = "completed"
        assessment.completed_at = datetime.utcnow()

        # Persist CareerProfile & CareerRecommendationRecord
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

            # Persist recommendations to CareerRecommendationRecord
            db.query(CareerRecommendationRecord).filter_by(student_id=student_id).delete()
            for rec in profile_data.get("career_recommendations", []):
                rec_record = CareerRecommendationRecord(
                    student_id=student_id,
                    career_name=rec.get("career_name", "Specialized Career"),
                    match_score=float(rec.get("match_score", 85.0)),
                    reason=rec.get("reason", "Tailored match from deep discovery interview."),
                    supporting_evidence=rec.get("supporting_evidence", []),
                    concerns=rec.get("concerns", []),
                    skills_needed=rec.get("skills_needed", []),
                    suggested_projects=rec.get("suggested_projects", []),
                    immediate_next_steps=rec.get("immediate_next_steps", []),
                    roadmap_stages=rec.get("roadmap_stages", []),
                )
                db.add(rec_record)

            # Sync to AssessmentResult, CareerRecommendation, SkillGap & Roadmap
            from app.models.assessment import AssessmentResult
            from app.models.recommendation import CareerRecommendation
            from app.models.roadmap import SkillGap as SkillGapModel, Roadmap as RoadmapModel, RoadmapItem as RoadmapItemModel

            user_obj = db.query(User).filter(User.user_id == student_id).first()
            if not user_obj:
                profile_row = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
                if profile_row:
                    user_obj = db.query(User).filter(User.id == profile_row.user_id).first()

            if user_obj:
                traits = profile_data.get("personality_profile", {})
                interest_scores = profile_data.get("interest_profile", {})
                skills_data = profile_data.get("skills_profile", {})
                confirmed_skills = skills_data.get("confirmed_skills", [])
                missing_skills = skills_data.get("missing_skills", [])

                skill_scores_map: Dict[str, float] = {}
                for sk in confirmed_skills:
                    skill_scores_map[sk.lower()] = 85.0
                for sk in skills_data.get("self_reported_skills", []):
                    if sk.lower() not in skill_scores_map:
                        skill_scores_map[sk.lower()] = 65.0
                for sk in missing_skills:
                    if sk.lower() not in skill_scores_map:
                        skill_scores_map[sk.lower()] = 30.0

                ar = db.query(AssessmentResult).filter_by(user_id=user_obj.id).first()
                if not ar:
                    ar = AssessmentResult(user_id=user_obj.id)
                    db.add(ar)
                    db.flush()

                ar.interest_scores = interest_scores
                ar.personality_scores = {k.lower(): v for k, v in traits.items() if isinstance(v, (int, float))}
                ar.skill_scores = skill_scores_map or {"analytical reasoning": 80.0, "problem solving": 75.0}
                ar.interest_area = list(interest_scores.keys())[0] if interest_scores else "Specialized Engineering"
                ar.strong_skills = confirmed_skills or ["Problem Solving", "Analytical Thinking"]
                ar.work_preference = "Collaborative / Innovation"
                ar.career_preferences = [r.get("career_name") for r in profile_data.get("career_recommendations", [])[:3]]

                # Seed/update CareerRecommendation records
                db.query(CareerRecommendation).filter_by(user_id=user_obj.id).delete()
                top_match_career_id = 1
                for rank_idx, rec in enumerate(profile_data.get("career_recommendations", []), 1):
                    c_title = rec.get("career_name", "")
                    base_title = rec.get("base_career", "")
                    c_match = (
                        db.query(Career).filter(Career.title == c_title).first() or
                        db.query(Career).filter(Career.title == base_title).first() or
                        db.query(Career).first()
                    )
                    if c_match:
                        if rank_idx == 1:
                            top_match_career_id = c_match.id
                        c_rec = CareerRecommendation(
                            user_id=user_obj.id,
                            career_id=c_match.id,
                            match_score=float(rec.get("match_score", 75.0)),
                            interest_match=min(98.0, float(rec.get("match_score", 75.0)) + 2.0),
                            skill_match=max(50.0, float(rec.get("match_score", 75.0)) - 8.0),
                            education_match=90.0,
                            goal_match=85.0,
                            work_pref_match=80.0,
                            reasons=[rec.get("reason", f"High alignment based on your interview answers in {c_title}")],
                            rank=rank_idx,
                        )
                        db.add(c_rec)

                # Seed personalized SkillGap and Roadmap for top match
                top_rec = profile_data.get("career_recommendations", [])[0] if profile_data.get("career_recommendations") else None
                if top_rec:
                    db.query(SkillGapModel).filter_by(user_id=user_obj.id).delete()
                    sg = SkillGapModel(
                        user_id=user_obj.id,
                        career_id=top_match_career_id,
                        strong_skills=confirmed_skills or ["Core Foundations"],
                        skills_to_improve=skills_data.get("self_reported_skills", []),
                        missing_skills=missing_skills or top_rec.get("skills_needed", []),
                        overall_readiness=float(top_rec.get("match_score", 75.0)),
                    )
                    db.add(sg)

                    roadmap_stages = top_rec.get("roadmap_stages", [])
                    if roadmap_stages:
                        db.query(RoadmapModel).filter_by(user_id=user_obj.id).delete()
                        new_roadmap = RoadmapModel(
                            user_id=user_obj.id,
                            career_id=top_match_career_id,
                            total_stages=len(roadmap_stages),
                            completed_stages=0,
                        )
                        db.add(new_roadmap)
                        db.flush()

                        for s_idx, st in enumerate(roadmap_stages, 1):
                            item = RoadmapItemModel(
                                roadmap_id=new_roadmap.id,
                                stage_number=st.get("stage_number", s_idx),
                                stage_title=st.get("stage_title", f"Stage {s_idx}"),
                                description=st.get("description", ""),
                                skills=st.get("skills", []),
                                topics=st.get("topics", []),
                                projects=st.get("projects", []),
                                resources=st.get("resources", []),
                                estimated_duration=st.get("estimated_duration", "4-6 weeks"),
                                is_completed=False,
                            )
                            db.add(item)

    db.commit()
    db.refresh(assessment)

    return AssessmentMessageResponse(
        assessment_id=assessment.id,
        status=assessment.status,
        is_completed=is_completed,
        conversational_prefix=result.get("conversational_prefix", ""),
        next_question=next_q,
        current_step=current_step_val,
        total_steps=total_steps_val,
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


# ─── MODULE 10: Multi-Agent Pipeline Endpoints & Intelligence ───

from app.models.career import Career, Exam, Scholarship, CareerMyth, MarketInfo
from app.models.roadmap import SkillGap as SkillGapModel, Roadmap as RoadmapModel, RoadmapItem as RoadmapItemModel
from app.models.recommendation import SelectedCareer

@router.post("/market-analysis", tags=["Five-Agent Intelligence Pipeline"])
async def run_market_intelligence(
    data: Dict[str, Any] = {},
    db: Session = Depends(get_db),
):
    """
    Agent 2: Market Intelligence Agent Endpoint.
    Researches labor market demand, salary ranges, and regional pathways (Kerala, India, Global).
    """
    career_title = data.get("career_title") or data.get("career") or "Machine Learning Engineer"
    location = data.get("location") or "Kerala, India"
    
    report = await market_agent.research_career_market(career_title, user_location_preference=location)
    return report


@router.post("/skill-gap", tags=["Five-Agent Intelligence Pipeline"])
def run_skill_gap_analysis(
    data: Dict[str, Any] = {},
    student_id: str = Depends(get_optional_student_id),
    db: Session = Depends(get_db),
):
    """
    Agent 3: Skill Gap Analyst Agent Endpoint.
    Compares the student's assessed profile against verified job requirements.
    """
    career_title = data.get("career_title")
    career_id = data.get("career_id")
    
    if career_id:
        career = db.query(Career).filter(Career.id == int(career_id)).first()
    elif career_title:
        career = db.query(Career).filter(Career.title == str(career_title)).first()
    else:
        # Default to selected career or top recommended career
        prof = db.query(CareerProfile).filter(CareerProfile.student_id == student_id).first()
        career = db.query(Career).first()

    if not career:
        raise HTTPException(status_code=404, detail="Career target not found.")

    # Load student skills from career profile or user
    prof = db.query(CareerProfile).filter(CareerProfile.student_id == student_id).first()
    student_skills = {}
    if prof and prof.personality_profile:
        # Map assessed traits into skills scores
        for k, v in (prof.personality_profile or {}).items():
            if isinstance(v, (int, float)):
                student_skills[k.lower()] = float(v)

    gap_report = skill_gap_agent.analyze(student_skills, career)
    return gap_report


@router.post("/roadmap", tags=["Five-Agent Intelligence Pipeline"])
def run_roadmap_generation(
    data: Dict[str, Any] = {},
    student_id: str = Depends(get_optional_student_id),
    db: Session = Depends(get_db),
):
    """
    Agent 4: Career Roadmap Generator Agent Endpoint.
    Produces a 12–24 month actionable milestone plan tailored to user's education category.
    """
    career_id = data.get("career_id")
    career_title = data.get("career_title")

    if career_id:
        career = db.query(Career).filter(Career.id == int(career_id)).first()
    elif career_title:
        career = db.query(Career).filter(Career.title == str(career_title)).first()
    else:
        career = db.query(Career).first()

    if not career:
        raise HTTPException(status_code=404, detail="Career not found.")

    prof = db.query(CareerProfile).filter(CareerProfile.student_id == student_id).first()
    student_skills = {}
    if prof and prof.personality_profile:
        for k, v in prof.personality_profile.items():
            if isinstance(v, (int, float)):
                student_skills[k.lower()] = float(v)

    gap = skill_gap_agent.analyze(student_skills, career)
    
    profile_dict = {
        "education_level": data.get("education_level", "College Student")
    }
    stages = roadmap_agent.generate(career, gap, profile_dict)

    return {
        "career_title": career.title,
        "total_stages": len(stages),
        "stages": stages,
        "roadmap_duration": "12–24 Months",
    }


@router.post("/feasibility", tags=["Five-Agent Intelligence Pipeline"])
def run_feasibility_evaluation(
    data: Dict[str, Any] = {},
    student_id: str = Depends(get_optional_student_id),
    db: Session = Depends(get_db),
):
    """
    Agent 5: Feasibility Evaluator Agent Endpoint.
    Evaluates achievability, time to entry, financial budget, and barrier mitigations.
    """
    career_id = data.get("career_id")
    career_title = data.get("career_title")

    if career_id:
        career = db.query(Career).filter(Career.id == int(career_id)).first()
    elif career_title:
        career = db.query(Career).filter(Career.title == str(career_title)).first()
    else:
        career = db.query(Career).first()

    if not career:
        raise HTTPException(status_code=404, detail="Career not found.")

    prof = db.query(CareerProfile).filter(CareerProfile.student_id == student_id).first()
    student_skills = {}
    if prof and prof.personality_profile:
        for k, v in prof.personality_profile.items():
            if isinstance(v, (int, float)):
                student_skills[k.lower()] = float(v)

    gap = skill_gap_agent.analyze(student_skills, career)
    profile_dict = {
        "education_level": data.get("education_level", "College Student"),
        "student_skills": student_skills,
    }

    eval_result = feasibility_agent.evaluate(profile_dict, career, gap)
    return eval_result


# ─── MODULE 11: Career Ecosystem Endpoints (Myths, Scholarships, Exams) ───

@router.get("/myths", tags=["Career Ecosystem"])
def get_career_myths(category: Optional[str] = None, db: Session = Depends(get_db)):
    """Retrieve fact-checked career myths and evidence-based realities."""
    query = db.query(CareerMyth)
    if category and category != "all":
        query = query.filter(CareerMyth.category == category)
    myths = query.all()
    return [
        {
            "id": m.id,
            "myth": m.myth,
            "reality": m.reality,
            "category": m.category or "General",
            "career_id": m.career_id,
        }
        for m in myths
    ]


@router.get("/scholarships", tags=["Career Ecosystem"])
def get_scholarships(education_level: Optional[str] = None, db: Session = Depends(get_db)):
    """Retrieve verified government and institutional scholarships."""
    query = db.query(Scholarship)
    if education_level:
        query = query.filter(Scholarship.education_level.ilike(f"%{education_level}%"))
    results = query.all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "provider": s.provider,
            "eligibility": s.eligibility,
            "education_level": s.education_level,
            "amount": s.amount,
            "application_period": s.application_period,
            "official_website": s.official_website,
            "description": s.description,
        }
        for s in results
    ]


@router.get("/exams", tags=["Career Ecosystem"])
def get_exams(career_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Retrieve entrance examinations and professional certifications."""
    query = db.query(Exam)
    if career_id:
        query = query.filter(Exam.career_id == career_id)
    results = query.all()
    return [
        {
            "id": e.id,
            "name": e.name,
            "category": e.category,
            "conducting_org": e.conducting_org,
            "eligibility": e.eligibility,
            "frequency": e.frequency,
            "official_website": e.official_website,
            "description": e.description,
            "career_id": e.career_id,
        }
        for e in results
    ]


# ─── MODULE 12: Reproducible Evaluation Framework ───

@router.get("/evaluation/run", tags=["System Evaluation"])
def run_system_evaluation(db: Session = Depends(get_db)):
    """
    Run reproducible evaluation benchmark across 100 synthetic student profiles.
    Returns Career Match Relevance, Skill Gap Accuracy, Roadmap Actionability,
    and Operational latency metrics.
    """
    from app.services.evaluation_service import evaluator
    careers = db.query(Career).all()
    results = evaluator.run_benchmark(careers)
    return results


# ─── Dual-Mode Assistant Chatbot (Student & Parent) ───

from pydantic import BaseModel as PydanticBase, Field


class ChatHistoryTurn(PydanticBase):
    role: str = Field(default="user", description="'user' or 'assistant'")
    text: str = Field(default="", max_length=4000)


class AssistantChatRequest(PydanticBase):
    message: str = Field(..., min_length=1, max_length=2500, description="User query")
    mode: str = Field(default="student", pattern="^(student|parent)$")
    student_name: Optional[str] = Field(default=None, max_length=150)
    education_level: Optional[str] = Field(default=None, max_length=150)
    current_page: Optional[str] = Field(default=None, max_length=100)
    history: Optional[List[ChatHistoryTurn]] = Field(default=None, description="Recent conversation turns for follow-up context")


@router.post("/assistant/chat", tags=["AI Assistant"])
async def assistant_chat_endpoint(req: AssistantChatRequest):
    """
    Intelligent Assistant Chatbot for both Students and Parents.
    Provides empathetic, domain-rich career guidance, platform navigation,
    and parental advisory. Maintains conversational context for follow-up queries.
    """
    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    mode = req.mode.lower()
    lowered = user_msg.lower()

    # Convert Pydantic history turns to list of dicts for LLM
    formatted_history = []
    if req.history:
        for turn in req.history:
            formatted_history.append({"role": turn.role, "text": turn.text})

    # 1. Try Gemini LLM via chat_with_history (preserves context and guidelines)
    from app.services.llm_service import llm_service
    if llm_service.is_configured():
        student_ctx = {
            "student_name": req.student_name,
            "education_level": req.education_level,
            "current_page": req.current_page
        }
        llm_reply = await llm_service.chat_with_history(
            current_message=user_msg,
            conversation_history=formatted_history,
            mode=mode,
            student_context=student_ctx
        )
        if llm_reply:
            return {
                "reply": llm_reply.strip(),
                "mode": mode,
                "source": "gemini",
                "has_context": bool(req.history and len(req.history) > 0)
            }

    # 2. Intelligent Contextual & Grounded Knowledge Engine
    # If the user is asking about specific careers, roles, skills, or comparisons,
    # retrieve grounded context from the Career Knowledge Base / RAG pipeline.
    from app.rag.vector_store import vector_store, RAGPipeline
    from app.services.career_service import CAREERS_DATA

    # Ensure vector store is populated
    if not vector_store.documents:
        vector_store.build_index(CAREERS_DATA)

    # Perform semantic search on the query
    retrieved = RAGPipeline.retrieve(user_msg, top_k=2)
    top_career_match = retrieved[0]["career"] if (retrieved and retrieved[0].get("score", 0) > 0.08) else None

    reply = ""
    if mode == "parent":
        if top_career_match and any(w in lowered for w in ["what", "how", "scope", "salary", "future", "career", "about"]):
            c = top_career_match
            reply = (
                f"💼 **Career Overview for Parents: {c['title']}**\n\n"
                f"- **What they do**: {c['description']}\n"
                f"- **Education Path**: Typically requires {c['required_degree']}.\n"
                f"- **Industry Demand**: Growth is rated as **{c.get('career_growth', 'High')}**.\n"
                f"- **Salary Scale in India**: Entry-level starts around ₹{c.get('salary_beginner', 5.0)} LPA and scales to ₹{c.get('salary_senior', 30.0)}+ LPA with experience.\n"
                f"- **Hiring Companies**: Active demand in IT hubs like Technopark (Trivandrum), Infopark (Kochi), and nationwide.\n\n"
                "💡 *Advisory tip*: Encourage your child to focus on building strong foundational skills and hands-on projects rather than immediate exam pressure."
            )
        elif any(w in lowered for w in ["read only", "edit", "change", "alter"]):
            reply = (
                "🔒 **Parent Access is Read-Only by Design**:\n\n"
                "To ensure authentic self-discovery, students complete the assessment independently. "
                "As a parent, you can view your child's personality profile, core competencies, and career matches, "
                "giving you a shared foundation for supportive, non-pressuring family discussions."
            )
        elif any(w in lowered for w in ["ai", "data science", "machine learning"]):
            reply = (
                "🤖 **Understanding AI & Data Careers**:\n\n"
                "Artificial Intelligence and Data Science are among the highest-growth domains globally and in India:\n"
                "- **Key Roles**: AI Engineer, Data Scientist, Machine Learning Specialist.\n"
                "- **Work Involved**: Analyzing business data, building predictive models, and automating smart processes.\n"
                "- **Regional Hubs**: Technopark (Thiruvananthapuram) and Infopark (Kochi) actively recruit for these roles, alongside Bangalore and Hyderabad."
            )
        elif any(w in lowered for w in ["job", "salary", "market", "demand", "kerala", "placement"]):
            reply = (
                "💼 **Job Market & Career Stability**:\n\n"
                "- **Tech Hubs in Kerala**: Over 800+ IT companies operate in Technopark, Infopark, and Cyberpark.\n"
                "- **Career Outlook**: Software, Cloud, and Data domains maintain steady entry-level and lateral hiring demand.\n"
                "- **Best Advice**: Long-term career security is built on problem-solving foundations and curiosity rather than a single specific degree title."
            )
        elif any(w in lowered for w in ["support", "help", "guide", "pressure"]):
            reply = (
                "🌱 **How to Support Your Child's Journey**:\n\n"
                "1. **Listen Actively**: Ask what aspects of their matched careers excite them most.\n"
                "2. **Encourage Hands-on Projects**: Support learning through real-world experiments, hackathons, and internships.\n"
                "3. **Focus on Growth**: Remind them that career paths evolve; adaptability is more valuable than rigid choices."
            )
        else:
            reply = (
                "👋 **Parent Guidance Advisory**:\n\n"
                "I am here to help you understand your child's career pathways. You can ask about:\n"
                "- Specific career tracks (e.g., Software Engineer, Cloud Architect, AI Specialist)\n"
                "- Higher education options (GATE, MS abroad, MBA)\n"
                "- Job market demand and salary outlooks in Kerala and pan-India\n"
                "- How to understand assessment results and support career decisions without pressure."
            )
    else:  # Student mode
        # 1. Grounded Match from Knowledge Base
        if top_career_match and any(w in lowered for w in ["cloud", "ml", "machine learning", "data", "software", "devops", "cyber", "ui", "ux", "product", "analyst", "skills", "become", "roadmap", "salary", "how to"]):
            c = top_career_match
            req_skills = ", ".join(c.get("required_skills", []))
            opt_skills = ", ".join(c.get("optional_skills", []))
            roles = ", ".join(c.get("job_roles", []))

            reply = (
                f"🎯 **Grounded Career Guide: {c['title']}**\n\n"
                f"**Overview**:\n{c['description']}\n\n"
                f"**Core Skills Required**:\n- **Must-Have**: {req_skills}\n- **Recommended / Preferred**: {opt_skills}\n\n"
                f"**Step-by-Step Learning Path**:\n"
                f"1. **Month 1-2 (Foundations)**: Master the primary language (e.g. Python / Linux / SQL) and core tools.\n"
                f"2. **Month 3-4 (Specialization)**: Build practical projects using {', '.join(c.get('required_skills', [])[:3])}.\n"
                f"3. **Month 5-6 (Portfolio & Placements)**: Deploy 2 real-world projects to GitHub and practice technical interviews.\n\n"
                f"**Industry & Compensation Outlook**:\n"
                f"- **Entry-Level**: ₹{c.get('salary_beginner', 5.0)} LPA\n"
                f"- **Experienced**: Up to ₹{c.get('salary_senior', 35.0)}+ LPA\n"
                f"- **Common Roles**: {roles}\n\n"
                f"Would you like recommended certifications or interview questions for {c['title']}?"
            )
        elif any(w in lowered for w in ["compare", "vs", "versus"]):
            reply = (
                "⚖️ **Career Comparison Overview**:\n\n"
                "| Career Track | Core Focus | Key Skills Needed | Growth Outlook |\n"
                "|---|---|---|---|\n"
                "| **AI / Machine Learning** | Predictive models & algorithms | Python, Math/Stats, PyTorch | Rapidly Expanding |\n"
                "| **Full-Stack Development** | Web apps & user interfaces | JavaScript, React, Node/Python | High Steady Demand |\n"
                "| **Cloud & DevOps** | Infrastructure, CI/CD, scalability | AWS/GCP, Docker, Kubernetes, Linux | High Demand |\n"
                "| **Data Analytics** | Business insights & dashboards | SQL, PowerBI, Excel, Python | Strong Across All Sectors |\n\n"
                "Which specific careers would you like a detailed breakdown of?"
            )
        elif any(w in lowered for w in ["roadmap", "steps", "plan", "how to start", "timeline"]):
            reply = (
                "🗺️ **6-Month Career Acceleration Roadmap**:\n\n"
                "1. **Foundations (Month 1-2)**: Master one core language (Python or JavaScript) and foundational Data Structures.\n"
                "2. **Domain Specialization (Month 3-4)**: Learn primary frameworks, relational databases (SQL), and Git version control.\n"
                "3. **Practical Portfolio (Month 5)**: Build and deploy 2 complete end-to-end projects demonstrating problem-solving.\n"
                "4. **Career Readiness (Month 6)**: Resume optimization, technical mock interviews, and applying for internships."
            )
        elif any(w in lowered for w in ["skill", "skills", "learn", "what do i need", "gap"]):
            reply = (
                "⚡ **Top In-Demand Skills to Build**:\n\n"
                "- **Programming & Logic**: Python or TypeScript with clean coding and daily practice (LeetCode / HackerRank).\n"
                "- **Data & Storage**: Relational SQL querying, database schema design, and working with REST APIs.\n"
                "- **Cloud & Version Control**: Git, Docker containerization, and basic deployment on AWS/GCP.\n"
                "- **Professional Skills**: Clear technical articulation, teamwork, and structured problem breakdown."
            )
        elif any(w in lowered for w in ["b.tech", "ai student", "machine learning", "data science"]):
            reply = (
                "🎓 **Guidance for B.Tech AI & Data Science Students**:\n\n"
                "You are in a high-opportunity specialization! To stand out:\n"
                "1. Solidify **Mathematics & Linear Algebra** — they make ML and deep learning intuitive.\n"
                "2. Master core tools: **NumPy, Pandas, Scikit-Learn, PyTorch, SQL**.\n"
                "3. Publish working models on **HuggingFace** and clean code on **GitHub**.\n\n"
                "What specific field within AI excites you most (e.g. Computer Vision, NLP, Generative AI, or Data Engineering)?"
            )
        elif any(w in lowered for w in ["gate", "higher study", "ms", "cat", "mba"]):
            reply = (
                "🎓 **Higher Studies vs Campus Placements**:\n\n"
                "- **GATE (M.Tech/MS)**: Top choice for deep research, R&D roles, and admission into IITs/IISc.\n"
                "- **MS Abroad (US/Europe)**: Ideal for international exposure, specialized AI labs, and global hiring.\n"
                "- **CAT (MBA)**: Strong path if you want to transition into Product Management or Technology Consulting.\n"
                "- **Campus Placements**: Excellent for immediate practical engineering experience and financial independence."
            )
        elif any(w in lowered for w in ["kerala", "technopark", "infopark", "trivandrum", "kochi"]):
            reply = (
                "🌴 **Tech Opportunities in Kerala**:\n\n"
                "- **Technopark (Trivandrum)**: Over 70,000 tech professionals across MNCs like UST, Infosys, TCS, Tata Elxsi.\n"
                "- **Infopark (Kochi)**: Rapidly growing hub with strong product development, fintech, and digital transformation firms.\n"
                "- **Cyberpark (Calicut)**: Emerging tech hub with active startup and software engineering presence."
            )
        elif any(w in lowered for w in ["interview", "resume", "prep", "placement"]):
            reply = (
                "🎯 **Interview Preparation Strategy**:\n\n"
                "1. **Resume**: Keep it to 1 clean page. Prioritize measurable project outcomes over course lists.\n"
                "2. **Coding Round**: Practice 2-3 algorithmic problems daily focusing on arrays, strings, and trees.\n"
                "3. **Core CS Fundamentals**: Review DBMS (SQL queries, indexing), Operating Systems, and OOP concepts.\n"
                "4. **Behavioral**: Prepare 2-3 stories using the STAR method (Situation, Task, Action, Result)."
            )
        else:
            reply = (
                "🚀 **AI Career Guidance Assistant**:\n\n"
                "I am your AI career companion! You can ask me:\n"
                "- **Specific careers**: 'How to become a Cloud Engineer?' or 'What does a Data Scientist do?'\n"
                "- **Step-by-step roadmaps**: 'Give me a roadmap for Machine Learning'\n"
                "- **Comparisons**: 'Compare AI Engineer vs Software Engineer'\n"
                "- **Higher studies**: 'GATE vs Campus Placements'\n"
                "- **Interview tips**: 'How to prepare for campus placements?'"
            )

    return {"reply": reply, "mode": mode, "source": "knowledge_engine"}

