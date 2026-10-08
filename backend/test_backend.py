"""
Automated Test Verification for 35% Milestone Backend
"""
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import engine, Base, SessionLocal
from app.models.career import Career
from app.models.user import User
from app.models.assessment import AssessmentResult
from app.services.career_service import seed_careers
from app.rag.vector_store import vector_store, RAGPipeline
from app.agents.coordinator import coordinator
from app.services.assessment_service import process_assessment

def run_tests():
    print("=== [1] Testing Database Initialization & Tables ===")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    print("[PASS] Tables created successfully.")

    print("\n=== [2] Testing Career Knowledge Base Seeding ===")
    seed_careers(db)
    careers = db.query(Career).all()
    print(f"[OK] Total careers in knowledge base: {len(careers)}")
    titles = [c.title for c in careers]
    print(f"[OK] Careers: {', '.join(titles[:6])}...")
    assert len(careers) >= 10, "Expected at least 10 careers in knowledge base"

    print("\n=== [3] Testing RAG Vector Store Indexing & Retrieval ===")
    vector_store.build_index(careers)
    print(f"[OK] Vector store indexed with {len(vector_store.documents)} documents.")
    search_results = vector_store.search("I want to build machine learning models with python", top_k=3)
    print(f"[OK] Top search result: {search_results[0]['career']['title']} (Score: {search_results[0]['score']})")
    assert "Machine Learning" in search_results[0]['career']['title'] or "Data" in search_results[0]['career']['title'] or "AI" in search_results[0]['career']['title']

    context = RAGPipeline.format_context(search_results)
    rag_answer = RAGPipeline.generate("What skills do I need for Machine Learning?", context, search_results)
    clean_rag = rag_answer[:120].encode('ascii', errors='ignore').decode('ascii')
    print(f"[OK] RAG Grounded Answer preview: {clean_rag}...")

    print("\n=== [4] Testing Student Profile Creation ===")
    test_email = "test.student@btech.edu"
    student = db.query(User).filter_by(email=test_email).first()
    if not student:
        student = User(
            email=test_email,
            hashed_password="mockhashedpassword",
            full_name="Arjun Sharma",
            age=21,
            education_level="B.Tech 3rd Year",
            course_degree="Artificial Intelligence & Data Science",
            college="National Institute of Technology",
            current_skills="Python, SQL, Mathematics",
            interests="Machine Learning, Data Analysis, Artificial Intelligence",
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    print(f"[OK] Student created: {student.full_name} (ID: {student.id})")

    print("\n=== [5] Testing Self-Assessment Agent ===")
    sample_answers = [
        {"question_key": "programming", "answer_value": 5, "category": "interest"},
        {"question_key": "mathematics", "answer_value": 5, "category": "interest"},
        {"question_key": "data_analysis", "answer_value": 4, "category": "interest"},
        {"question_key": "python", "answer_value": 4, "category": "skill"},
        {"question_key": "sql", "answer_value": 4, "category": "skill"},
        {"question_key": "statistics", "answer_value": 4, "category": "skill"},
        {"question_key": "research_oriented", "answer_value": 5, "category": "personality"},
        {"question_key": "high_salary", "answer_value": 5, "category": "goal"},
    ]
    assessment_res = process_assessment(db, student.id, sample_answers)
    print(f"[OK] Assessment processed. Primary Area: {assessment_res.interest_area}")
    print(f"[OK] Strong Skills: {assessment_res.strong_skills}")

    print("\n=== [6] Testing Career Recommendation Agent ===")
    from app.api.career import _generate_recommendations
    recs = _generate_recommendations(db, student.id, assessment_res)
    print(f"[OK] Generated {len(recs)} recommendations:")
    for r in recs[:5]:
        c = db.query(Career).filter_by(id=r.career_id).first()
        print(f"   - Rank {r.rank}: {c.title} (Match: {r.match_score}%) - Reason: {r.reasons[0] if r.reasons else ''}")

    print("\n=== [7] Testing Skill Gap Analysis Agent ===")
    top_career = db.query(Career).filter_by(id=recs[0].career_id).first()
    student_skills = assessment_res.skill_scores or {}
    gap = coordinator.run_skill_gap(student_skills, top_career)
    print(f"[OK] Career: {top_career.title}")
    print(f"[OK] Overall Readiness: {gap['overall_readiness']}%")
    print(f"[OK] Strong Skills: {[s['skill'] for s in gap['strong_skills']]}")
    print(f"[OK] Missing Skills: {[s['skill'] for s in gap['missing_skills']]}")

    print("\n=== [8] Testing Learning Roadmap Agent ===")
    roadmap_stages = coordinator.run_roadmap(top_career, gap)
    print(f"[OK] Generated {len(roadmap_stages)} personalized roadmap stages:")
    for stage in roadmap_stages:
        print(f"   Stage {stage.get('stage_number')}: {stage.get('stage_title')} ({stage.get('estimated_duration')})")
        print(f"     Skills to learn: {stage.get('skills', [])}")

    db.close()
    print("\n==========================================")
    print("ALL 35% MILESTONE BACKEND TESTS PASSED! [PASS]")
    print("==========================================")

if __name__ == "__main__":
    run_tests()
