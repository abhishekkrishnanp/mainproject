"""
Profile Analysis Agent
────────────────────────────────────────────────────────────────────────────
Responsibility: Analyze a student's assessment results (interests, skills,
personality, goals) and produce a structured profile dict.

Architecture Note:
  - Currently uses rule-based mock logic for demo purposes.
  - To integrate a real LLM (e.g., Gemini), replace _run_mock() with
    a call to the LLM API inside _run_llm(). Set USE_REAL_LLM=true in .env.
"""
from __future__ import annotations
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


# ─── Interest Area Mapping ────────────────────────────────────────────────────
INTEREST_AREA_MAP = {
    "technology": ["programming", "mathematics", "data_analysis", "research", "cybersecurity", "cloud"],
    "design_creative": ["design", "creativity", "ui_ux"],
    "business": ["business", "management", "entrepreneurship", "communication"],
    "healthcare": ["healthcare", "biology"],
    "research": ["research", "mathematics", "data_analysis"],
}

WORK_PREF_MAP = {
    "Research": ["research_oriented"],
    "Creative": ["creative_work"],
    "Team-based": ["team_work"],
    "Individual": ["individual_work"],
    "Remote": ["remote_work"],
    "Office": ["office_work"],
    "Practical": ["practical_work"],
}


class ProfileAnalysisAgent:
    """
    Agent ID: profile_agent
    Input:  assessment dict (interest_scores, skill_scores, personality_scores, goal_scores)
    Output: structured profile dict
    """

    AGENT_ID = "profile_agent"

    def analyze(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entry point. Calls mock or LLM backend depending on config.
        """
        try:
            return self._run_mock(assessment_data)
        except Exception as e:
            logger.error(f"[ProfileAgent] Error: {e}")
            return self._fallback_profile()

    # ─── Mock Implementation ──────────────────────────────────────────────────

    def _run_mock(self, data: Dict[str, Any]) -> Dict[str, Any]:
        interest_scores: Dict[str, float] = data.get("interest_scores", {})
        skill_scores: Dict[str, float] = data.get("skill_scores", {})
        personality_scores: Dict[str, float] = data.get("personality_scores", {})
        goal_scores: Dict[str, float] = data.get("goal_scores", {})

        # Determine primary interest area
        interest_area = self._determine_interest_area(interest_scores)

        # Classify skills
        strong_skills = [k for k, v in skill_scores.items() if v >= 70]
        weak_skills = [k for k, v in skill_scores.items() if v < 50]

        # Determine work preference
        work_preference = self._determine_work_pref(personality_scores)

        # Derive career preferences from interests + goals
        career_prefs = self._derive_career_prefs(interest_scores, goal_scores, interest_area)

        profile = {
            "interest_area": interest_area,
            "strong_skills": strong_skills,
            "weak_skills": weak_skills,
            "work_preference": work_preference,
            "career_preferences": career_prefs,
            "interest_scores": interest_scores,
            "skill_scores": skill_scores,
            "personality_scores": personality_scores,
            "goal_scores": goal_scores,
        }
        logger.info(f"[ProfileAgent] Profile built: area={interest_area}, prefs={career_prefs}")
        return profile

    def _determine_interest_area(self, interest_scores: Dict[str, float]) -> str:
        area_totals: Dict[str, float] = {}
        for area, keys in INTEREST_AREA_MAP.items():
            area_totals[area] = sum(interest_scores.get(k, 0) for k in keys)
        return max(area_totals, key=area_totals.get, default="technology").replace("_", " ").title()

    def _determine_work_pref(self, personality_scores: Dict[str, float]) -> str:
        for pref, keys in WORK_PREF_MAP.items():
            if any(personality_scores.get(k, 0) >= 70 for k in keys):
                return pref
        return "Team-based"

    def _derive_career_prefs(
        self,
        interest_scores: Dict[str, float],
        goal_scores: Dict[str, float],
        interest_area: str,
    ) -> List[str]:
        prefs = []
        area_lower = interest_area.lower()

        if "technology" in area_lower:
            if interest_scores.get("programming", 0) >= 70:
                prefs.append("Software Engineer")
            if interest_scores.get("data_analysis", 0) >= 60:
                prefs.extend(["Data Scientist", "Machine Learning Engineer"])
            if interest_scores.get("cybersecurity", 0) >= 60:
                prefs.append("Cybersecurity Analyst")
            if interest_scores.get("cloud", 0) >= 60:
                prefs.append("Cloud Engineer")
        if "design" in area_lower or "creative" in area_lower:
            prefs.append("UI/UX Designer")
        if "business" in area_lower:
            prefs.extend(["Product Manager", "Business Analyst"])
        if "research" in area_lower or goal_scores.get("research", 0) >= 70:
            prefs.append("Research Scientist")
        if goal_scores.get("high_salary", 0) >= 70:
            prefs.append("AI Engineer")

        return list(dict.fromkeys(prefs)) or ["Software Engineer"]  # deduplicate, ensure non-empty

    def _fallback_profile(self) -> Dict[str, Any]:
        return {
            "interest_area": "Technology",
            "strong_skills": [],
            "weak_skills": [],
            "work_preference": "Team-based",
            "career_preferences": ["Software Engineer"],
        }
