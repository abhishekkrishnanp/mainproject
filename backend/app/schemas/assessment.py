from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class AssessmentAnswerIn(BaseModel):
    question_key: Optional[str] = None
    question_id: Optional[str] = None
    answer_value: Optional[Any] = None
    answer: Optional[Any] = None
    category: Optional[str] = "interest"
    question_text: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.question_key:
            self.question_key = self.question_id or "q"
        if not self.question_id:
            self.question_id = self.question_key
        if self.answer_value is None:
            self.answer_value = self.answer if self.answer is not None else 3
        if self.answer is None:
            self.answer = self.answer_value


class AssessmentCreate(BaseModel):
    answers: List[AssessmentAnswerIn]


class AssessmentOut(BaseModel):
    id: int
    user_id: int
    interest_scores: Optional[Dict[str, Any]] = None
    skill_scores: Optional[Dict[str, Any]] = None
    personality_scores: Optional[Dict[str, Any]] = None
    goal_scores: Optional[Dict[str, Any]] = None
    interest_area: Optional[str] = None
    strong_skills: Optional[List[str]] = None
    weak_skills: Optional[List[str]] = None
    work_preference: Optional[str] = None
    career_preferences: Optional[List[str]] = None
    created_at: datetime

    model_config = {"from_attributes": True}
