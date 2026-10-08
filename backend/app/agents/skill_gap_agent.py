"""
Skill Gap Analysis Agent
────────────────────────────────────────────────────────────────────────────
Responsibility: Compare a student's current skills (from assessment) against
the required skills for their selected career. Classify each required skill
and compute an overall readiness percentage.

Skill Status Levels:
  Strong           – Student has the skill at ≥70% proficiency
  Intermediate     – Student has the skill at 40-69% proficiency
  Needs Improvement – Student has the skill but at <40%
  Missing          – Student has no knowledge of this skill
"""
from __future__ import annotations
import logging
from typing import Dict, Any, List, Optional
from app.agents.base import CareerAgent

logger = logging.getLogger(__name__)

READINESS_WEIGHTS = {
    "Strong": 1.0,
    "Intermediate": 0.6,
    "Needs Improvement": 0.25,
    "Missing": 0.0,
}


class SkillGapAgent(CareerAgent):
    """
    Agent ID: skill_gap_agent
    Phase 3 Target: Complete career requirements vs student skills gap report.
    """

    agent_name: str = "SkillGapAgent"
    description: str = "Identifies skill disparities and readiness ratings against career targets."
    AGENT_ID = "skill_gap_agent"

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process skill mapping."""
        return {
            "status": "ready_for_phase_3",
            "message": "Skill Gap Agent structured for Phase 3 deep curriculum mapping.",
            "data": data,
        }

    def generate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final skill gap report."""
        return {
            "agent": self.agent_name,
            "status": "skeleton_ready",
            "result": data,
        }

    def analyze(self, student_skill_scores: Any, career: Optional[Any] = None) -> Dict[str, Any]:
        if isinstance(student_skill_scores, dict) and career is None and "student_skills" in student_skill_scores:
            career = student_skill_scores.get("career")
            student_skill_scores = student_skill_scores.get("student_skills", {})
        if career is None:
            return {"strong_skills": [], "skills_to_improve": [], "missing_skills": [], "overall_readiness": 0.0}

        required: List[str] = career.required_skills or []
        optional: List[str] = career.optional_skills or []

        strong, improve, missing = [], [], []

        for skill in required:
            status = self._classify_skill(skill, student_skill_scores)
            entry = {"skill": skill, "status": status}
            if status == "Strong":
                strong.append(entry)
            elif status in ("Intermediate", "Needs Improvement"):
                improve.append(entry)
            else:
                missing.append(entry)

        all_classified = strong + improve + missing
        if all_classified:
            readiness = sum(
                READINESS_WEIGHTS[e["status"]] for e in all_classified
            ) / len(all_classified) * 100
        else:
            readiness = 0.0

        return {
            "strong_skills": strong,
            "skills_to_improve": improve,
            "missing_skills": missing,
            "overall_readiness": round(readiness, 1),
        }

    def _classify_skill(self, skill: str, student_scores: Dict[str, float]) -> str:
        skill_lower = skill.lower()
        best_score = 0.0
        for k, v in student_scores.items():
            if k.lower() in skill_lower or skill_lower in k.lower():
                best_score = max(best_score, v)

        if best_score >= 70:
            return "Strong"
        elif best_score >= 40:
            return "Intermediate"
        elif best_score > 0:
            return "Needs Improvement"
        else:
            return "Missing"
