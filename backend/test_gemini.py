"""
Unit test for Gemini LLM integration and fallback mechanisms.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.llm_service import llm_service

client = TestClient(app)


def test_gemini_status_endpoint():
    response = client.get("/api/v1/gemini/status")
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    assert "model" in data
    assert "sdk_installed" in data
    assert data["sdk_installed"] is True
    assert data["provider"] == "Google Gemini"
    # Ensure sensitive credentials are NOT leaked
    assert "api_key" not in data
    assert "key" not in data


def test_gemini_recommendations_endpoint():
    payload = {
        "interests": ["Machine Learning", "Web Development"],
        "skills": ["Python", "FastAPI", "SQL"],
        "education_level": "B.Tech Computer Science",
        "aspirations": "Become an AI Engineer"
    }
    response = client.post("/api/v1/gemini/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    rec = data["recommendations"][0]
    assert "title" in rec
    assert "match_score" in rec
    assert "why_recommended" in rec


def test_gemini_roadmap_endpoint():
    payload = {
        "target_career": "Cloud Solutions Architect",
        "current_skills": ["Linux", "Basic Python"],
        "timeline_months": 6
    }
    response = client.post("/api/v1/gemini/roadmap", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "milestones" in data
    assert len(data["milestones"]) > 0


def test_gemini_skill_gap_endpoint():
    payload = {
        "target_career": "Data Scientist",
        "student_skills": ["Python", "Pandas"]
    }
    response = client.post("/api/v1/gemini/skill-gap", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "missing_critical_skills" in data
    assert "priority_learning_order" in data


def test_gemini_qa_student_and_parent():
    # Student question
    student_payload = {
        "question": "What is the best way to prepare for tech placements in Kerala?",
        "role": "student",
        "education_level": "B.Tech Final Year"
    }
    resp_student = client.post("/api/v1/gemini/qa", json=student_payload)
    assert resp_student.status_code == 200
    assert "answer" in resp_student.json()

    # Parent question
    parent_payload = {
        "question": "Is Artificial Intelligence a secure and stable field for my daughter?",
        "role": "parent"
    }
    resp_parent = client.post("/api/v1/gemini/qa", json=parent_payload)
    assert resp_parent.status_code == 200
    assert "answer" in resp_parent.json()


def test_gemini_myth_buster():
    payload = {
        "career_or_topic": "Cybersecurity Specialist"
    }
    response = client.post("/api/v1/gemini/myth-buster", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "myths" in data
    assert len(data["myths"]) > 0


def test_assistant_chat_with_conversation_context():
    """
    Test that the chatbot accepts conversation history and responds meaningfully
    to follow-up questions.
    """
    history = [
        {"role": "user", "text": "I am a B.Tech AI student."},
        {"role": "assistant", "text": "What area of AI interests you most? E.g., machine learning, computer vision, NLP?"},
        {"role": "user", "text": "Machine learning and data science."},
        {"role": "assistant", "text": "Great choice. Machine Learning focuses on statistical algorithms and data modeling."}
    ]

    # Follow-up query referring to previous context ("that")
    payload = {
        "message": "What skills do I need for that?",
        "mode": "student",
        "education_level": "B.Tech AI",
        "history": history
    }

    response = client.post("/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 10
    assert data["mode"] == "student"


def test_assistant_chat_validation():
    """Verify input validation rejects empty or whitespace-only messages."""
    response = client.post("/assistant/chat", json={"message": "   "})
    assert response.status_code == 422 or response.status_code == 400
