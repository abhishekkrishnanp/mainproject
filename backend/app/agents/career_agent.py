"""
Career Recommendation Agent
────────────────────────────────────────────────────────────────────────────
Responsibility: Score each career in the database against the student's
profile using a transparent, weighted multi-factor algorithm.

Scoring Factors (weights sum to 100):
  - Interest Match    : 30%
  - Skill Match       : 25%
  - Education Match   : 15%
  - Goal Match        : 15%
  - Work Pref Match   : 15%
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# ─── Weight Configuration ─────────────────────────────────────────────────────
WEIGHTS = {
    "interest": 0.30,
    "skill": 0.25,
    "education": 0.15,
    "goal": 0.15,
    "work_pref": 0.15,
}

EDUCATION_RANK = {
    "10th": 1, "12th": 2, "diploma": 3,
    "b.tech": 4, "btech": 4, "b.e": 4, "be": 4, "bsc": 4,
    "mtech": 5, "m.tech": 5, "msc": 5, "ms": 5,
    "phd": 6, "ph.d": 6,
}

CAREER_EDUCATION_MIN = {
    "Research Scientist": 5,
    "Data Scientist": 4,
    "AI Engineer": 4,
    "Machine Learning Engineer": 4,
    "Software Engineer": 4,
    "Cybersecurity Analyst": 4,
    "Cloud Engineer": 4,
    "DevOps Engineer": 4,
    "UI/UX Designer": 3,
    "Product Manager": 4,
    "Business Analyst": 4,
    "Data Analyst": 4,
    "Data Engineer": 4,
}

GOAL_TAG_MAP = {
    "high_salary": ["AI Engineer", "Machine Learning Engineer", "Data Scientist", "Cloud Engineer", "Software Engineer", "Data Engineer"],
    "research": ["Research Scientist", "Data Scientist", "AI Engineer"],
    "entrepreneurship": ["Product Manager", "Business Analyst", "Software Engineer"],
    "job_stability": ["Software Engineer", "Cybersecurity Analyst", "DevOps Engineer", "Cloud Engineer", "Data Engineer"],
    "work_life_balance": ["UI/UX Designer", "Business Analyst", "Data Analyst", "Product Manager"],
    "international_career": ["AI Engineer", "Machine Learning Engineer", "Cloud Engineer", "Software Engineer"],
}

WORK_PREF_TAG_MAP = {
    "individual_work": ["Research Scientist", "Data Scientist", "Data Analyst"],
    "team_work": ["Software Engineer", "Product Manager", "DevOps Engineer", "UI/UX Designer"],
    "remote_work": ["Software Engineer", "UI/UX Designer", "Data Analyst", "Cloud Engineer"],
    "office_work": ["Business Analyst", "Product Manager", "Cybersecurity Analyst"],
    "research_oriented": ["Research Scientist", "Data Scientist", "AI Engineer", "Machine Learning Engineer"],
    "practical_work": ["Software Engineer", "DevOps Engineer", "Cybersecurity Analyst"],
    "creative_work": ["UI/UX Designer", "Product Manager"],
}


class CareerRecommendationAgent:
    """
    Agent ID: career_agent
    Input:  profile dict (from ProfileAnalysisAgent) + list of Career ORM objects
    Output: list of recommendation dicts sorted by match_score DESC
    """

    AGENT_ID = "career_agent"

    def recommend(self, profile: Dict[str, Any], careers: List[Any]) -> List[Dict[str, Any]]:
        results = []
        for career in careers:
            try:
                rec = self._score_career(profile, career)
                results.append(rec)
            except Exception as e:
                logger.error(f"[CareerAgent] Error scoring {career.title}: {e}")

        results.sort(key=lambda x: x["match_score"], reverse=True)
        for i, r in enumerate(results):
            r["rank"] = i + 1
        return results

    def _score_career(self, profile: Dict[str, Any], career: Any) -> Dict[str, Any]:
        interest_score = self._score_interest(profile, career)
        skill_score = self._score_skill(profile, career)
        edu_score = self._score_education(profile, career)
        goal_score = self._score_goal(profile, career)
        work_pref_score = self._score_work_pref(profile, career)

        overall = (
            interest_score * WEIGHTS["interest"]
            + skill_score * WEIGHTS["skill"]
            + edu_score * WEIGHTS["education"]
            + goal_score * WEIGHTS["goal"]
            + work_pref_score * WEIGHTS["work_pref"]
        )

        reasons = self._generate_reasons(
            career.title, interest_score, skill_score, edu_score, goal_score, work_pref_score, profile
        )

        return {
            "career_id": career.id,
            "career_title": career.title,
            "match_score": round(overall, 1),
            "interest_match": round(interest_score, 1),
            "skill_match": round(skill_score, 1),
            "education_match": round(edu_score, 1),
            "goal_match": round(goal_score, 1),
            "work_pref_match": round(work_pref_score, 1),
            "reasons": reasons,
            "rank": 0,  # filled after sorting
        }

    # ─── Scoring Sub-functions ────────────────────────────────────────────────

    def _score_interest(self, profile: Dict[str, Any], career: Any) -> float:
        interest_tags: List[str] = career.interest_tags or []
        interest_scores: Dict[str, float] = profile.get("interest_scores", {})
        if not interest_tags or not interest_scores:
            return 50.0
        total = sum(interest_scores.get(t, 0) for t in interest_tags)
        return min(100.0, (total / (len(interest_tags) * 100)) * 100 * 1.2)

    def _score_skill(self, profile: Dict[str, Any], career: Any) -> float:
        required: List[str] = [s.lower() for s in (career.required_skills or [])]
        student_skills_raw: str = profile.get("skill_scores", {})
        # student_skills is a dict of skill_name→score; convert to list of known skills
        student_known = [k.lower() for k, v in student_skills_raw.items() if v >= 50]
        if not required:
            return 60.0
        matched = sum(1 for s in required if any(sk in s or s in sk for sk in student_known))
        return round((matched / len(required)) * 100, 1)

    def _score_education(self, profile: Dict[str, Any], career: Any) -> float:
        edu_raw: str = (profile.get("education_level") or "b.tech").lower().replace(" ", "")
        student_rank = max(
            (v for k, v in EDUCATION_RANK.items() if k in edu_raw), default=4
        )
        min_required = CAREER_EDUCATION_MIN.get(career.title, 4)
        if student_rank >= min_required:
            return 100.0
        diff = min_required - student_rank
        return max(0.0, 100.0 - diff * 25)

    def _score_goal(self, profile: Dict[str, Any], career: Any) -> float:
        goal_scores: Dict[str, float] = profile.get("goal_scores", {})
        score = 0.0
        total_weight = 0.0
        for goal, high_careers in GOAL_TAG_MAP.items():
            g_score = goal_scores.get(goal, 0)
            if g_score > 0:
                match = 1.0 if career.title in high_careers else 0.3
                score += g_score * match
                total_weight += g_score
        return round((score / total_weight) if total_weight else 50.0, 1)

    def _score_work_pref(self, profile: Dict[str, Any], career: Any) -> float:
        personality: Dict[str, float] = profile.get("personality_scores", {})
        score = 0.0
        total = 0.0
        for pref, good_careers in WORK_PREF_TAG_MAP.items():
            p_score = personality.get(pref, 0)
            if p_score > 0:
                match = 1.0 if career.title in good_careers else 0.3
                score += p_score * match
                total += p_score
        return round((score / total) if total else 50.0, 1)

    # ─── Reason Generation ────────────────────────────────────────────────────

    def _generate_reasons(
        self,
        title: str,
        interest: float,
        skill: float,
        edu: float,
        goal: float,
        work: float,
        profile: Dict[str, Any],
    ) -> List[str]:
        reasons = []
        if interest >= 70:
            reasons.append(f"Your interests strongly align with {title} (Interest Match: {interest:.0f}%)")
        if skill >= 60:
            reasons.append(f"You already possess {skill:.0f}% of the required skills")
        if edu >= 100:
            reasons.append("Your education meets the minimum qualification requirements")
        if goal >= 70:
            reasons.append("This career aligns with your stated goals (salary / growth / stability)")
        if work >= 70:
            reasons.append("Your preferred work style matches typical work environments in this field")
        if not reasons:
            reasons.append(f"Overall compatibility score: {((interest+skill+edu+goal+work)/5):.0f}%")
        return reasons
