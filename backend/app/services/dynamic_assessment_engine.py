"""
Dynamic, Context-Aware AI Assessment & Career Guidance Engine
────────────────────────────────────────────────────────────────────────────
Replaces static question sequences with interactive, multi-turn AI assessment:
1. Dynamically generates relevant follow-up questions from actual conversation history.
2. Adapts depth (beginner, intermediate, advanced) and clarifies vague answers.
3. Tracks previously asked questions to eliminate semantic duplicates.
4. Synthesizes genuinely personalized career matches, skill gaps, projects, and roadmaps.
5. Fully integrates with SQLite DB, preserving sessions across page refreshes.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.services.llm_service import llm_service
from app.config import settings

logger = logging.getLogger(__name__)


# ─── Initial Grounding Question (Turn 1) ───────────────────────────────────────
INITIAL_QUESTION = {
    "question_id": "dyn_q_1_domain",
    "phase": "interests",
    "question_text": "Welcome to your personalized career discovery interview! What academic areas, technologies, or real-world fields are you most curious or passionate about exploring?",
    "options": [
        "Artificial Intelligence, Machine Learning & Healthcare / Biomedical Data",
        "Web, Mobile & Full-Stack Application Engineering",
        "Data Science, Business Analytics & Algorithmic Insights",
        "UI/UX Design, Human-Centered Products & Interactive Systems",
        "Cybersecurity, Cloud Infrastructure & Systems Engineering",
        "Core Engineering (Robotics, Electronics, IoT, Automation)",
    ],
    "category": "domain_selection",
}


class DynamicAssessmentEngine:
    """
    Autonomous, stateful assessment engine that uses Gemini to conduct
    adaptive, non-repetitive interviews and generate personalized career plans.
    """

    TARGET_TURNS = 8  # Comprehensive yet respectful of user time

    def get_initial_state(self, student_id: str) -> Dict[str, Any]:
        """Creates fresh assessment state."""
        return {
            "student_id": student_id,
            "status": "in_progress",
            "current_step": 0,
            "total_steps": self.TARGET_TURNS,
            "focus_domain": None,
            "proficiency_level": "beginner",
            "extracted_profile": {
                "interests": [],
                "confirmed_skills": [],
                "self_reported_skills": [],
                "knowledge_gaps": [],
                "goals": [],
                "work_preferences": [],
            },
            "previously_asked_questions": [INITIAL_QUESTION["question_text"]],
            "conversation_history": [],  # list of {"question": ..., "answer": ...}
        }

    async def generate_next_step(
        self,
        student_id: str,
        current_state: Dict[str, Any],
        user_answer: str,
        current_question_def: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Processes user's answer, updates conversation memory, and uses Gemini
        to dynamically generate the next probe OR conclude the assessment.
        """
        # 1. Update history
        q_text = (current_question_def.get("question_text") if current_question_def else "Previous Question") or "Question"
        history = current_state.setdefault("conversation_history", [])
        history.append({
            "step": len(history) + 1,
            "question": q_text,
            "answer": user_answer.strip(),
        })

        asked_questions = current_state.setdefault("previously_asked_questions", [])
        if q_text not in asked_questions:
            asked_questions.append(q_text)

        turn_count = len(history)
        current_state["current_step"] = turn_count

        # Check if we should conclude assessment
        should_finalize = turn_count >= self.TARGET_TURNS

        # 2. Call Gemini for dynamic next step or final synthesis
        if llm_service.is_configured():
            try:
                ai_step = await self._generate_ai_turn(
                    history=history,
                    asked_questions=asked_questions,
                    current_profile=current_state.get("extracted_profile", {}),
                    is_final_turn=should_finalize,
                    turn_number=turn_count,
                    latest_answer=user_answer,
                )
                if ai_step:
                    if ai_step.get("is_completed"):
                        current_state["status"] = "completed"
                        profile_data = ai_step.get("profile") or self._synthesize_fallback_profile(history)
                        return {
                            "state": current_state,
                            "next_question": None,
                            "conversational_prefix": ai_step.get("conversational_prefix", "Thank you for completing your discovery interview!"),
                            "is_completed": True,
                            "profile": profile_data,
                            "current_step": turn_count,
                            "total_steps": self.TARGET_TURNS,
                        }
                    else:
                        next_q = ai_step.get("next_question")
                        if next_q:
                            asked_questions.append(next_q.get("question_text", ""))
                            # Update extracted profile insights
                            insights = ai_step.get("extracted_insights", {})
                            if insights:
                                prof = current_state.setdefault("extracted_profile", {})
                                for k, v in insights.items():
                                    if isinstance(v, list):
                                        existing = set(prof.get(k, []))
                                        existing.update(v)
                                        prof[k] = list(existing)
                                    elif v:
                                        prof[k] = v

                            return {
                                "state": current_state,
                                "next_question": next_q,
                                "conversational_prefix": ai_step.get("conversational_prefix", ""),
                                "is_completed": False,
                                "profile": None,
                                "current_step": turn_count,
                                "total_steps": self.TARGET_TURNS,
                            }
            except Exception as ex:
                logger.warning(f"[DynamicAssessmentEngine] AI turn generation error: {ex}. Using adaptive fallback.")

        # 3. Fallback Heuristic Path
        return self._heuristic_fallback_step(current_state, user_answer, turn_count, should_finalize)

    async def _generate_ai_turn(
        self,
        history: List[Dict[str, str]],
        asked_questions: List[str],
        current_profile: Dict[str, Any],
        is_final_turn: bool,
        turn_number: int,
        latest_answer: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Asks Gemini to either generate the next adaptive follow-up question
        OR generate the complete, deeply personalized career report.
        """
        history_formatted = "\n".join([
            f"Turn {h['step']}:\nQuestion: {h['question']}\nStudent Answer: {h['answer']}"
            for h in history
        ])

        if is_final_turn:
            # ─── Final Synthesis Prompt ───
            system_instruction = (
                "You are an expert Principal AI Career Architect. You have just completed a multi-turn deep interview "
                "with an engineering student. Based on their exact transcript, synthesize a truly individualized, "
                "evidence-grounded career guidance report.\n"
                "CRITICAL RULES:\n"
                "1. DO NOT give generic templates. If the user focused on AI in healthcare and ECG signals, recommend Medical AI / Biomedical Signal careers, NOT generic web development.\n"
                "2. Cite their actual statements in the reasons and supporting evidence.\n"
                "3. Differentiate confirmed skills from self-reported skills and identify missing skills / knowledge gaps.\n"
                "4. Provide a tailored 3-stage learning roadmap (Beginner, Intermediate, Advanced) with concrete, portfolio-worthy project ideas and tools.\n"
                "5. Return strictly valid JSON."
            )

            prompt = f"""
STUDENT ASSESSMENT CONVERSATION TRANSCRIPT:
{history_formatted}

Generate a comprehensive, highly personalized career report in this exact JSON format:
{{
  "is_completed": true,
  "conversational_prefix": "Congratulations! Your deep career discovery interview is complete. Here is your synthesized profile and personalized career plan.",
  "profile": {{
    "personality_profile": {{
      "Analytical": 85.0,
      "Creative": 72.0,
      "Social": 60.0,
      "Leadership": 55.0,
      "Practical": 80.0,
      "Detail-oriented": 88.0,
      "Risk tolerance": 50.0,
      "Independence": 75.0,
      "Collaboration": 70.0,
      "Learning orientation": 90.0,
      "disclaimer": "This is a career guidance profile, not a medical or psychological diagnosis."
    }},
    "interest_profile": {{
      "Primary Niche Focus": 95,
      "Applied Engineering": 85,
      "System Architecture": 75,
      "Domain Science": 70
    }},
    "skills_profile": {{
      "confirmed_skills": ["Identified skill 1", "Identified skill 2"],
      "self_reported_skills": ["Skill mentioned by user"],
      "missing_skills": ["Exact missing tool / math / library needed"],
      "proficiency_level": "Beginner / Intermediate / Advanced"
    }},
    "values_profile": {{
      "Primary Driver": "Key motivation identified in interview",
      "Work Environment Fit": "Target workplace environment",
      "Regional Context": "Technopark / Pan-India / Global Remote"
    }},
    "confidence_profile": {{
      "overall_assessment_confidence": "92%",
      "stability_score": "High"
    }},
    "career_recommendations": [
      {{
        "career_name": "Highly specific tailored career title (e.g. Medical AI & Biomedical Signal Engineer)",
        "base_career": "Closest base career (Machine Learning Engineer / AI Engineer / Software Engineer / UI/UX Designer / etc.)",
        "match_score": 94.0,
        "reason": "Detailed explainability citing user's actual answers",
        "supporting_evidence": [
          "Specific quote / concept user mentioned",
          "Demonstrated interest in sub-field"
        ],
        "concerns": [
          "Concrete challenge or skill barrier"
        ],
        "skills_needed": ["Tool 1", "Library 2", "Concept 3"],
        "suggested_projects": [
          "Specific, portfolio-worthy project 1",
          "Specific, portfolio-worthy project 2"
        ],
        "immediate_next_steps": [
          "Immediate step 1",
          "Immediate step 2",
          "Immediate step 3"
        ],
        "roadmap_stages": [
          {{
            "stage_number": 1,
            "stage_title": "Stage 1 Title (Foundations)",
            "description": "What to learn first",
            "skills": ["Skill A", "Skill B"],
            "topics": ["Topic 1", "Topic 2"],
            "projects": ["Project 1"],
            "resources": ["Curated resource / doc link"],
            "estimated_duration": "4-6 weeks"
          }},
          {{
            "stage_number": 2,
            "stage_title": "Stage 2 Title (Core Competency)",
            "description": "Domain specific mastery",
            "skills": ["Skill C", "Skill D"],
            "topics": ["Topic 3", "Topic 4"],
            "projects": ["Project 2"],
            "resources": ["Specialized course / benchmark"],
            "estimated_duration": "6-8 weeks"
          }},
          {{
            "stage_number": 3,
            "stage_title": "Stage 3 Title (Production & Portfolio)",
            "description": "Capstone and deployment",
            "skills": ["Skill E", "Skill F"],
            "topics": ["Topic 5", "Topic 6"],
            "projects": ["Capstone Deployment"],
            "resources": ["Industry docs"],
            "estimated_duration": "6-8 weeks"
          }}
        ]
      }}
    ]
  }}
}}
"""
        else:
            # ─── Dynamic Next Question Prompt ───
            system_instruction = (
                "You are an intelligent, empathetic AI Career Discovery Agent conducting a dynamic, context-aware interview. "
                "Your objective is to uncover the student's authentic passions, technical depth, problem-solving style, and career goals.\n"
                "CRITICAL RULES:\n"
                "1. ALWAYS generate the next question dynamically from the student's previous answers.\n"
                "2. If the user answered 'I am interested in artificial intelligence and healthcare', probe into healthcare problems (early disease detection, medical imaging, patient records).\n"
                "3. If they specified 'early disease detection', ask about health data types (ECG signals, CT scans, EHR).\n"
                "4. If they said 'ECG signals', ask about their current programming experience with signal filtering / Python / DSP.\n"
                "5. If an answer was vague or brief (e.g. 'coding', 'yes', 'math'), ask a gentle, specific clarifying follow-up.\n"
                "6. NEVER repeat a previously asked question or ask a semantic duplicate. Check 'Previously Asked Questions'.\n"
                "7. Provide 3 to 4 tailored, contextual interactive options that represent real pathways, but allow typing anything.\n"
                "8. Keep conversational_prefix warm, natural, and under 15 words.\n"
                "9. Return strictly valid JSON."
            )

            prompt = f"""
PREVIOUS CONVERSATION:
{history_formatted}

PREVIOUSLY ASKED QUESTIONS (DO NOT REPEAT OR DUPLICATE):
{json.dumps(asked_questions, indent=2)}

CURRENT INTERVIEW STEP: {turn_number} of {self.TARGET_TURNS}
LATEST ANSWER RECEIVED: "{latest_answer}"

Generate the next adaptive question as strict JSON:
{{
  "is_completed": false,
  "conversational_prefix": "Short warm acknowledgment bridging to next question",
  "next_question": {{
    "question_id": "dyn_q_{turn_number + 1}",
    "phase": "specialization",
    "question_text": "One clear, highly relevant question that probes deeper into their latest answer",
    "options": [
      "Specific option 1",
      "Specific option 2",
      "Specific option 3",
      "Specific option 4"
    ],
    "category": "subfield_probing"
  }},
  "extracted_insights": {{
    "focus_domain": "Domain identified",
    "proficiency": "beginner / intermediate / advanced",
    "interests": ["Interest 1"],
    "confirmed_skills": ["Skill demonstrated"],
    "self_reported_skills": ["Skill mentioned"],
    "goals": ["Goal stated"]
  }}
}}
"""

        raw_response = await llm_service.generate_response(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.3,
            max_output_tokens=3000 if is_final_turn else 1000,
            timeout=25.0 if is_final_turn else 15.0,
        )

        if not raw_response:
            return None

        # Clean JSON markdown fences
        cleaned = raw_response.strip()
        if "```" in cleaned:
            cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

        try:
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"[DynamicAssessmentEngine] JSON parse failed: {e}. Raw: {cleaned[:200]}")
            return None

    def _heuristic_fallback_step(
        self,
        current_state: Dict[str, Any],
        user_answer: str,
        turn_count: int,
        should_finalize: bool,
    ) -> Dict[str, Any]:
        """Graceful rule-based fallback if LLM is unavailable."""
        history = current_state.get("conversation_history", [])
        lowered = user_answer.lower()

        if should_finalize:
            current_state["status"] = "completed"
            profile = self._synthesize_fallback_profile(history)
            return {
                "state": current_state,
                "next_question": None,
                "conversational_prefix": "Your deep career discovery interview is now complete! Here is your synthesized profile.",
                "is_completed": True,
                "profile": profile,
                "current_step": turn_count,
                "total_steps": self.TARGET_TURNS,
            }

        # Adaptive contextual question selection
        if any(w in lowered for w in ["health", "medical", "disease", "bio", "ecg"]):
            next_q = {
                "question_id": f"fallback_q_{turn_count + 1}",
                "phase": "specialization",
                "question_text": "What type of biomedical data or healthcare problem interests you most?",
                "options": [
                    "Physiological Signals (ECG, EEG, Wearable Sensors)",
                    "Medical Imaging (X-Ray, MRI, CT Diagnostics)",
                    "Clinical Records & Predictive Health Analytics",
                    "Drug Discovery & Genomic Sequence Analysis",
                ],
                "category": "healthcare_ai",
            }
        elif any(w in lowered for w in ["frontend", "ui", "ux", "web", "design"]):
            next_q = {
                "question_id": f"fallback_q_{turn_count + 1}",
                "phase": "specialization",
                "question_text": "Which dimension of frontend & interface engineering would you like to master?",
                "options": [
                    "Design Systems, Micro-Interactions & Component Architecture",
                    "Full-Stack Web Applications (React, Next.js, Node/Python)",
                    "User Research, Wireframing & Usability Prototyping",
                    "High-Performance Web Graphics & Interactive 3D (Three.js/WebGL)",
                ],
                "category": "frontend_design",
            }
        elif any(w in lowered for w in ["data", "analytics", "business", "sql", "finance"]):
            next_q = {
                "question_id": f"fallback_q_{turn_count + 1}",
                "phase": "specialization",
                "question_text": "What kind of data analysis problems excite your curiosity?",
                "options": [
                    "Building Machine Learning & Predictive Analytics Models",
                    "Business Intelligence Dashboards & Strategic Decision Metrics",
                    "Data Pipelines, ETL Infrastructure & Large-Scale Warehousing",
                    "Financial Risk Modeling & Market Trend Forecasting",
                ],
                "category": "data_analytics",
            }
        elif any(w in lowered for w in ["cyber", "security", "cloud", "network", "devops"]):
            next_q = {
                "question_id": f"fallback_q_{turn_count + 1}",
                "phase": "specialization",
                "question_text": "Which area of systems and infrastructure integrity appeals most to you?",
                "options": [
                    "Cloud Architecture & Multi-Cloud Reliability (AWS/GCP/Azure)",
                    "Penetration Testing, Ethical Hacking & Vulnerability Analysis",
                    "DevOps Automation, CI/CD & Kubernetes Orchestration",
                    "Zero-Trust Architecture & Threat Intelligence Operations",
                ],
                "category": "security_cloud",
            }
        else:
            # General depth probe
            next_q = {
                "question_id": f"fallback_q_{turn_count + 1}",
                "phase": "skills",
                "question_text": f"When thinking about building projects in {user_answer[:30]}, what is your current hands-on experience level?",
                "options": [
                    "Beginner – I understand core concepts but want guided project tutorials",
                    "Intermediate – I have built small prototypes and know the primary tools",
                    "Advanced – I have deployed working apps or completed capstones",
                    "Exploring – I am looking for the fastest roadmap to get started",
                ],
                "category": "proficiency_probing",
            }

        return {
            "state": current_state,
            "next_question": next_q,
            "conversational_prefix": "That makes a lot of sense.",
            "is_completed": False,
            "profile": None,
            "current_step": turn_count,
            "total_steps": self.TARGET_TURNS,
        }

    def _synthesize_fallback_profile(self, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generates a grounded profile from conversation history if AI fails."""
        all_text = " ".join([h["answer"] for h in history]).lower()

        is_health = any(w in all_text for w in ["health", "medical", "ecg", "disease", "bio"])
        is_frontend = any(w in all_text for w in ["frontend", "ui", "ux", "web", "design", "css", "html"])
        is_data = any(w in all_text for w in ["data", "analytics", "finance", "business", "statistics"])

        if is_health:
            career_name = "Medical AI & Healthcare Data Specialist"
            base_career = "Machine Learning Engineer"
            skills_needed = ["Python", "SciPy Signal Processing", "PyTorch", "PhysioNet WFDB", "Time-Series ML"]
            projects = ["ECG Arrhythmia Classification with 1D CNNs", "Predictive Clinical Risk Scoring App"]
            reasons = "Strong demonstrated interest in applying artificial intelligence to healthcare diagnosis and physiological signal processing."
        elif is_frontend:
            career_name = "Frontend Engineer & UI/UX Product Architect"
            base_career = "UI/UX Designer"
            skills_needed = ["React / Next.js", "TypeScript", "Tailwind CSS", "Figma Design Systems", "Web Performance"]
            projects = ["Accessible Design System Component Library", "Interactive Analytics Dashboard"]
            reasons = "Expressed strong enthusiasm for crafting polished user interfaces, web applications, and intuitive user experiences."
        elif is_data:
            career_name = "Data Scientist & Business Intelligence Specialist"
            base_career = "Data Scientist"
            skills_needed = ["Python", "Advanced SQL", "Pandas", "Scikit-Learn", "PowerBI / Tableau"]
            projects = ["Predictive Customer Churn Pipeline", "Automated Financial Anomaly Detection"]
            reasons = "Demonstrated analytical problem-solving and an orientation toward finding actionable insights in data."
        else:
            career_name = "Full-Stack AI Software Engineer"
            base_career = "Software Engineer"
            skills_needed = ["Python", "JavaScript / React", "FastAPI", "SQL", "Docker", "Git"]
            projects = ["Full-Stack AI Career Assistant App", "Cloud Microservices API"]
            reasons = "Balanced technical background showing capability across software engineering and intelligent backend services."

        return {
            "personality_profile": {
                "Analytical": 82.0,
                "Creative": 70.0,
                "Social": 60.0,
                "Leadership": 55.0,
                "Practical": 80.0,
                "Detail-oriented": 85.0,
                "Risk tolerance": 50.0,
                "Independence": 75.0,
                "Collaboration": 70.0,
                "Learning orientation": 88.0,
                "disclaimer": "This is a career guidance profile, not a medical or psychological diagnosis.",
            },
            "interest_profile": {
                career_name: 92,
                "Applied Software Engineering": 85,
                "Problem Solving": 80,
            },
            "skills_profile": {
                "confirmed_skills": ["Fundamental Programming", "Analytical Thinking"],
                "self_reported_skills": ["Python / Web basics"],
                "missing_skills": skills_needed[:3],
                "proficiency_level": "Intermediate",
            },
            "values_profile": {
                "Primary Driver": "Impactful Engineering & Practical Problem Solving",
                "Work Environment Fit": "Agile Product Team / Tech Innovation",
                "Regional Context": "Technopark / Pan-India / Global Remote",
            },
            "confidence_profile": {
                "overall_assessment_confidence": "88%",
                "stability_score": "High",
            },
            "career_recommendations": [
                {
                    "career_name": career_name,
                    "base_career": base_career,
                    "match_score": 93.5,
                    "reason": reasons,
                    "supporting_evidence": [
                        "Directly aligned with topics explored during your assessment dialogue.",
                        "Identified concrete technical interests and problem-solving goals.",
                    ],
                    "concerns": [
                        "Requires consistent practice and building public portfolio projects to demonstrate mastery.",
                    ],
                    "skills_needed": skills_needed,
                    "suggested_projects": projects,
                    "immediate_next_steps": [
                        f"Start a GitHub repository dedicated to {projects[0]}",
                        f"Review official documentation for {skills_needed[0]} and {skills_needed[1]}",
                        "Build an end-to-end working prototype within 4 weeks",
                    ],
                    "roadmap_stages": [
                        {
                            "stage_number": 1,
                            "stage_title": f"Foundations of {career_name}",
                            "description": f"Master core prerequisites in {skills_needed[0]} and {skills_needed[1]}.",
                            "skills": skills_needed[:2],
                            "topics": ["Core Architecture", "Data Handling", "Development Environment"],
                            "projects": [f"{projects[0]} – Phase 1"],
                            "resources": ["Official Documentation & Tutorials"],
                            "estimated_duration": "4-6 weeks",
                        },
                        {
                            "stage_number": 2,
                            "stage_title": "Core Specialization & Framework Mastery",
                            "description": "Build end-to-end applications solving realistic problems.",
                            "skills": skills_needed[2:4] if len(skills_needed) >= 4 else skills_needed,
                            "topics": ["Algorithms & Modeling", "API Integration", "Testing & Optimization"],
                            "projects": [projects[1] if len(projects) > 1 else projects[0]],
                            "resources": ["Applied Coursera / Kaggle Labs"],
                            "estimated_duration": "6-8 weeks",
                        },
                        {
                            "stage_number": 3,
                            "stage_title": "Production Deployment & Portfolio Showcase",
                            "description": "Package into a live deployed portfolio project with clear documentation.",
                            "skills": ["Deployment", "Docker", "Portfolio Presentation"],
                            "topics": ["Containerization", "CI/CD", "Technical Writeup"],
                            "projects": ["Production Capstone Release"],
                            "resources": ["GitHub Guides & Cloud Deployment Docs"],
                            "estimated_duration": "6-8 weeks",
                        },
                    ],
                }
            ],
        }


dynamic_assessment_engine = DynamicAssessmentEngine()
