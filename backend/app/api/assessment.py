from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.assessment import AssessmentResult
from app.schemas.assessment import AssessmentCreate, AssessmentOut
from app.services.assessment_service import process_assessment
from app.core.deps import get_current_active_user

router = APIRouter()


@router.post("", response_model=AssessmentOut, status_code=status.HTTP_201_CREATED)
def submit_assessment(
    assessment_in: AssessmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit assessment answers. Processes scores and builds user profile."""
    if not assessment_in.answers:
        raise HTTPException(status_code=400, detail="Assessment answers cannot be empty.")

    answers_dicts = [a.model_dump() for a in assessment_in.answers]
    result = process_assessment(db, current_user.id, answers_dicts)
    return result


@router.get("", response_model=AssessmentOut)
def get_assessment(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get the current user's latest assessment result."""
    result = db.query(AssessmentResult).filter_by(user_id=current_user.id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found. Please complete the assessment first."
        )
    return result
