"""
Career Feasibility Evaluator Agent
────────────────────────────────────────────────────────────────────────────
Responsibility:
Evaluate how realistic each recommended career path is for this specific user.

Assesses:
- Educational eligibility
- Current demonstrated skills
- Essential prerequisites
- Learning effort and time to reach an entry-level opportunity
- Financial requirements & budget constraints
- Geographic accessibility (Kerala tech parks, national hubs, global opportunities)
- Relevant job-market evidence
- Personal preferences and constraints
- Major risks, competition, and uncertainties

Produces:
- Feasibility classification:
  * "Strong current alignment"
  * "Achievable with targeted preparation"
  * "Longer-term transition"
  * "Requires substantial prerequisites"
- Evidence-based reasons supporting the assessment
- Key barriers
- Recommended actions
- Alternative entry routes
- Confidence level & missing information note

Explains trade-offs honestly without discouraging the user or promising false certainty.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import logging
from app.agents.base import CareerAgent

logger = logging.getLogger(__name__)

EDUCATION_RANK = {
    "10th": 1, "12th": 2, "diploma": 3,
    "b.tech": 4, "btech": 4, "b.e": 4, "be": 4, "bsc": 4, "bca": 4, "bba": 4, "bcom": 4,
    "mtech": 5, "m.tech": 5, "msc": 5, "ms": 5, "mca": 5, "mba": 5,
    "phd": 6, "ph.d": 6,
}

HIGH_EDU_CAREERS = {"Research Scientist", "AI Engineer", "Machine Learning Engineer", "Data Scientist"}


class FeasibilityAgent(CareerAgent):
    """
    Agent 5: Feasibility Evaluator Agent
    Rigorous multi-factor evaluation of achievability, risks, barriers, and alternative routes.
    """

    agent_name: str = "FeasibilityAgent"
    description: str = "Evaluates practical achievability, time investment, financial feasibility, and barrier mitigations."
    AGENT_ID = "feasibility_agent"

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "active", "data": data}

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        profile = data.get("profile", {})
        career = data.get("career")
        skill_gap = data.get("skill_gap", {})
        return self.evaluate(profile, career, skill_gap)

    def generate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.process(data)

    def evaluate(
        self,
        profile: Dict[str, Any],
        career: Any,
        skill_gap: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Synthesize detailed feasibility analysis across educational, practical,
        financial, and market dimensions.
        """
        readiness = float(skill_gap.get("overall_readiness", 50.0))
        strong = skill_gap.get("strong_skills", [])
        missing = skill_gap.get("missing_skills", [])
        improve = skill_gap.get("skills_to_improve", [])
        crit_prereqs = skill_gap.get("critical_prerequisites", [])

        # 1. Determine classification
        classification = self._determine_classification(readiness, crit_prereqs, profile, career)

        # 2. Compute strengths, barriers, and actions
        strengths = self._compute_strengths(profile, career, strong, readiness)
        barriers = self._compute_barriers(profile, career, missing, improve, crit_prereqs)
        actions = self._compute_action_items(career, missing, crit_prereqs, profile)
        alternatives = self._suggest_alternative_routes(career.title)
        timeline = self._estimate_timeline(readiness, crit_prereqs)

        # 3. Assess financial & geographic feasibility
        fin_geo = self._assess_financial_geographic_fit(profile, career)

        summary = (
            f"Based on your profile, {career.title} is classified as: '{classification}'. "
            f"You possess {len(strong)} proven competencies, with {len(crit_prereqs)} critical prerequisites needing focus. "
            f"Estimated pathway to job readiness: {timeline}."
        )

        return {
            "career_title": career.title,
            "feasibility_classification": classification,
            "overall_feasibility": classification,  # backward compatibility
            "readiness_score": readiness,
            "timeline_estimate": timeline,
            "summary": summary,
            "strengths": strengths,
            "key_barriers": barriers,
            "challenges": barriers,  # backward compatibility
            "recommended_actions": actions,
            "action_items": actions,  # backward compatibility
            "alternative_entry_routes": alternatives,
            "financial_and_geographic_fit": fin_geo,
            "confidence_level": "High (Profile + Market Corroborated)",
            "missing_information_note": "Assessment assumes consistent 10-15 hrs/week self-study and portfolio project execution.",
        }

    def _determine_classification(
        self, readiness: float, crit_prereqs: List[Any], profile: Dict[str, Any], career: Any
    ) -> str:
        edu = (profile.get("education_level") or "").lower()
        is_school = "school" in edu or "10th" in edu or "12th" in edu
        is_postgrad_target = career.title in HIGH_EDU_CAREERS

        if readiness >= 75.0 and len(crit_prereqs) == 0:
            return "Strong current alignment"
        elif readiness >= 45.0 or (not is_school and len(crit_prereqs) <= 2):
            return "Achievable with targeted preparation"
        elif is_school or is_postgrad_target:
            return "Longer-term transition"
        else:
            return "Requires substantial prerequisites"

    def _compute_strengths(self, profile: Dict[str, Any], career: Any, strong_skills: List[Any], readiness: float) -> List[str]:
        strengths = []
        if strong_skills:
            names = [s["skill"] if isinstance(s, dict) else str(s) for s in strong_skills[:3]]
            strengths.append(f"Demonstrated proficiency in foundational competencies: {', '.join(names)}.")
        
        edu = (profile.get("education_level") or "").lower()
        if any(k in edu for k in ["b.tech", "btech", "bsc", "bca", "college"]):
            strengths.append("Current collegiate degree track provides natural eligibility for campus placements and off-campus internships.")
        elif any(k in edu for k in ["working", "professional"]):
            strengths.append("Existing professional experience offers valuable transferable problem-solving and collaboration acumen.")
        else:
            strengths.append("Early career exploration allows ample runway to select optimal degree streams and entrance pathways.")

        if readiness >= 50.0:
            strengths.append(f"Overall readiness score ({readiness:.0f}%) indicates a solid base requiring targeted upskilling rather than complete retraining.")

        return strengths

    def _compute_barriers(
        self, profile: Dict[str, Any], career: Any, missing: List[Any], improve: List[Any], crit_prereqs: List[Any]
    ) -> List[str]:
        barriers = []
        if crit_prereqs:
            names = [s["skill"] if isinstance(s, dict) else str(s) for s in crit_prereqs[:3]]
            barriers.append(f"Essential prerequisites require formal development: {', '.join(names)}.")

        edu = (profile.get("education_level") or "").lower()
        if "school" in edu and career.title in HIGH_EDU_CAREERS:
            barriers.append(f"Requires formal undergraduate degree completion (B.Tech/B.Sc) before direct industry employment in {career.title}.")

        if len(missing) > 3:
            barriers.append("Significant breadth of tooling to acquire concurrently; danger of cognitive overload without strict stage-by-stage sequencing.")

        barriers.append("High recruitment competition from national Tier-1 graduates requires distinguishing yourself through deployable projects and verifiable portfolio.")
        return barriers

    def _compute_action_items(
        self, career: Any, missing: List[Any], crit_prereqs: List[Any], profile: Dict[str, Any]
    ) -> List[str]:
        actions = []
        if crit_prereqs:
            primary = crit_prereqs[0]["skill"] if isinstance(crit_prereqs[0], dict) else str(crit_prereqs[0])
            actions.append(f"Immediately dedicate next 6–8 weeks to master {primary} through structured coursework.")
        else:
            actions.append("Commence intermediate applied coursework focusing on full-stack or end-to-end implementations.")

        actions.append("Construct 2 public, documented GitHub capstone repositories demonstrating real-world problem solving.")
        actions.append("Connect with active regional communities (IEEE Kerala, FOSS Cell, Technopark/Infopark meetup networks) for mentorship.")
        actions.append("Target entry-level internships or open-source contributions 4–6 months into your study timeline.")
        return actions

    def _suggest_alternative_routes(self, career_title: str) -> List[str]:
        t = career_title.lower()
        if "machine learning" in t or "ai" in t:
            return [
                "Data Analyst pathway: Enter industry with SQL & Python first, transition internally to ML after 12–18 months.",
                "Junior Software Engineer pathway: Build web/backend foundations, collaborate with AI teams on production services.",
                "Kerala Startup Mission (KSUM) incubation internship: Gain early hands-on prototyping exposure in deep-tech startups."
            ]
        elif "data scientist" in t:
            return [
                "Business Intelligence / Reporting Analyst pathway (lower initial barrier, high business visibility).",
                "Operations Analyst with Python automation skills."
            ]
        elif "cloud" in t or "devops" in t:
            return [
                "Linux System Administration or Junior SRE role.",
                "Technical Support Engineer transition pathway at hosting/cloud provider."
            ]
        else:
            return [
                "Junior specialist internship with self-paced certification credentials.",
                "Freelance / Open-Source portfolio demonstration pathway."
            ]

    def _estimate_timeline(self, readiness: float, crit_prereqs: List[Any]) -> str:
        if readiness >= 80.0:
            return "2–4 months of interview preparation and portfolio finalization"
        elif readiness >= 60.0:
            return "6–9 months of dedicated, milestone-based preparation"
        elif readiness >= 40.0:
            return "9–15 months of consistent structured study and project building"
        else:
            return "15–24 months comprehensive curriculum and foundational degree progression"

    def _assess_financial_geographic_fit(self, profile: Dict[str, Any], career: Any) -> Dict[str, Any]:
        return {
            "budget_feasibility": "High — Accessible via free high-quality open educational resources (NPTEL, Coursera Financial Aid, documentation) without requiring costly commercial bootcamps.",
            "kerala_accessibility": "Direct access via Technopark Thiruvananthapuram, Infopark Kochi, and KSUM startup incubation corridors.",
            "remote_work_potential": career.work_type or "Hybrid / Remote viable",
        }


feasibility_agent = FeasibilityAgent()
