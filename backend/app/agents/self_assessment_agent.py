"""
Self-Assessment Agent
────────────────────────────────────────────────────────────────────────────
Fully implemented specialized agent for Phase 1 (First 35-40%).
Conducts a deep career discovery interview (25-40 interactions), maintains
memory across questions, dynamically branches based on student category,
and generates initial personality, interest, and top 5 career recommendations.
"""
from typing import Dict, Any, List, Optional
import logging
import asyncio

from app.agents.base import CareerAgent
from app.services.conversational_assessment import assessment_engine
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class SelfAssessmentAgent(CareerAgent):
    """
    Agent 1: Self-Assessment Agent
    Inherits CareerAgent contract.
    """

    agent_name: str = "SelfAssessmentAgent"
    description: str = "Autonomous conversational agent conducting deep multi-dimensional career self-discovery."

    def __init__(self):
        self.engine = assessment_engine

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze current assessment state and extract dimension scores.
        """
        state = data.get("assessment_state", data)
        return {
            "current_question": state.get("current_question_index", 0),
            "total_planned": state.get("total_questions_planned", 25),
            "category": state.get("category"),
            "traits": state.get("personality_traits", {}),
            "answered_count": len(state.get("previous_answers", [])),
        }

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes incoming message from student, updates memory, and selects next step.
        """
        student_id = data.get("student_id", "student_1")
        answer_text = data.get("message", "").strip()
        state = data.get("assessment_state") or self.engine.get_initial_state(student_id)
        current_question_def = data.get("current_question_def")

        # Record answer if message was provided
        if answer_text:
            qid = current_question_def.get("question_id") if current_question_def else f"q_{len(state.get('previous_answers', []))}"
            state = self.engine.record_answer(state, qid, answer_text, current_question_def)

        # Get next question
        next_q = self.engine.get_next_question(state)

        is_completed = (next_q is None)
        profile_data = None
        if is_completed:
            state["status"] = "completed"
            profile_data = self.engine.generate_career_profile(state)

        return {
            "state": state,
            "next_question": next_q,
            "is_completed": is_completed,
            "profile": profile_data,
        }

    def generate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes final self-assessment profile and recommendations.
        """
        state = data.get("assessment_state", data)
        return self.engine.generate_career_profile(state)

    # ─── High-Level Assessment Session Handlers ───

    def start_new_session(self, student_id: str) -> Dict[str, Any]:
        """Start a fresh deep discovery interview."""
        state = self.engine.get_initial_state(student_id)
        first_q = self.engine.get_next_question(state)
        return {
            "state": state,
            "current_question": first_q,
            "is_completed": False,
            "message": "Welcome to your deep career self-assessment discovery. Let's begin by understanding your current educational situation.",
        }

    async def handle_student_response(
        self, student_id: str, current_state: Dict[str, Any], answer_text: str, question_def: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handles student answer, updates state, and provides next question with conversational intro.
        """
        processed = self.process({
            "student_id": student_id,
            "message": answer_text,
            "assessment_state": current_state,
            "current_question_def": question_def,
        })

        new_state = processed["state"]
        next_q = processed["next_question"]
        is_completed = processed["is_completed"]

        conversational_prefix = ""
        # Optionally enhance conversational flow with LLM if available
        if llm_service.is_configured() and next_q and not is_completed:
            prompt = (
                f"The student just answered: '{answer_text}' to the question '{question_def.get('question_text')}'. "
                f"We are continuing our deep career interview. The next question to ask is: '{next_q.get('question_text')}'. "
                f"In 1 short, warm, supportive sentence (under 15 words), acknowledge their previous answer and naturally bridge into the next question."
            )
            llm_text = await llm_service.generate_response(prompt)
            if llm_text:
                conversational_prefix = llm_text.strip() + " "

        return {
            "state": new_state,
            "next_question": next_q,
            "conversational_prefix": conversational_prefix,
            "is_completed": is_completed,
            "profile": processed.get("profile"),
            "current_step": len(new_state.get("previous_answers", [])),
            "total_steps": new_state.get("total_questions_planned", 25),
        }


self_assessment_agent = SelfAssessmentAgent()
