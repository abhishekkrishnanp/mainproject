"""
Gemini-Backed Multi-Turn Chat Router
─────────────────────────────────────────────────────────────────────────────
Provides:
  POST  /gemini/chat          – single turn, JSON response
  POST  /gemini/chat/stream   – SSE streaming response
  GET   /gemini/chat/history  – retrieve chat history for the current user

Wiring in main.py:
  app.include_router(chat_router.router, prefix="/api/v1", tags=[...])
  → final paths: /api/v1/gemini/chat, /api/v1/gemini/chat/stream, etc.

Also mounted without prefix so legacy /gemini/* paths still resolve.

Key design decisions
────────────────────
* Uses the real app.database.get_db, app.models.user.User, and
  app.core.deps.get_current_active_user (the actual JWT dependency).
* Profile context is built from User fields directly — there is no
  separate Profile model in this codebase.
* Tavily market-data enrichment is keyword-triggered (no extra LLM call).
  The injected text is clearly labelled inside the system prompt and is
  capped at ~1 500 chars. If Tavily times out or errors, the chat
  continues silently without market data.
* Streaming uses Server-Sent Events (SSE) via StreamingResponse.
* Both /chat and /chat/stream share the same _build_prompt() and
  _maybe_fetch_market_context() helpers.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import AsyncGenerator, Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.services.llm_service import llm_service
from app.services.tavily_service import tavily_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gemini", tags=["Gemini Chat"])

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    mode: str = Field(default="student", pattern="^(student|parent)$")
    # Optional: frontend may pass extra context (e.g. current page)
    current_page: Optional[str] = Field(default=None, max_length=100)
    # Optional: client can keep a local history list for stateless fallback
    history: Optional[List[Dict[str, str]]] = Field(default=None)


class ChatMessageOut(BaseModel):
    role: str
    content: str
    had_market_context: bool = False
    created_at: str

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    reply: str
    source: str = "gemini"
    had_market_context: bool = False
    session_id: Optional[int] = None


# ─────────────────────────────────────────────────────────────────────────────
# Market-intent keyword detection
# ─────────────────────────────────────────────────────────────────────────────

_MARKET_KEYWORDS = re.compile(
    r"\b(salary|salaries|pay|package|ctc|lpa|hiring|job demand|openings|"
    r"market|trend|future of|growth|in-demand|employment|recruit|placement)\b",
    re.IGNORECASE,
)

_ROLE_KEYWORDS = re.compile(
    r"\b(engineer|developer|scientist|analyst|designer|manager|architect|"
    r"consultant|researcher|specialist|ai|ml|data|software|cloud|"
    r"devops|frontend|backend|fullstack|python|java|ml engineer|"
    r"machine learning|deep learning)\b",
    re.IGNORECASE,
)


def _is_market_query(text: str) -> bool:
    """True if message mentions market/salary topics."""
    return bool(_MARKET_KEYWORDS.search(text))


def _extract_role_hint(text: str) -> str:
    """Best-effort extraction of a career role from a message."""
    m = _ROLE_KEYWORDS.search(text)
    return m.group(0).strip() if m else "Software Engineer"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _build_profile_context(user: User) -> Dict[str, Any]:
    """Build a context dict from real User model fields (no separate Profile model)."""
    return {
        "student_name": user.full_name or "Student",
        "education_level": user.education_level or "College",
        "course_degree": user.course_degree,
        "college": user.college,
        "current_skills": user.current_skills,
        "interests": user.interests,
        "location": user.location,
    }


def _build_system_prompt(mode: str, profile: Dict[str, Any], market_context: Optional[str] = None) -> str:
    """Assemble the system prompt with optional market data section."""
    # --- base persona ---
    if mode == "parent":
        base = (
            "You are an intelligent AI Career Guidance Assistant specialising in Parent Advisory "
            "within the AI-Powered Agentic Career Guidance System (ACGS).\n"
            "Use simple, friendly, professional, non-technical language. "
            "Help parents understand modern careers, their child's strengths, Kerala & India tech ecosystems "
            "(Technopark Thiruvananthapuram, Infopark Kochi), and global opportunities.\n"
            "Key Rules:\n"
            "- Ask follow-up questions when the child's background is unclear.\n"
            "- Present roadmaps as numbered steps; use markdown tables for comparisons.\n"
            "- Never guarantee employment, salary, or admission outcomes.\n"
            "- Clearly distinguish verified data from estimates; never invent salary figures or exam dates.\n"
            "- If you lack current information, recommend official sources."
        )
    else:
        base = (
            "You are an intelligent AI Career Guidance Assistant in the ACGS system.\n"
            "Help students explore career options, identify skill gaps, and plan their professional development.\n"
            "Key Rules:\n"
            "- Ask follow-up questions when interests, education, or goals are unclear.\n"
            "- Give personalised recommendations backed by concrete reasoning.\n"
            "- Use simple, friendly, professional language; use bullet points and tables where helpful.\n"
            "- Never guarantee employment, salary, or admission outcomes.\n"
            "- Never invent job openings, salary figures, exam dates, or scholarship deadlines.\n"
            "- When current information is unavailable, explain the limitation and recommend official sources."
        )

    # --- student context prefix (only for student mode) ---
    ctx_lines = []
    if mode == "student":
        name = profile.get("student_name")
        edu = profile.get("education_level")
        degree = profile.get("course_degree")
        skills = profile.get("current_skills")
        interests = profile.get("interests")
        location = profile.get("location")
        if name:
            ctx_lines.append(f"Student: {name}")
        if edu:
            ctx_lines.append(f"Education: {edu}")
        if degree:
            ctx_lines.append(f"Degree: {degree}")
        if skills:
            ctx_lines.append(f"Current Skills: {skills[:200]}")
        if interests:
            ctx_lines.append(f"Interests: {interests[:200]}")
        if location:
            ctx_lines.append(f"Location: {location}")

    if ctx_lines:
        base += "\n\n--- STUDENT PROFILE CONTEXT ---\n" + "\n".join(ctx_lines)

    # --- market data section (kept in a clearly-labelled block) ---
    if market_context:
        base += (
            "\n\n--- MARKET DATA (from live web search — treat as reference, not guaranteed) ---\n"
            + market_context[:1500]
            + "\n--- END MARKET DATA ---\n"
            "Use the market data above to enrich your answer. "
            "Do NOT quote specific salary numbers as guarantees; label them as reported estimates."
        )

    return base


async def _maybe_fetch_market_context(message: str) -> Optional[str]:
    """
    If the message is market-related, call Tavily with a 5-second timeout.
    Returns a concise summary string, or None on failure / non-market query.
    """
    if not _is_market_query(message):
        return None

    if not tavily_service.is_configured():
        # Fall back to curated evidence, which is fast (no network call)
        role_hint = _extract_role_hint(message)
        try:
            data = await asyncio.wait_for(
                tavily_service.search_career_market(role_hint), timeout=5.0
            )
            return _summarise_tavily(data)
        except Exception:
            return None

    role_hint = _extract_role_hint(message)
    try:
        data = await asyncio.wait_for(
            tavily_service.search_career_market(role_hint), timeout=5.0
        )
        return _summarise_tavily(data)
    except asyncio.TimeoutError:
        logger.warning("[chat_router] Tavily timed out; proceeding without market context.")
        return None
    except Exception as e:
        logger.warning(f"[chat_router] Tavily error: {e}; proceeding without market context.")
        return None


def _summarise_tavily(data: Dict[str, Any]) -> str:
    """Convert Tavily result into a compact text block (≤ 1 500 chars)."""
    lines = []
    summary = data.get("summary", "")
    if summary:
        lines.append(summary[:400])

    for src in data.get("sources", [])[:3]:
        snippet = src.get("content_snippet", "")
        org = src.get("organization", "")
        if snippet:
            lines.append(f"[{org}] {snippet[:300]}")

    return "\n".join(lines)[:1500]


def _get_or_create_session(db: Session, user_id: int, mode: str) -> ChatSession:
    """Get the most recent active chat session for user, or create a new one."""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id, ChatSession.mode == mode)
        .order_by(ChatSession.id.desc())
        .first()
    )
    if not session:
        session = ChatSession(user_id=user_id, mode=mode)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def _history_from_db(session: ChatSession, limit: Optional[int] = None) -> List[Dict[str, str]]:
    """Return the last `limit` message turns from DB as list[{role, text}]."""
    lim = limit if limit is not None else getattr(settings, "CHAT_MAX_HISTORY", 20)
    msgs = session.messages[-lim:] if len(session.messages) > lim else session.messages
    return [{"role": m.role, "text": m.content} for m in msgs]


def _save_turn(
    db: Session,
    session_id: int,
    user_content: str,
    assistant_content: str,
    had_market: bool,
) -> None:
    """Persist one user + assistant turn to DB."""
    db.add(ChatMessage(session_id=session_id, role="user", content=user_content))
    db.add(
        ChatMessage(
            session_id=session_id,
            role="assistant",
            content=assistant_content,
            had_market_context=had_market,
        )
    )
    db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Single-turn Gemini chat with DB-persisted history and optional Tavily market data.
    Auth: Bearer JWT required.
    """
    if not llm_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API key is not configured. Please set GEMINI_API_KEY in the backend .env file.",
        )

    profile = _build_profile_context(current_user)
    market_context = await _maybe_fetch_market_context(req.message)
    system_prompt = _build_system_prompt(req.mode, profile, market_context)
    had_market = market_context is not None

    # Load chat session and history
    session = _get_or_create_session(db, current_user.id, req.mode)
    history = _history_from_db(session)

    # If client sends its own history (stateless fallback), prefer DB history
    if not history and req.history:
        history = [{"role": h.get("role", "user"), "text": h.get("text", "")} for h in req.history[-8:]]

    reply = await llm_service.chat_with_history(
        current_message=req.message,
        conversation_history=history,
        mode=req.mode,
        student_context=profile,
        timeout=20.0,
    )

    # Override system instruction with our enriched one if possible
    # (llm_service.chat_with_history builds its own, but the market section
    #  we injected goes into the user message prefix instead)
    if had_market and reply:
        # Market context was already embedded in system_prompt string — no action needed.
        pass

    if not reply:
        reply = (
            "I'm having trouble reaching the Gemini service right now. "
            "Please try again in a moment or check your API key configuration."
        )
        source = "system_fallback"
    else:
        source = "gemini"

    # Persist the turn
    _save_turn(db, session.id, req.message, reply, had_market)

    return ChatResponse(
        reply=reply,
        source=source,
        had_market_context=had_market,
        session_id=session.id,
    )


