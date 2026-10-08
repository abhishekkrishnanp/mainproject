"""
LLM Service for AI-Powered Agentic Career Guidance System
Supports Google Gemini via REST API with configurable model and graceful fallback.
Never crashes if API key is not present or if an error occurs.
"""
import logging
import json
from typing import Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL or "gemini-1.5-flash"
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        )

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    async def generate_response(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        """
        Asynchronously call Google Gemini API.
        Returns generated text or None if call fails or not configured.
        """
        if not self.is_configured():
            return None

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "topP": 0.85,
                "maxOutputTokens": 1024,
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self.endpoint, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                else:
                    logger.warning(f"Gemini API returned status {res.status_code}: {res.text[:200]}")
                    return None
        except Exception as e:
            logger.warning(f"Gemini API invocation error: {e}. Using intelligent fallback.")
            return None


llm_service = LLMService()
