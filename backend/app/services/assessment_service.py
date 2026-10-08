"""
Assessment Service
────────────────────────────────────────────────────────────────────────────
Processes raw assessment answers into category scores, then calls the
Profile Analysis Agent to build the structured student profile.
"""
from __future__ import annotations
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.assessment import AssessmentResult, AssessmentAnswer
from app.agents.coordinator import coordinator
import logging

logger = logging.getLogger(__name__)


def process_assessment(
    db: Session,
    user_id: int,
    answers: List[Dict[str, Any]],
) -> AssessmentResult:
    """
    1. Aggregate raw answers into category scores (0-100 per key).
    2. Call ProfileAnalysisAgent to derive the structured profile.
    3. Persist to DB and return the ORM object.
    """
    # ── Aggregate by category ─────────────────────────────────────────────────
    category_buckets: Dict[str, Dict[str, List[int]]] = {
        "interest": {}, "skill": {}, "personality": {}, "goal": {}
    }

    for ans in answers:
        cat = ans.get("category", "interest")
        key = ans.get("question_key") or ans.get("question_id") or "unknown"
        raw_val = ans.get("answer_value") if ans.get("answer_value") is not None else ans.get("answer", 3)
        try:
            val = int(float(raw_val))
        except (ValueError, TypeError):
            val = 3
        category_buckets.setdefault(cat, {}).setdefault(key, []).append(val)

    def to_scores(bucket: Dict[str, List[int]]) -> Dict[str, float]:
        """Convert Likert 1-5 to 0-100 percentage per key."""
        return {
            k: round(((sum(v) / len(v)) - 1) / 4 * 100, 1)
            for k, v in bucket.items()
        }

    interest_scores = to_scores(category_buckets.get("interest", {}))
    skill_scores = to_scores(category_buckets.get("skill", {}))
    personality_scores = to_scores(category_buckets.get("personality", {}))
    goal_scores = to_scores(category_buckets.get("goal", {}))

    # ── Run Profile Agent ─────────────────────────────────────────────────────
    profile = coordinator.run_profile_analysis({
        "interest_scores": interest_scores,
        "skill_scores": skill_scores,
        "personality_scores": personality_scores,
        "goal_scores": goal_scores,
    })

    # ── Upsert Assessment Result ──────────────────────────────────────────────
    existing = db.query(AssessmentResult).filter_by(user_id=user_id).first()
    if existing:
        result = existing
        # Clear old answers
        db.query(AssessmentAnswer).filter_by(assessment_id=existing.id).delete()
    else:
        result = AssessmentResult(user_id=user_id)
        db.add(result)
        db.flush()

    result.interest_scores = interest_scores
    result.skill_scores = skill_scores
    result.personality_scores = personality_scores
    result.goal_scores = goal_scores
    result.interest_area = profile.get("interest_area")
    result.strong_skills = profile.get("strong_skills")
    result.weak_skills = profile.get("weak_skills")
    result.work_preference = profile.get("work_preference")
    result.career_preferences = profile.get("career_preferences")

    # ── Store individual answers ───────────────────────────────────────────────
    for ans in answers:
        answer_obj = AssessmentAnswer(
            assessment_id=result.id,
            question_key=ans.get("question_key"),
            answer_value=int(ans.get("answer_value", 3)),
            category=ans.get("category", "interest"),
        )
        db.add(answer_obj)

    db.commit()
    db.refresh(result)
    logger.info(f"[AssessmentService] Processed assessment for user {user_id}")
    return result