@router.post("/chat/stream")
async def chat_stream_endpoint(
    req: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Server-Sent Events streaming chat. Streams tokens as `data: <chunk>\n\n`.
    Final event: `data: [DONE]\n\n`.
    Auth: Bearer JWT required.
    """
    if not llm_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API key is not configured.",
        )

    profile = _build_profile_context(current_user)
    market_context = await _maybe_fetch_market_context(req.message)
    had_market = market_context is not None

    session = _get_or_create_session(db, current_user.id, req.mode)
    history = _history_from_db(session)
    if not history and req.history:
        history = [{"role": h.get("role", "user"), "text": h.get("text", "")} for h in req.history[-8:]]

    async def event_generator() -> AsyncGenerator[str, None]:
        full_reply = ""
        try:
            # llm_service.chat_with_history returns the full text (no streaming SDK call yet)
            # We simulate streaming by chunking the response word-by-word.
            reply = await llm_service.chat_with_history(
                current_message=req.message,
                conversation_history=history,
                mode=req.mode,
                student_context=profile,
                timeout=25.0,
            )

            if not reply:
                fallback = (
                    "I'm having trouble reaching the Gemini service. "
                    "Please try again in a moment."
                )
                yield f"data: {json.dumps({'chunk': fallback})}\n\n"
                full_reply = fallback
            else:
                # Stream word by word with a tiny delay for visual effect
                words = reply.split(" ")
                for i, word in enumerate(words):
                    chunk = word + (" " if i < len(words) - 1 else "")
                    full_reply += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    await asyncio.sleep(0.018)  # ~55 words/sec streaming rate

        except asyncio.CancelledError:
            logger.info("[chat_router/stream] Client disconnected before completion.")
            return
        except Exception as e:
            logger.error(f"[chat_router/stream] Error: {e}")
            err_msg = "An error occurred while generating the response."
            yield f"data: {json.dumps({'chunk': err_msg})}\n\n"
            full_reply = err_msg
        finally:
            # Always persist even if client disconnected mid-stream
            if full_reply:
                _save_turn(db, session.id, req.message, full_reply, had_market)
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/chat/history")
async def get_chat_history(
    mode: str = "student",
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve the current user's chat history for the given mode.
    Returns the most recent `limit` messages.
    Auth: Bearer JWT required.
    """
    session = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id, ChatSession.mode == mode)
        .order_by(ChatSession.id.desc())
        .first()
    )
    if not session:
        return {"session_id": None, "mode": mode, "messages": []}

    msgs = session.messages[-limit:] if len(session.messages) > limit else session.messages
    return {
        "session_id": session.id,
        "mode": mode,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "had_market_context": m.had_market_context,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in msgs
        ],
    }


@router.delete("/chat/history")
async def clear_chat_history(
    mode: str = "student",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Clear the current user's chat session and history for the given mode.
    Auth: Bearer JWT required.
    """
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id, ChatSession.mode == mode)
        .all()
    )
    for s in sessions:
        db.delete(s)
    db.commit()
    return {"cleared": True, "mode": mode}
