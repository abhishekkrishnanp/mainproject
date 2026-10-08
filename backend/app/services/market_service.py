"""
Market Service
────────────────────────────────────────────────────────────────────────────
Service layer for market intelligence data. Designed so external APIs
(LinkedIn, Naukri, NASSCOM, BLS) can be connected in the future.

Currently: reads from the database (seeded demo data, clearly labeled).
Future:    fetch from external API → update DB → return fresh data.
"""
from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session
from app.models.career import MarketInfo, Career
from app.agents.coordinator import coordinator
import logging

logger = logging.getLogger(__name__)


def get_market_data(db: Session, career_id: int) -> dict:
    """
    Retrieve market intelligence for a career.
    Currently reads from the seeded database (demo data).
    To add a real data source: implement fetch_from_external_api() and
    call it here, then update the MarketInfo record.
    """
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise ValueError(f"Career with id {career_id} not found")

    market_info = db.query(MarketInfo).filter(MarketInfo.career_id == career_id).first()

    # Route through market agent (which also handles the fallback case)
    return coordinator.run_market_intelligence(career, market_info)


# ── Future hook for real-time data ────────────────────────────────────────────
def fetch_from_external_api(career_title: str) -> Optional[dict]:
    """
    TODO: Integrate a real job market API here.
    Example sources:
      - https://api.linkedin.com/v2/jobSearch
      - https://devapi.getpaidapi.com/salary
      - https://rapidapi.com (job board APIs)
    
    Returns None if no external API is configured.
    """
    logger.info(f"[MarketService] External API not configured. Returning None for '{career_title}'.")
    return None
