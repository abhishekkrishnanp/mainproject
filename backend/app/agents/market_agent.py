"""
Market Intelligence Agent
────────────────────────────────────────────────────────────────────────────
Responsibility: Provide current market information about a career.

⚠️ DATA NOTICE: All data returned by this agent is SAMPLE/DEMO data stored
in the database. It is clearly labeled as such. To enable real-time market
data, integrate an external API (e.g., LinkedIn, Naukri, NASSCOM) and update
the MarketService layer. This agent will then relay real data.
"""
from __future__ import annotations
from typing import Dict, Any, Optional
import logging

from app.agents.base import CareerAgent

logger = logging.getLogger(__name__)


class MarketIntelligenceAgent(CareerAgent):
    """
    Agent ID: market_agent
    Phase 2 Target: Real-time live Tavily search, job trends, salary insights, Kerala/India/Global demand.
    """

    agent_name: str = "MarketIntelligenceAgent"
    description: str = "Evaluates live labor market trends, salary distributions, and hiring demand."
    AGENT_ID = "market_agent"

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze career or query to determine target market segment."""
        career_title = data.get("career_title", "Technology")
        return {"target_career": career_title, "status": "ready_for_phase_2"}

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process market data retrieval (placeholder interface for Phase 2)."""
        return {
            "status": "pending_live_integration",
            "message": "Market Intelligence Agent is structured for Phase 2 Tavily integration.",
            "data": data,
        }

    def generate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final formatted market intelligence report."""
        return {
            "agent": self.agent_name,
            "status": "skeleton_ready",
            "result": data,
        }

    def get_market_info(self, career: Any, market_info: Optional[Any]) -> Dict[str, Any]:
        if market_info:
            return self._from_db(career, market_info)
        else:
            return self._fallback(career)

    def _from_db(self, career: Any, info: Any) -> Dict[str, Any]:
        return {
            "career_title": career.title,
            "demand_level": info.demand_level,
            "demand_growth_pct": info.demand_growth_pct,
            "top_skills": info.top_skills or [],
            "emerging_technologies": info.emerging_technologies or [],
            "job_openings_india": info.job_openings_india,
            "top_companies": info.top_companies or [],
            "industry_trends": info.industry_trends or [],
            "avg_salary_fresher": info.avg_salary_fresher,
            "avg_salary_experienced": info.avg_salary_experienced,
            "is_demo_data": True,
            "data_notice": (
                "📊 This data is sample/demo data stored in the database for demonstration purposes. "
                "Real-time market data can be connected via external APIs (LinkedIn, Naukri, NASSCOM)."
            ),
        }

    def _fallback(self, career: Any) -> Dict[str, Any]:
        logger.warning(f"[MarketAgent] No market data for {career.title}. Using minimal fallback.")
        return {
            "career_title": career.title,
            "demand_level": "N/A",
            "demand_growth_pct": None,
            "top_skills": career.required_skills or [],
            "emerging_technologies": [],
            "job_openings_india": None,
            "top_companies": [],
            "industry_trends": ["Real-time data not configured"],
            "avg_salary_fresher": career.salary_beginner,
            "avg_salary_experienced": career.salary_senior,
            "is_demo_data": True,
            "data_notice": (
                "📊 No market data record found. Showing base career data only. "
                "Configure an external API for real market intelligence."
            ),
        }
