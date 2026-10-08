"""
Career Feasibility Agent
────────────────────────────────────────────────────────────────────────────
Responsibility: Evaluate whether a selected career is achievable for this
student given their current education, skills, and skill gaps. Provide
actionable reasoning — not a binary yes/no.
"""
from __future__ import annotations
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

EDUCATION_RANK = {
    "10th": 1, "12th": 2, "diploma": 3,
    "b.tech": 4, "btech": 4, "b.e": 4, "be": 4, "bsc": 4,
    "mtech": 5, "m.tech": 5, "msc": 5, "ms": 5,
    "phd": 6, "ph.d": 6,
}

HIGH_EDU_CAREERS = {"Research Scientist", "AI Engineer", "Machine Learning Engineer", "Data Scientist"}
TIMELINE_ESTIMATES = {
    (90, 100): "You are nearly job-ready! 2-4 months of focused preparation.",
    (70, 89): "You can be job-ready in 6-9 months with consistent effort.",
    (50, 69): "Plan for 9-15 months of structured learning and project building.",
    (30, 49): "This is a stretch goal — budget 15-24 months for comprehensive upskilling.",
    (0, 29): "This career requires significant foundational work. Budget 24-36 months.",
}


from app.agents.base import CareerAgent


class FeasibilityAgent(CareerAgent):
    """
    Agent ID: feasibility_agent
    Phase 5 Target: Realistic evaluation of competition, difficulty, time investment, and readiness.
    """

    agent_name: str = "FeasibilityAgent"
    description: str = "Evaluates practical achievement probability, competition levels, and transition difficulty."
    AGENT_ID = "feasibility_agent"

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze feasibility inputs."""
        return {"status": "ready_for_phase_5", "data": data}

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process feasibility evaluation."""
        return {"status": "skeleton_ready", "message": "Feasibility Agent ready for Phase 5 expansion."}

    def generate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final feasibility report."""
        return {"agent": self.agent_name, "status": "skeleton_ready", "result": data}

    def evaluate(
        self,
        profile: Dict[str, Any],
        career: Any,
        skill_gap: Dict[str, Any],
    ) -> Dict[str, Any]:
        readiness = skill_gap.get("overall_readiness", 50.0)
        strong = skill_gap.get("strong_skills", [])
        missing = skill_gap.get("missing_skills", [])
        improve = skill_gap.get("skills_to_improve", [])

        strengths = self._compute_strengths(profile, career, strong, readiness)
        challenges = self._compute_challenges(profile, career, missing, improve)
        action_items = self._compute_action_items(career, missing, improve, profile)
        timeline = self._estimate_timeline(readiness)
        overall = self._overall_level(readiness)

        summary = (
            f"Based on your current profile, this career is {overall.lower()}ly feasible. "
            f"You have {len(strong)} strong skill(s) and need to develop {len(missing)} more. "
            f"{timeline}"
        )

        return {
            "career_title": career.title,
            "overall_feasibility": overall,
            "readiness_score": readiness,
            "strengths": strengths,
            "challenges": challenges,
            "action_items": action_items,
            "timeline_estimate": timeline,
            "summary": summary,
        }

    def _compute_strengths(self, profile, career, strong_skills, readiness) -> List[str]:
        strengths = []
        if strong_skills:
            names = [s["skill"] for s in strong_skills[:3]]
            strengths.append(f"You already have strong proficiency in: {', '.join(names)}")
        edu = (profile.get("education_level") or "").lower()
        if career.title not in HIGH_EDU_CAREERS or any(k in edu for k in ["b.tech", "btech", "bsc"]):
            strengths.append("Your education meets or is on track to meet the basic qualifications")
        if readiness >= 60:
            strengths.append(f"Your overall skill readiness ({readiness:.0f}%) is above average")
        interest_area = profile.get("interest_area", "")
        if career.title in (profile.get("career_preferences") or []):
            strengths.append(f"This career aligns with your stated interest in {interest_area}")
        return strengths or ["You have a clear motivation to pursue this career path"]

    def _compute_challenges(self, profile, career, missing, improve) -> List[str]:
        challenges = []
        if missing:
            missing_names = [s["skill"] for s in missing[:4]]
            challenges.append(f"You currently lack: {', '.join(missing_names)}")
        if improve:
            improve_names = [s["skill"] for s in improve[:3]]
            challenges.append(f"Skills needing improvement: {', '.join(improve_names)}")
        edu = (profile.get("education_level") or "").lower()
        if career.title in HIGH_EDU_CAREERS and not any(k in edu for k in ["mtech", "phd", "msc"]):
            challenges.append("A postgraduate degree (M.Tech/M.S.) is preferred for senior roles in this field")
        return challenges or ["No major blockers identified — continue building your skill set"]

    def _compute_action_items(self, career, missing, improve, profile) -> List[str]:
        actions = []
        for s in missing[:3]:
            actions.append(f"Learn {s['skill']} — take an online course or refer to official documentation")
        for s in improve[:2]:
            actions.append(f"Strengthen {s['skill']} — practice with projects and exercises")
        actions.append("Complete 2-3 real-world projects to build a strong portfolio")
        actions.append("Explore internship/freelance opportunities to gain industry exposure")
        actions.append("Join relevant communities (GitHub, LinkedIn groups, Kaggle, etc.)")
        return actions

    def _estimate_timeline(self, readiness: float) -> str:
        for (low, high), msg in TIMELINE_ESTIMATES.items():
            if low <= readiness <= high:
                return msg
        return "Timeline depends on your pace of learning and consistency."

    def _overall_level(self, readiness: float) -> str:
        if readiness >= 80:
            return "High"
        elif readiness >= 50:
            return "Medium"
        else:
            return "Low"
