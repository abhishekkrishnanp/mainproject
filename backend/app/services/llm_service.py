"""
LLM Service for AI-Powered Agentic Career Guidance System
────────────────────────────────────────────────────────────────────────────
Integrates Google Gemini using the official Google Gen AI SDK (google-genai).
Includes:
- Robust error handling, configurable timeouts, and graceful fallbacks.
- Domain-specific prompt generators for:
    1. Career Recommendations based on interests & skills
    2. Personalized Roadmap Generation
    3. Skill-Gap Analysis
    4. Career Question Answering (Student & Parent context)
    5. Career Myth Clarification
- Ensures API keys are never leaked to logs or clients.
"""
from __future__ import annotations
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List

from app.config import settings

logger = logging.getLogger(__name__)

# Try to import official google-genai SDK
try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    GENAI_SDK_AVAILABLE = True
except ImportError:
    GENAI_SDK_AVAILABLE = False
    logger.warning("google-genai SDK not found. LLMService will use fallback mechanisms.")


FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-flash-latest"
]


class LLMService:
    """
    Reusable service for interacting with Google Gemini models
    via the official Google Gen AI SDK.
    """

    def __init__(self):
        self._refresh_client()

    def _refresh_client(self):
        self.api_key = (settings.GEMINI_API_KEY or "").strip()
        self.model = settings.GEMINI_MODEL or "gemini-3.5-flash-lite"
        self._client = None

        if GENAI_SDK_AVAILABLE and self.is_configured():
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Google GenAI Client: {e}")
                self._client = None

    def is_configured(self) -> bool:
        """Returns True if a valid API key is present."""
        return bool(self.api_key and len(self.api_key) > 5)

    def get_status(self) -> Dict[str, Any]:
        """Provides status without exposing the key."""
        return {
            "configured": self.is_configured(),
            "model": self.model,
            "sdk_installed": GENAI_SDK_AVAILABLE,
            "provider": "Google Gemini"
        }

    async def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        timeout: float = 15.0,
        temperature: float = 0.4,
        max_output_tokens: int = 1500
    ) -> Optional[str]:
        """
        Asynchronously call Google Gemini via the official SDK with a timeout.
        Returns generated text or None on failure/unconfigured.
        """
        if not self.is_configured():
            return None

        if not self._client:
            self._refresh_client()
            if not self._client:
                return None

        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        for candidate_model in models_to_try:
            async def _call():
                config = types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    system_instruction=system_instruction if system_instruction else None
                )
                response = await self._client.aio.models.generate_content(
                    model=candidate_model,
                    contents=prompt,
                    config=config
                )
                return response.text if response else None

            try:
                result = await asyncio.wait_for(_call(), timeout=timeout)
                if result:
                    return result
            except asyncio.TimeoutError:
                logger.warning(f"Gemini API call ({candidate_model}) timed out after {timeout} seconds.")
            except Exception as e:
                logger.warning(f"Gemini API invocation error ({candidate_model}): {str(e)[:160]}. Trying fallback...")

        return None

    async def chat_with_history(
        self,
        current_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        mode: str = "student",
        student_context: Optional[Dict[str, Any]] = None,
        timeout: float = 15.0
    ) -> Optional[str]:
        """
        Multi-turn conversational generation using Gemini official SDK.
        Preserves conversation context for follow-up questions while maintaining token limits.
        """
        # Exact prompt guidelines specified for Career Guidance System
        if mode == "parent":
            system_instruction = (
                "You are an intelligent AI Career Guidance Assistant specializing in Parent Advisory. "
                "Your purpose is to help parents understand modern career options, understand their child's strengths, "
                "and support their professional development without pressure.\n\n"
                "Key Rules:\n"
                "- Ask relevant follow-up questions when the child's education, skills, or interests are unclear.\n"
                "- Use simple, friendly, professional, non-technical language.\n"
                "- Present roadmaps as numbered steps and comparisons as markdown tables when useful.\n"
                "- Explain modern job ecosystems (e.g. Kerala's Technopark Thiruvananthapuram, Infopark Kochi, pan-India, and global avenues).\n"
                "- Do not guarantee employment, salary, admission, or future career success.\n"
                "- Clearly distinguish verified information from estimates and predictions. Never invent current job openings, salary figures, scholarship deadlines, or exam dates.\n"
                "- When reliable current information is unavailable, explain this limitation and recommend checking official sources.\n"
                "- Respect privacy and treat recommendations as supportive guidance, not absolute mandates."
            )
        else:
            system_instruction = (
                "You are an intelligent AI Career Guidance Assistant. Your purpose is to help students explore "
                "career options, understand their strengths, identify skill gaps, and plan their professional development.\n\n"
                "Key Instructions:\n"
                "- Ask relevant follow-up questions when the student's interests, education, skills, or goals are unclear.\n"
                "- Provide personalized recommendations with clear explanations rather than making unsupported assumptions.\n"
                "- Use simple, friendly, professional language.\n"
                "- Present roadmaps as numbered steps and comparisons as tables when useful.\n"
                "- Do not guarantee employment, salary, admission, or future career success.\n"
                "- Clearly distinguish verified information from estimates and predictions. Never invent current job openings, salary figures, scholarship deadlines, examination dates, or eligibility requirements.\n"
                "- When current information is required, use verified sources if available. If reliable information is unavailable, explain this limitation and recommend checking the relevant official source.\n"
                "- Respect user privacy and do not request unnecessary sensitive personal information.\n"
                "- Treat career recommendations as guidance, not as absolute decisions about a student's future."
            )

        if not self.is_configured():
            return None

        if not self._client:
            self._refresh_client()
            if not self._client:
                return None

        # Build conversation contents for Gemini
        # Truncate history to recent 8 turns to keep context fast and within budget
        history_turns = (conversation_history or [])[-8:]
        
        # Prepare contents
        contents = []
        for turn in history_turns:
            role = turn.get("role", "user")
            text = (turn.get("text") or turn.get("message") or "").strip()
            if not text:
                continue
            gemini_role = "model" if role in ["assistant", "model", "bot"] else "user"
            contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=text)]
                )
            )

        # Context prefix if available
        context_prefix = ""
        if student_context:
            name = student_context.get("student_name")
            edu = student_context.get("education_level")
            page = student_context.get("current_page")
            details = []
            if name: details.append(f"Student: {name}")
            if edu: details.append(f"Level: {edu}")
            if page: details.append(f"Current Screen: {page}")
            if details:
                context_prefix = f"[{', '.join(details)}]\n"

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=f"{context_prefix}{current_message}")]
            )
        )

        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        for candidate_model in models_to_try:
            async def _call_chat():
                config = types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=1500,
                    system_instruction=system_instruction
                )
                response = await self._client.aio.models.generate_content(
                    model=candidate_model,
                    contents=contents,
                    config=config
                )
                return response.text if response else None

            try:
                result = await asyncio.wait_for(_call_chat(), timeout=timeout)
                if result:
                    return result
            except asyncio.TimeoutError:
                logger.warning(f"Gemini chat call ({candidate_model}) timed out after {timeout} seconds.")
            except Exception as e:
                logger.warning(f"Gemini chat invocation error ({candidate_model}): {str(e)[:160]}. Trying fallback...")

        return None

    # ──────────────────────────────────────────────────────────────────────────
    # Career Feature 1: Recommendations based on interests & skills
    # ──────────────────────────────────────────────────────────────────────────
    async def recommend_careers_with_llm(
        self,
        interests: List[str],
        skills: List[str],
        education_level: str = "Undergraduate",
        aspirations: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized career recommendations based on student input.
        """
        sys_inst = (
            "You are an expert AI Career Guidance Counselor. Given a student's interests, "
            "existing skills, and education level, recommend the top 3-4 suitable career paths. "
            "For each career provide: title, match_score (0-100), why_recommended (evidence-based explanation), "
            "growth_outlook, and top_next_steps. Return valid JSON."
        )

        prompt = (
            f"Student Profile:\n"
            f"- Education Level: {education_level}\n"
            f"- Core Interests: {', '.join(interests) if interests else 'General technology and problem solving'}\n"
            f"- Current Skills: {', '.join(skills) if skills else 'Beginner computer and logic skills'}\n"
            f"- Aspirations: {aspirations or 'Build a sustainable and rewarding modern career'}\n\n"
            f"Provide recommendations in this JSON structure:\n"
            f"{{\n"
            f'  "recommendations": [\n'
            f'    {{\n'
            f'      "title": "Career Title",\n'
            f'      "match_score": 88,\n'
            f'      "why_recommended": "Reasoning based on skills and interests",\n'
            f'      "growth_outlook": "High Demand / Emerging",\n'
            f'      "top_next_steps": ["Step 1", "Step 2"]\n'
            f'    }}\n'
            f'  ],\n'
            f'  "summary_advice": "High level guidance paragraph"\n'
            f"}}"
        )

        raw = await self.generate_response(prompt, system_instruction=sys_inst, temperature=0.3)
        if raw:
            try:
                # Strip markdown code blocks if returned
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[1]
                    if cleaned.endswith("```"):
                        cleaned = cleaned.rsplit("\n", 1)[0]
                    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned)
            except Exception as ex:
                logger.warning(f"Could not parse Gemini JSON response for recommendations: {ex}")

        # Graceful heuristic fallback if LLM is unavailable
        return {
            "source": "heuristic_fallback",
            "recommendations": [
                {
                    "title": "Software Engineer",
                    "match_score": 85,
                    "why_recommended": f"Strong alignment with skills: {', '.join(skills[:3]) if skills else 'Analytical thinking'}",
                    "growth_outlook": "High Demand",
                    "top_next_steps": ["Deepen Data Structures & Algorithms", "Build 2 full-stack projects"]
                },
                {
                    "title": "Data Analyst / AI Specialist",
                    "match_score": 80,
                    "why_recommended": f"Matches interests in {', '.join(interests[:2]) if interests else 'technology'}",
                    "growth_outlook": "Rapidly Growing",
                    "top_next_steps": ["Master Python & SQL", "Explore Machine Learning foundations"]
                }
            ],
            "summary_advice": "Focus on turning your core interests into project portfolios and verifiable problem-solving skills."
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Career Feature 2: Personalized Career Roadmap Generation
    # ──────────────────────────────────────────────────────────────────────────
    async def generate_roadmap_with_llm(
        self,
        target_career: str,
        current_skills: List[str],
        timeline_months: int = 6
    ) -> Dict[str, Any]:
        """
        Generate a milestone-by-milestone actionable learning roadmap.
        """
        sys_inst = (
            "You are a Senior Technical Career Architect. Create a structured, realistic "
            f"{timeline_months}-month milestone roadmap for a student wanting to become a {target_career}. "
            "Break the plan into logical phases (e.g. Month 1-2 Foundations, Month 3-4 Specialization, Month 5-6 Capstone & Job Prep). "
            "Output valid JSON."
        )

        prompt = (
            f"Target Career: {target_career}\n"
            f"Student's Current Skills: {', '.join(current_skills) if current_skills else 'Beginner level'}\n"
            f"Timeline: {timeline_months} months\n\n"
            f"Return JSON format:\n"
            f"{{\n"
            f'  "career": "{target_career}",\n'
            f'  "timeline_months": {timeline_months},\n'
            f'  "milestones": [\n'
            f'    {{\n'
            f'      "phase": "Month 1-2: Foundations",\n'
            f'      "focus_areas": ["Skill A", "Skill B"],\n'
            f'      "tasks": ["Task 1", "Task 2"],\n'
            f'      "expected_outcome": "Outcome summary"\n'
            f'    }}\n'
            f'  ],\n'
            f'  "recommended_certifications_or_projects": ["Project 1", "Certification 1"]\n'
            f"}}"
        )

        raw = await self.generate_response(prompt, system_instruction=sys_inst, temperature=0.3)
        if raw:
            try:
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[1]
                    if cleaned.endswith("```"):
                        cleaned = cleaned.rsplit("\n", 1)[0]
                    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned)
            except Exception as ex:
                logger.warning(f"Failed to parse LLM roadmap JSON: {ex}")

        # Fallback
        return {
            "source": "heuristic_fallback",
            "career": target_career,
            "timeline_months": timeline_months,
            "milestones": [
                {
                    "phase": "Phase 1: Core Fundamentals (Month 1-2)",
                    "focus_areas": ["Programming fundamentals", "Domain tools"],
                    "tasks": ["Complete guided coursework", "Solve daily practice challenges"],
                    "expected_outcome": f"Solid working proficiency for {target_career}"
                },
                {
                    "phase": "Phase 2: Project Building (Month 3-4)",
                    "focus_areas": ["Real-world application", "System integration"],
                    "tasks": ["Build 2 production-grade portfolio items", "Version control with Git"],
                    "expected_outcome": "Demonstrable portfolio repository"
                },
                {
                    "phase": "Phase 3: Career Readiness (Month 5-6)",
                    "focus_areas": ["Mock interviews", "Resume & LinkedIn optimization"],
                    "tasks": ["Apply to internships/entry roles", "Technical interview preparation"],
                    "expected_outcome": "Interview-ready profile"
                }
            ],
            "recommended_certifications_or_projects": [
                f"Full-stack end-to-end {target_career} capstone project",
                "Industry recognized foundational credential"
            ]
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Career Feature 3: Skill-Gap Analysis
    # ──────────────────────────────────────────────────────────────────────────
    async def analyze_skill_gap_with_llm(
        self,
        target_career: str,
        student_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Identify missing critical skills, prioritize them, and provide learning advice.
        """
        sys_inst = (
            "You are an AI Technical Hiring Evaluator. Analyze the gap between a student's current skills "
            f"and the realistic market expectations for '{target_career}'. "
            "Highlight strengths, missing required skills, missing nice-to-have skills, and priority order. "
            "Output valid JSON."
        )

        prompt = (
            f"Target Career: {target_career}\n"
            f"Student's Current Skills: {', '.join(student_skills) if student_skills else 'None specified'}\n\n"
            f"Return JSON format:\n"
            f"{{\n"
            f'  "career": "{target_career}",\n'
            f'  "readiness_score": 65,\n'
            f'  "acquired_skills": ["Skill 1"],\n'
            f'  "missing_critical_skills": ["Critical 1", "Critical 2"],\n'
            f'  "missing_preferred_skills": ["Preferred 1"],\n'
            f'  "priority_learning_order": ["Step 1", "Step 2"],\n'
            f'  "market_insight": "Current hiring trends for this role"\n'
            f"}}"
        )

        raw = await self.generate_response(prompt, system_instruction=sys_inst, temperature=0.2)
        if raw:
            try:
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[1]
                    if cleaned.endswith("```"):
                        cleaned = cleaned.rsplit("\n", 1)[0]
                    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned)
            except Exception as ex:
                logger.warning(f"Failed to parse skill gap JSON: {ex}")

        # Fallback
        return {
            "source": "heuristic_fallback",
            "career": target_career,
            "readiness_score": 60,
            "acquired_skills": student_skills,
            "missing_critical_skills": ["Advanced Problem Solving", f"Core {target_career} Tools", "System Architecture"],
            "missing_preferred_skills": ["Cloud Deployment", "Automated Testing"],
            "priority_learning_order": ["Master the primary programming framework", "Complete practical projects"],
            "market_insight": f"Companies hiring for {target_career} prioritize hands-on problem solving over passive course certificates."
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Career Feature 4: Career Question Answering
    # ──────────────────────────────────────────────────────────────────────────
    async def answer_career_question(
        self,
        question: str,
        user_role: str = "student",
        student_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Answer user questions with context-aware, empathetic, and factual guidance.
        """
        ctx_str = ""
        if student_context:
            ctx_str = (
                f"Student Education: {student_context.get('education_level', 'College')}, "
                f"Branch: {student_context.get('branch', 'Engineering/General')}, "
                f"Target Interests: {student_context.get('interests', 'Tech')}"
            )

        if user_role == "parent":
            sys_inst = (
                "You are the ACGS Parent Advisory Assistant in the AI-Powered Career Guidance System. "
                "Respond with empathy, clarity, and non-technical explanations. "
                "Help parents understand modern careers, alleviate anxiety about job stability, "
                "and explain regional hubs (Kerala Technopark/Infopark and pan-India) as well as global avenues. "
                "Keep answers reassuring, structured, and under 150 words."
            )
        else:
            sys_inst = (
                "You are the ACGS Career Guidance Mentor in the AI-Powered Career Guidance System. "
                "Provide direct, motivating, actionable advice to students. "
                "Reference practical industry skills, courses, portfolio strategies, and competitive hiring realities. "
                "Keep answers organized with bullet points where helpful and under 160 words."
            )

        prompt = f"User Question: {question}\nContext: {ctx_str}"
        llm_reply = await self.generate_response(prompt, system_instruction=sys_inst)

        if llm_reply:
            return {
                "answer": llm_reply.strip(),
                "role": user_role,
                "source": "gemini"
            }

        # Fallback answer
        return {
            "answer": (
                "To succeed in this career direction, focus on solid foundational principles: "
                "1) Build real demonstrable projects rather than just collecting certificates; "
                "2) Keep your problem-solving and communication skills sharp; "
                "3) Connect with alumni and professionals working in your target industry."
            ),
            "role": user_role,
            "source": "system_fallback"
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Career Feature 5: Career Myth Clarification
    # ──────────────────────────────────────────────────────────────────────────
    async def clarify_career_myths(
        self,
        career_or_topic: str
    ) -> Dict[str, Any]:
        """
        Identify and debunk common myths and misconceptions about careers.
        """
        sys_inst = (
            "You are a Career Myth-Buster and Fact-Checker. For the given career or domain, "
            "identify 3 common myths, state the real fact for each, and provide a grounding takeaway. "
            "Return valid JSON."
        )

        prompt = (
            f"Career or Domain: {career_or_topic}\n\n"
            f"Provide response in this JSON format:\n"
            f"{{\n"
            f'  "career": "{career_or_topic}",\n'
            f'  "myths": [\n'
            f'    {{\n'
            f'      "myth": "Common misconception",\n'
            f'      "reality": "Factual reality",\n'
            f'      "impact": "Why believing this hurts students"\n'
            f'    }}\n'
            f'  ],\n'
            f'  "verdict": "Concluding takeaway"\n'
            f"}}"
        )

        raw = await self.generate_response(prompt, system_instruction=sys_inst, temperature=0.2)
        if raw:
            try:
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[1]
                    if cleaned.endswith("```"):
                        cleaned = cleaned.rsplit("\n", 1)[0]
                    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned)
            except Exception as ex:
                logger.warning(f"Failed to parse myth buster JSON: {ex}")

        # Fallback
        return {
            "source": "heuristic_fallback",
            "career": career_or_topic,
            "myths": [
                {
                    "myth": f"You must be a prodigy or have a top-tier degree to succeed in {career_or_topic}.",
                    "reality": "Consistent deliberate practice, curiosity, and practical projects carry far more weight in modern hiring.",
                    "impact": "Causes students to self-select out and abandon ambition prematurely."
                },
                {
                    "myth": "AI will eliminate all entry-level positions in this field immediately.",
                    "reality": "AI tools automate boilerplate tasks; candidates who learn how to leverage AI tools are more productive and in higher demand.",
                    "impact": "Paralyzes learners with unnecessary panic instead of adopting new tools."
                }
            ],
            "verdict": "Focus on verified competencies, continuous learning, and hands-on portfolio proof."
        }


# Global singleton instance
llm_service = LLMService()
