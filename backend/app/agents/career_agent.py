"""
Career Recommendation Agent
────────────────────────────────────────────────────────────────────────────
Responsibility:
Score each candidate career in the database against the student's multi-dimensional
profile using a transparent, configurable, multi-factor scoring algorithm.

Scoring Factors (Configurable, Normalized Weights):
- Interests Alignment: 25%
- Demonstrated & Transferable Skills: 20%
- Values and Motivations: 15%
- Work-Style / Personality Compatibility: 10%
- Education & Qualification Eligibility: 10%
- Goals & Career Expectations: 10%
- Practical Feasibility & Market Opportunity: 10%

Provides:
- Rank & Normalized Match Score (0–100%)
- Sub-scores (Personal fit vs Current readiness vs Market opportunity vs Feasibility)
- Personalized evidence-based matching reasons
- Transparent explanation (not an unexplained black-box number)
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Configurable documented weights (Sum = 1.0)
WEIGHTS = {
    "interests": 0.25,
    "skills": 0.20,
    "values": 0.15,
    "work_style": 0.10,
    "education": 0.10,
    "goals": 0.10,
    "feasibility": 0.10,
}

EDUCATION_RANK = {
    "10th": 1, "12th": 2, "diploma": 3,
    "b.tech": 4, "btech": 4, "b.e": 4, "be": 4, "bsc": 4, "bca": 4, "bba": 4, "bcom": 4,
    "mtech": 5, "m.tech": 5, "msc": 5, "ms": 5, "mca": 5, "mba": 5,
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
    Agent: Career Matching & Ranking Engine
    Hybrid matching engine combining structured multi-factor scoring with transparent evidence.
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
        values_score = self._score_values(profile, career)
        work_style_score = self._score_work_style(profile, career)
        edu_score = self._score_education(profile, career)
        goal_score = self._score_goal(profile, career)
        feasibility_score = self._score_feasibility(profile, career, skill_score, edu_score)

        # Weighted calculation
        total = (
            interest_score * WEIGHTS["interests"]
            + skill_score * WEIGHTS["skills"]
            + values_score * WEIGHTS["values"]
            + work_style_score * WEIGHTS["work_style"]
            + edu_score * WEIGHTS["education"]
            + goal_score * WEIGHTS["goals"]
            + feasibility_score * WEIGHTS["feasibility"]
        )
        total = round(min(100.0, max(0.0, total)), 1)

        reasons = self._generate_reasons(
            career.title, interest_score, skill_score, edu_score, goal_score, work_style_score, profile
        )

        return {
            "career_id": career.id,
            "career_title": career.title,
            "match_score": total,
            "interest_match": interest_score,
            "skill_match": skill_score,
            "education_match": edu_score,
            "goal_match": goal_score,
            "work_pref_match": work_style_score,
            "values_match": values_score,
            "feasibility_match": feasibility_score,
            "reasons": reasons,
            "personal_fit_score": round((interest_score * 0.5 + values_score * 0.3 + work_style_score * 0.2), 1),
            "current_readiness_score": round((skill_score * 0.6 + edu_score * 0.4), 1),
            "market_opportunity_score": round(feasibility_score, 1),
        }

    def _score_interest(self, profile: Dict[str, Any], career: Any) -> float:
        interest_scores: Dict[str, float] = profile.get("interest_scores", {})
        tags: List[str] = [t.lower() for t in (career.interest_tags or [])]
        if not tags or not interest_scores:
            return 50.0

        scores = []
        for tag in tags:
            tag_scores = [v for k, v in interest_scores.items() if tag in str(k).lower() or str(k).lower() in tag]
            if tag_scores:
                scores.append(max(tag_scores))
            else:
                scores.append(35.0)

        return round(sum(scores) / len(scores), 1) if scores else 50.0

    def _score_skill(self, profile: Dict[str, Any], career: Any) -> float:
        student_skills = profile.get("skill_scores", {})
        required = [s.lower() for s in (career.required_skills or [])]
        if not required:
            return 60.0

        student_known = [str(k).lower() for k, v in student_skills.items() if float(v) >= 40.0]
        matched = sum(1 for s in required if any(sk in s or s in sk for sk in student_known))
        return round((matched / len(required)) * 100, 1)

    def _score_values(self, profile: Dict[str, Any], career: Any) -> float:
        # Check values and impact orientation
        traits = profile.get("personality_traits", {}) or profile.get("personality_scores", {})
        learning = float(traits.get("learning_orientation", 60.0))
        social = float(traits.get("social", 50.0))
        detail = float(traits.get("detail_oriented", 50.0))
        
        t = career.title.lower()
        if "research" in t or "scientist" in t:
            return round((learning * 0.7 + detail * 0.3), 1)
        elif "product" in t or "business" in t:
            return round((social * 0.6 + learning * 0.4), 1)
        else:
            return round((learning * 0.5 + detail * 0.5), 1)

    def _score_work_style(self, profile: Dict[str, Any], career: Any) -> float:
        personality = profile.get("personality_scores", {}) or profile.get("personality_traits", {})
        score = 0.0
        total = 0.0
        for pref, good_careers in WORK_PREF_TAG_MAP.items():
            p_score = personality.get(pref, 0)
            if p_score > 0:
                match = 1.0 if career.title in good_careers else 0.4
                score += p_score * match
                total += p_score
        return round((score / total) if total else 55.0, 1)

    def _score_education(self, profile: Dict[str, Any], career: Any) -> float:
        edu_raw: str = (profile.get("education_level") or "b.tech").lower().replace(" ", "")
        student_rank = max(
            (v for k, v in EDUCATION_RANK.items() if k in edu_raw), default=4
        )
        min_required = CAREER_EDUCATION_MIN.get(career.title, 4)
        if student_rank >= min_required:
            return 100.0
        diff = min_required - student_rank
        return max(20.0, 100.0 - diff * 25)

    def _score_goal(self, profile: Dict[str, Any], career: Any) -> float:
        goal_scores: Dict[str, float] = profile.get("goal_scores", {})
        score = 0.0
        total_weight = 0.0
        for goal, high_careers in GOAL_TAG_MAP.items():
            g_score = goal_scores.get(goal, 0)
            if g_score > 0:
                match = 1.0 if career.title in high_careers else 0.35
                score += g_score * match
                total_weight += g_score
        return round((score / total_weight) if total_weight else 55.0, 1)

    def _score_feasibility(self, profile: Dict[str, Any], career: Any, skill_score: float, edu_score: float) -> float:
        # Feasibility merges skill readiness with labor market viability
        market_demand = 85.0 if career.career_growth in ("High", "Very High") else 70.0
        return round((skill_score * 0.4 + edu_score * 0.3 + market_demand * 0.3), 1)

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
        if interest >= 65:
            reasons.append(f"Strong interest alignment with core domains of {title} ({interest:.0f}%)")
        if skill >= 50:
            reasons.append(f"Demonstrated proficiency in {skill:.0f}% of foundational competencies")
        if edu >= 90:
            reasons.append("Your educational background satisfies entry requirements")
        if goal >= 65:
            reasons.append("Aligns with stated career growth and compensation aspirations")
        if work >= 60:
            reasons.append("Matches your preferred problem solving and collaboration work style")
        if not reasons:
            reasons.append(f"Solid foundational aptitude with positive growth potential in {title}")
        return reasons


career_recommendation_agent = CareerRecommendationAgent()
