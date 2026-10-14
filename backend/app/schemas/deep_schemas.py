"""
Pydantic schemas for AI-Powered Agentic Career Guidance System (ACGS)
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# ─── Auth & Registration ───

class StudentRegisterRequest(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=50, description="Unique username / user ID")
    name: str = Field(..., min_length=2, max_length=150, description="Full name of student")
    email: EmailStr
    password: str = Field(..., min_length=6, description="Account password")
    confirm_password: str = Field(..., min_length=6, description="Confirm password")
    phone: Optional[str] = None
    parent_whatsapp: Optional[str] = None
    education_level: Optional[str] = "College Student"
    current_class_or_year: Optional[str] = None
    stream: Optional[str] = None
    branch: Optional[str] = None
    department: Optional[str] = None
    university: Optional[str] = None
    cgpa_percentage: Optional[str] = None


class StudentLoginRequest(BaseModel):
    user_id: str = Field(..., description="User ID or Email")
    password: str


class ParentLoginRequest(BaseModel):
    parent_id: str = Field(..., description="Unique Parent ID (e.g. ACGS-PAR-XXXXX)")
    parent_pin: str = Field(..., min_length=4, max_length=10, description="Secure Parent PIN")


class StudentRegisterResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    id: Optional[int] = None
    student_id: str
    parent_id: str
    parent_pin: str
    user_id: str
    name: str
    full_name: Optional[str] = None
    email: str
    education_level: Optional[str] = None


class StudentProfileOut(BaseModel):
    id: int
    user_id: str
    student_id: str
    name: str
    email: str
    phone: Optional[str] = None
    parent_whatsapp: Optional[str] = None
    education_level: Optional[str] = None
    current_class_or_year: Optional[str] = None
    stream: Optional[str] = None
    branch: Optional[str] = None
    department: Optional[str] = None
    university: Optional[str] = None
    cgpa_percentage: Optional[str] = None
    parent_id: Optional[str] = None


class StudentProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    parent_whatsapp: Optional[str] = None
    education_level: Optional[str] = None
    current_class_or_year: Optional[str] = None
    stream: Optional[str] = None
    branch: Optional[str] = None
    department: Optional[str] = None
    university: Optional[str] = None
    cgpa_percentage: Optional[str] = None


# ─── Assessment Chatbot Schemas ───

class AssessmentStartResponse(BaseModel):
    assessment_id: int
    student_id: str
    status: str
    current_question: Optional[Dict[str, Any]] = None
    total_questions: int
    message: str


class AssessmentMessageRequest(BaseModel):
    assessment_id: Optional[int] = None
    student_id: Optional[str] = None
    answer: str
    question_id: Optional[str] = None
    question_text: Optional[str] = None


class AssessmentMessageResponse(BaseModel):
    assessment_id: int
    status: str
    is_completed: bool
    conversational_prefix: Optional[str] = ""
    next_question: Optional[Dict[str, Any]] = None
    current_step: int
    total_steps: int
    profile: Optional[Dict[str, Any]] = None


class AssessmentStatusResponse(BaseModel):
    assessment_id: Optional[int] = None
    student_id: str
    status: str # not_started, in_progress, completed
    current_step: int
    total_steps: int
    has_profile: bool
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class AssessmentHistoryResponse(BaseModel):
    student_id: str
    assessment_id: Optional[int] = None
    status: str
    total_responses: int
    responses: List[Dict[str, Any]]


# ─── Career Profile & Recommendations ───

class CareerProfileResponse(BaseModel):
    student_id: str
    personality_profile: Optional[Dict[str, Any]] = None
    interest_profile: Optional[Dict[str, Any]] = None
    skills_profile: Optional[Dict[str, Any]] = None
    values_profile: Optional[Dict[str, Any]] = None
    confidence_profile: Optional[Dict[str, Any]] = None
    career_recommendations: Optional[List[Dict[str, Any]]] = None
    disclaimer: str = "This is an initial career guidance profile, not a medical or psychological diagnosis."


# ─── Parent Dashboard Summary ───

class ParentStudentSummaryResponse(BaseModel):
    is_read_only: bool = True
    notice: str = "READ ONLY ACCESS. Recommendations are student-first and cannot be modified by parents."
    student_name: str
    student_id: str
    parent_id: str
    education_level: Optional[str] = None
    current_class_or_year: Optional[str] = None
    stream_or_branch: Optional[str] = None
    university: Optional[str] = None
    assessment_status: str
    assessment_progress: Dict[str, Any]
    personality_profile: Optional[Dict[str, Any]] = None
    skills_profile: Optional[Dict[str, Any]] = None
    interest_profile: Optional[Dict[str, Any]] = None
    career_recommendations: Optional[List[Dict[str, Any]]] = None
    selected_career: Optional[str] = None
