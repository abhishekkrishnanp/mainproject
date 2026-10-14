"""
Self-Assessment Agent
────────────────────────────────────────────────────────────────────────────
Autonomous agent conducting deep, multi-dimensional, context-aware career discovery.
Uses Gemini to dynamically generate follow-up questions from actual conversation history,
tracks previously asked questions, adapts depth, and generates individualized career reports.
"""
from typing import Dict, Any, List, Optional
import logging
import asyncio

from app.agents.base import CareerAgent
from app.services.dynamic_assessment_engine import dynamic_assessment_engine, INITIAL_QUESTION
from app.services.conversational_assessment import assessment_engine
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class SelfAssessmentAgent(CareerAgent):
    """
    Agent 1: Self-Assessment Agent
    Dynamically generates adaptive questions, manages conversation state,
    and synthesizes personalized career trajectories.
    """

    agent_name: str = "SelfAssessmentAgent"
    description: str = "Autonomous conversational agent conducting deep multi-dimensional career self-discovery."

    def __init__(self):
        self.engine = assessment_engine
        self.dynamic_engine = dynamic_assessment_engine

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze current assessment state and extract dimension scores.
        """
        state = data.get("assessment_state", data)
        return {
            "current_question": state.get("current_step", len(state.get("conversation_history", []))),
            "total_planned": state.get("total_steps", self.dynamic_engine.TARGET_TURNS),
            "answered_count": len(state.get("conversation_history", [])),
            "focus_domain": state.get("focus_domain"),
        }

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous fallback for base CareerAgent compliance.
        """
        student_id = data.get("student_id", "student_1")
        state = data.get("assessment_state") or self.dynamic_engine.get_initial_state(student_id)
        history = state.get("conversation_history", [])
        is_completed = len(history) >= self.dynamic_engine.TARGET_TURNS
        profile_data = self.dynamic_engine._synthesize_fallback_profile(history) if is_completed else None

        return {
            "state": state,
            "next_question": None if is_completed else INITIAL_QUESTION,
            "is_completed": is_completed,
            "profile": profile_data,
        }

    def generate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes final self-assessment profile and recommendations.
        """
        state = data.get("assessment_state", data)
        history = state.get("conversation_history", [])
        return self.dynamic_engine._synthesize_fallback_profile(history)

    # ─── High-Level Assessment Session Handlers ───

    def start_new_session(self, student_id: str) -> Dict[str, Any]:
        """Start a fresh dynamic discovery interview."""
        state = self.dynamic_engine.get_initial_state(student_id)
        return {
            "state": state,
            "current_question": INITIAL_QUESTION,
            "is_completed": False,
            "message": "Welcome to your deep career self-assessment discovery. Let's explore your authentic interests, technical passions, and career aspirations.",
        }

    async def handle_student_response(
        self, student_id: str, current_state: Dict[str, Any], answer_text: str, question_def: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handles student answer, updates state, and provides next dynamic question using Gemini.
        """
        # Ensure state has dynamic fields
        if "conversation_history" not in current_state and "previous_answers" in current_state:
            # Migrate older state if present
            current_state["conversation_history"] = [
                {"step": idx + 1, "question": a.get("question_text", "Question"), "answer": a.get("answer", "")}
                for idx, a in enumerate(current_state.get("previous_answers", []))
            ]

        result = await self.dynamic_engine.generate_next_step(
            student_id=student_id,
            current_state=current_state,
            user_answer=answer_text,
            current_question_def=question_def,
        )

        return result


self_assessment_agent = SelfAssessmentAgent()
