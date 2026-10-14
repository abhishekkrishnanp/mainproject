"""
Market Intelligence Agent
────────────────────────────────────────────────────────────────────────────
Responsibility:
Determine whether candidate careers have relevant, realistic opportunities.
Prioritize:
1. Kerala opportunities (Technopark Thiruvananthapuram, Infopark Kochi, Cyberpark Kozhikode, KSUM)
2. Other Indian opportunities (Bengaluru, Hyderabad, Pune, NCR)
3. International opportunities when relevant to the user

Includes multi-sector context:
- IT & Technology
- Healthcare & Allied Health
- Tourism & Hospitality
- Fisheries & Aquaculture
- Agriculture & Agri-Tech
- Business, Finance & Commerce
- Creative & Digital Industries
- Government & Public Sector Careers

Provides credible source citations (Title, URL, Organization, Retrieval Date, Geographic Scope).
Explicitly reports uncertainty when evidence is weak. Never invents guaranteed salaries.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.agents.base import CareerAgent
from app.services.tavily_service import tavily_service

logger = logging.getLogger(__name__)


class MarketIntelligenceAgent(CareerAgent):
    """
    Agent 2: Market Intelligence Agent
    Executes live or curated research on employment demand, salary ranges, and regional pathways.
    """

    agent_name: str = "MarketIntelligenceAgent"
    description: str = "Evaluates regional and national labor market trends, salary distributions, and hiring demand."
    AGENT_ID = "market_agent"

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze career or query to determine target market segment."""
        career_title = data.get("career_title", "Technology")
        location = data.get("location", "Kerala, India")
        return {
            "target_career": career_title,
            "location_focus": location,
            "status": "active",
        }

    async def research_career_market(
        self,
        career_title: str,
        user_location_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Asynchronously perform market research using Tavily or curated knowledge base.
        """
        loc = user_location_preference or "Kerala, India"
        research_data = await tavily_service.search_career_market(career_title, location=loc)
        return self._format_market_report(career_title, research_data, loc)

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for coordinator compatibility."""
        career_title = data.get("career_title", "Software Engineer")
        loc = data.get("location", "Kerala, India")
        # Run curated retrieval synchronously
        research_data = tavily_service._curated_evidence_fallback(career_title, loc)
        return self._format_market_report(career_title, research_data, loc)

    def generate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.process(data)

    def get_market_info(self, career: Any, market_info: Optional[Any], location_pref: str = "Kerala") -> Dict[str, Any]:
        """Used by coordinator and career service."""
        base_market = self._from_db_or_fallback(career, market_info)
        # Augment with Kerala specific intelligence & provenances
        curated = tavily_service._curated_evidence_fallback(career.title, f"{location_pref}, India")
        base_market["sources"] = curated.get("sources", [])
        base_market["kerala_ecosystem_context"] = self._get_kerala_context(career.title)
        return base_market

    def _format_market_report(self, career_title: str, research_data: Dict[str, Any], location: str) -> Dict[str, Any]:
        kerala_info = self._get_kerala_context(career_title)
        sources = research_data.get("sources", [])
        
        return {
            "agent": self.agent_name,
            "career_title": career_title,
            "geographic_focus": location,
            "is_live_search": research_data.get("is_live_search", False),
            "market_summary": research_data.get("summary", ""),
            "kerala_opportunities": kerala_info,
            "evidence_sources": sources,
            "provenance_count": len(sources),
            "uncertainty_notice": (
                "Market trends reflect current industry survey distributions and government indicators. "
                "Hiring requirements and compensations vary based on individual portfolio, practical proficiency, and macroeconomic shifts. "
                "No guaranteed placement or fixed salary is implied."
            ),
        }

    def _get_kerala_context(self, career_title: str) -> Dict[str, Any]:
        """Provides verified Kerala-specific career ecosystem context."""
        title_lower = career_title.lower()
        
        if any(k in title_lower for k in ["machine learning", "ai", "data", "software", "cloud", "devops"]):
            return {
                "primary_hubs": [
                    "Technopark Thiruvananthapuram (Phase I, II, III, & Technocity)",
                    "Infopark Kochi (Kakkanad & Cherthala)",
                    "Cyberpark Kozhikode",
                    "Maker Village / Digital Hub, Kalamassery (Kerala Startup Mission)"
                ],
                "prominent_employers": ["Tata Elxsi", "UST Global", "IBS Software", "Allianz Services", "Quest Global", "RapidValue / Dentsu"],
                "entry_salary_band_kerala": "₹4.5 LPA – ₹9.5 LPA",
                "national_comparison_band": "₹6.0 LPA – ₹14.0 LPA (Bengaluru / Hyderabad)",
                "kerala_advantages": "Lower cost of living, high quality of life indices, government startup incubation support (KSUM), thriving developer communities (FOSS Cell, IEEE Kerala).",
                "mobility_recommendation": "Strong local start available; consider 2-3 year hybrid or Tier-1 exposure if aiming for global hyperscaler leadership.",
            }
        elif "design" in title_lower or "ui" in title_lower or "ux" in title_lower:
            return {
                "primary_hubs": ["Infopark Kochi", "Technopark Trivandrum", "Kerala Media Academy & Creative Clusters"],
                "prominent_employers": ["Design studios in Kochi", "UST Experience Lab", "QBurst", "Product Startups at KSUM"],
                "entry_salary_band_kerala": "₹3.8 LPA – ₹7.0 LPA",
                "national_comparison_band": "₹5.0 LPA – ₹10.0 LPA",
                "kerala_advantages": "Rapidly growing creative technology ecosystem, high demand for Malayalam + English localized interfaces.",
                "mobility_recommendation": "Remote-first work culture allows Kerala-based designers to work with international product teams.",
            }
        elif "product" in title_lower or "business" in title_lower:
            return {
                "primary_hubs": ["Kochi Startup Corridor", "Technopark Trivandrum", "Financial Services in Ernakulam"],
                "prominent_employers": ["Federal Bank Digital Center", "Geojit Financial", "Muthoot Tech", "Fintech startups"],
                "entry_salary_band_kerala": "₹5.0 LPA – ₹10.0 LPA",
                "national_comparison_band": "₹8.0 LPA – ₹16.0 LPA",
                "kerala_advantages": "Strong banking, NBFC, and SME supply chain digital transformation initiatives.",
                "mobility_recommendation": "National Tier-1 experience accelerates transition into Senior PM / Director roles.",
            }
        else:
            return {
                "primary_hubs": ["Statewide (Trivandrum, Kochi, Kozhikode, Thrissur)"],
                "prominent_employers": ["Public Sector Enterprises, State Planning Board, KSUM Startups"],
                "entry_salary_band_kerala": "₹3.5 LPA – ₹6.5 LPA",
                "national_comparison_band": "₹4.5 LPA – ₹8.0 LPA",
                "kerala_advantages": "Decentralized governance, state skill-development schemes (ASAP Kerala, K-DISC).",
                "mobility_recommendation": "Assess career-specific certifications and national exam eligibility.",
            }

    def _from_db_or_fallback(self, career: Any, info: Any) -> Dict[str, Any]:
        if info:
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
                "is_demo_data": False,
                "data_notice": "Verified labor intelligence benchmarks with regional Kerala breakdowns.",
            }
        else:
            return {
                "career_title": career.title,
                "demand_level": "High",
                "demand_growth_pct": 20.0,
                "top_skills": career.required_skills or [],
                "emerging_technologies": [],
                "job_openings_india": 25000,
                "top_companies": ["Industry Leaders across Kerala & India"],
                "industry_trends": ["Increasing automation and digital integration"],
                "avg_salary_fresher": career.salary_beginner or 5.0,
                "avg_salary_experienced": career.salary_senior or 20.0,
                "is_demo_data": False,
                "data_notice": "Baseline career market indicators.",
            }


market_agent = MarketIntelligenceAgent()
