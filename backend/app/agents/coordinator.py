"""
Agent Coordinator
────────────────────────────────────────────────────────────────────────────
Central orchestrator for the multi-agent architecture.

Architecture:
  Frontend → FastAPI Routes → AgentCoordinator → Specialized Agents → DB

Each agent has a single, non-overlapping responsibility:
  profile_agent       – Analyze assessment → structured profile
  career_agent        – Score careers → ranked recommendations
  skill_gap_agent     – Compare student vs career skills → gap report
  roadmap_agent       – Generate personalized learning roadmap
  feasibility_agent   – Evaluate career feasibility → action plan
  market_agent        – Return market intelligence data
  simulation_agent    – Generate 10-year career simulation
"""
from __future__ import annotations
import logging
from typing import Dict, Any, List, Optional

from app.agents.profile_agent import ProfileAnalysisAgent
from app.agents.career_agent import CareerRecommendationAgent
from app.agents.skill_gap_agent import SkillGapAgent
from app.agents.roadmap_agent import RoadmapAgent
from app.agents.feasibility_agent import FeasibilityAgent
from app.agents.market_agent import MarketIntelligenceAgent
from app.agents.simulation_agent import CareerSimulationAgent

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """
    Routes tasks to appropriate specialized agents.
    All agent instances are lightweight and stateless.
    """

    def __init__(self):
        self.profile_agent = ProfileAnalysisAgent()
        self.career_agent = CareerRecommendationAgent()
        self.skill_gap_agent = SkillGapAgent()
        self.roadmap_agent = RoadmapAgent()
        self.feasibility_agent = FeasibilityAgent()
        self.market_agent = MarketIntelligenceAgent()
        self.simulation_agent = CareerSimulationAgent()
        logger.info("[AgentCoordinator] Initialized with 7 specialized agents.")

    # ─── Task: Profile Analysis ───────────────────────────────────────────────
    def run_profile_analysis(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("[AgentCoordinator] → profile_agent")
        return self.profile_agent.analyze(assessment_data)

    # ─── Task: Career Recommendations ────────────────────────────────────────
    def run_career_recommendations(
        self, profile: Dict[str, Any], careers: List[Any]
    ) -> List[Dict[str, Any]]:
        logger.info("[AgentCoordinator] → career_agent")
        return self.career_agent.recommend(profile, careers)

    # ─── Task: Skill Gap Analysis ────────────────────────────────────────────
    def run_skill_gap(
        self, student_skill_scores: Dict[str, float], career: Any
    ) -> Dict[str, Any]:
        logger.info(f"[AgentCoordinator] → skill_gap_agent for {career.title}")
        return self.skill_gap_agent.analyze(student_skill_scores, career)

    # ─── Task: Roadmap Generation ─────────────────────────────────────────────
    def run_roadmap(self, career: Any, skill_gap: Dict[str, Any]) -> List[Dict[str, Any]]:
        logger.info(f"[AgentCoordinator] → roadmap_agent for {career.title}")
        return self.roadmap_agent.generate(career, skill_gap)

    # ─── Task: Feasibility Evaluation ────────────────────────────────────────
    def run_feasibility(
        self, profile: Dict[str, Any], career: Any, skill_gap: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info(f"[AgentCoordinator] → feasibility_agent for {career.title}")
        return self.feasibility_agent.evaluate(profile, career, skill_gap)

    # ─── Task: Market Intelligence ───────────────────────────────────────────
    def run_market_intelligence(self, career: Any, market_info: Optional[Any]) -> Dict[str, Any]:
        logger.info(f"[AgentCoordinator] → market_agent for {career.title}")
        return self.market_agent.get_market_info(career, market_info)

    # ─── Task: Career Simulation ─────────────────────────────────────────────
    def run_simulation(self, career: Any) -> List[Dict[str, Any]]:
        logger.info(f"[AgentCoordinator] → simulation_agent for {career.title}")
        return self.simulation_agent.simulate(career)


# ─── Singleton Instance ───────────────────────────────────────────────────────
coordinator = AgentCoordinator()
