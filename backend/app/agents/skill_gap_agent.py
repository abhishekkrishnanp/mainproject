"""
Skill Gap Analysis Agent
────────────────────────────────────────────────────────────────────────────
Responsibility:
Compare user's current profile against candidate career requirements using
a structured skills taxonomy and verified job requirements.

Classifies skill gaps into:
1. Critical prerequisites (Essential for entry-level eligibility)
2. High-priority skills (Frequently tested in screening and technical interviews)
3. Supporting skills (Enhance capability and productivity)
4. Optional specializations (Distinguish top performers)

Provides concrete learning pathways, estimated learning effort, and educational prerequisites.
Never infers mastery solely from expressed interest.
Distinguishes between a genuine skill gap and lack of evidence.
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
    Agent 3: Skill Gap Analyst Agent
    Rigorous taxonomy-based gap mapping between student abilities and job requirements.
    """

    agent_name: str = "SkillGapAgent"
    description: str = "Detailed taxonomy analysis classifying skill gaps into critical, high-priority, and supporting."
    AGENT_ID = "skill_gap_agent"

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinator process interface."""
        student_skills = data.get("student_skills", {})
        career = data.get("career")
        return self.analyze(student_skills, career)

    def generate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.process(data)

    def analyze(self, student_skill_scores: Any, career: Optional[Any] = None) -> Dict[str, Any]:
        """
        Analyze skill gaps with multi-level classification and learning effort estimates.
        """
        if isinstance(student_skill_scores, dict) and career is None and "student_skills" in student_skill_scores:
            career = student_skill_scores.get("career")
            student_skill_scores = student_skill_scores.get("student_skills", {})

        if career is None:
            return {
                "strong_skills": [],
                "skills_to_improve": [],
                "missing_skills": [],
                "critical_prerequisites": [],
                "high_priority_skills": [],
                "supporting_skills": [],
                "optional_specializations": [],
                "overall_readiness": 0.0,
                "gap_summary": "No career target specified.",
            }

        required: List[str] = list(career.required_skills or [])
        optional: List[str] = list(career.optional_skills or [])

        # Taxonomy classification
        strong = []
        improve = []
        missing = []

        critical_prereqs = []
        high_priority = []
        supporting = []
        optional_specs = []

        # Analyze required skills
        for idx, skill in enumerate(required):
            status, score, has_evidence = self._evaluate_skill_evidence(skill, student_skill_scores)
            learning_effort = self._estimate_learning_effort(skill, status)
            practical_action = self._suggest_practical_learning(skill)

            skill_entry = {
                "skill": skill,
                "status": status,
                "proficiency_score": score,
                "has_demonstrated_evidence": has_evidence,
                "learning_effort": learning_effort,
                "practical_action": practical_action,
            }

            if status == "Strong":
                strong.append(skill_entry)
            elif status in ("Intermediate", "Needs Improvement"):
                improve.append(skill_entry)
            else:
                missing.append(skill_entry)

            # Classify gap hierarchy
            if idx < 2:  # Foundational skills (e.g. programming/math/core)
                if status != "Strong":
                    critical_prereqs.append(skill_entry)
            else:
                if status != "Strong":
                    high_priority.append(skill_entry)

        # Analyze optional skills
        for skill in optional:
            status, score, has_evidence = self._evaluate_skill_evidence(skill, student_skill_scores)
            skill_entry = {
                "skill": skill,
                "status": status,
                "proficiency_score": score,
                "has_demonstrated_evidence": has_evidence,
                "learning_effort": self._estimate_learning_effort(skill, status),
                "practical_action": self._suggest_practical_learning(skill),
            }
            if status == "Strong":
                supporting.append(skill_entry)
            else:
                optional_specs.append(skill_entry)

        all_classified = strong + improve + missing
        if all_classified:
            readiness = sum(READINESS_WEIGHTS[e["status"]] for e in all_classified) / len(all_classified) * 100
        else:
            readiness = 0.0

        gap_summary = (
            f"You demonstrate {len(strong)} verified skills out of {len(required)} core requirements. "
            f"{len(critical_prereqs)} critical prerequisites and {len(high_priority)} high-priority competencies need focused development."
        )

        return {
            "career_title": career.title,
            "overall_readiness": round(readiness, 1),
            "strong_skills": strong,
            "skills_to_improve": improve,
            "missing_skills": missing,
            "critical_prerequisites": critical_prereqs,
            "high_priority_skills": high_priority,
            "supporting_skills": supporting,
            "optional_specializations": optional_specs,
            "educational_prerequisites": career.required_degree or "Bachelor's degree in relevant discipline",
            "gap_summary": gap_summary,
        }

    def _evaluate_skill_evidence(self, skill: str, student_scores: Any) -> tuple[str, float, bool]:
        """
        Distinguishes between verified demonstrated skill, reported interest, or missing evidence.
        """
        if not isinstance(student_scores, dict):
            return "Missing", 0.0, False

        skill_lower = skill.lower()
        best_score = 0.0
        has_evidence = False

        for k, v in student_scores.items():
            k_lower = str(k).lower()
            if k_lower in skill_lower or skill_lower in k_lower:
                val = float(v) if isinstance(v, (int, float)) else 50.0
                if val > best_score:
                    best_score = val
                    has_evidence = (val >= 60.0)

        if best_score >= 70.0:
            return "Strong", best_score, True
        elif best_score >= 40.0:
            return "Intermediate", best_score, has_evidence
        elif best_score > 0.0:
            return "Needs Improvement", best_score, False
        else:
            return "Missing", 0.0, False

    def _estimate_learning_effort(self, skill: str, status: str) -> str:
        if status == "Strong":
            return "Maintenance (Build 1 capstone project)"
        elif status == "Intermediate":
            return "3–6 weeks of targeted practice (20–30 hours)"
        elif status == "Needs Improvement":
            return "6–10 weeks structured curriculum (40–60 hours)"
        else:
            return "8–14 weeks foundational study and hands-on labs (60–90 hours)"

    def _suggest_practical_learning(self, skill: str) -> str:
        s = skill.lower()
        if "python" in s:
            return "Build 3 CLI applications and complete 'Automate the Boring Stuff with Python'."
        elif "machine learning" in s:
            return "Implement linear regression, decision trees, and random forests from scratch with Scikit-learn."
        elif "sql" in s:
            return "Practice 50 LeetCode/HackerRank SQL queries and design an e-commerce schema."
        elif "statistics" in s or "math" in s:
            return "Complete Khan Academy Statistics & 3Blue1Brown Linear Algebra series."
        elif "deep learning" in s or "tensorflow" in s or "pytorch" in s:
            return "Train a CNN image classifier and fine-tune a Hugging Face Transformer on a custom dataset."
        elif "cloud" in s or "aws" in s or "docker" in s or "kubernetes" in s:
            return "Containerize a web app with Docker and deploy to AWS free tier with CI/CD pipeline."
        elif "ui" in s or "ux" in s or "figma" in s:
            return "Design an end-to-end mobile app prototype in Figma with interactive components."
        elif "product" in s or "agile" in s:
            return "Draft a Product Requirements Document (PRD) and conduct 5 user discovery interviews."
        else:
            return f"Follow hands-on project tutorials and document implementation on GitHub."


skill_gap_agent = SkillGapAgent()
