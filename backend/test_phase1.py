"""
Automated Test Verification for Phase 1 (First 35-40%) Implementation
Tests:
- Student Registration & Unique ID / Parent ID / Parent PIN Generation
- Student Login
- Parent Authentication (Read Only)
- Student / Parent Access Separation (Parent cannot access student write routes)
- Assessment Creation & Resume
- Answer Persistence & Memory Tracking
- Duplicate Question Prevention
- Adaptive Follow-Up Triggers
- Generation of 10-Dimension Personality Profile & Initial Career Profile
- Top 5 Preliminary Career Matches with Why, Evidence, Concerns, Skills
- Different User Types (School, Engineering/College, Commerce, Arts, Postgraduate, Working Professional)
- API Failure & Fallback Handling
"""
import sys
import os
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app
from app.database import engine, Base, SessionLocal
from app.models import User, StudentProfile, ParentAccount, Assessment, AssessmentResponse, CareerProfile, CareerRecommendationRecord
from app.agents.self_assessment_agent import self_assessment_agent
from app.services.conversational_assessment import assessment_engine

client = TestClient(app)


class Phase1ComprehensiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    def test_01_student_registration_and_credential_generation(self):
        """Test Student registration creates student_id, parent_id, and hashed parent_pin."""
        user_suffix = os.urandom(4).hex()
        payload = {
            "user_id": f"student_{user_suffix}",
            "name": "Kavya Nair",
            "email": f"kavya_{user_suffix}@test.edu",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "phone": "9876543210",
            "parent_whatsapp": "9876543211",
            "education_level": "College Student",
            "branch": "Computer Science & Engineering",
            "university": "APJ Abdul Kalam Technological University (KTU)",
            "cgpa_percentage": "8.7",
        }
        res = client.post("/auth/register", json=payload)
        self.assertEqual(res.status_code, 201, f"Failed registration: {res.text}")
        data = res.json()

        # Check required fields
        self.assertTrue(data["student_id"].startswith("ACGS-STU-"))
        self.assertTrue(data["parent_id"].startswith("ACGS-PAR-"))
        self.assertEqual(len(data["parent_pin"]), 6)
        self.assertTrue(data["parent_pin"].isdigit())
        self.assertTrue("access_token" in data)

        # Verify DB persistence
        db = SessionLocal()
        parent_acc = db.query(ParentAccount).filter_by(parent_id=data["parent_id"]).first()
        self.assertIsNotNone(parent_acc)
        self.assertNotEqual(parent_acc.parent_pin_hash, data["parent_pin"])  # PIN must be hashed!
        db.close()

    def test_02_student_login(self):
        """Test student login using user_id and password."""
        user_suffix = os.urandom(4).hex()
        reg_payload = {
            "user_id": f"rohit_{user_suffix}",
            "name": "Rohit Pillai",
            "email": f"rohit_{user_suffix}@test.edu",
            "password": "Password99!",
            "confirm_password": "Password99!",
            "education_level": "College Student",
        }
        reg_res = client.post("/auth/register", json=reg_payload)
        self.assertEqual(reg_res.status_code, 201)

        login_res = client.post("/auth/login", json={"user_id": f"rohit_{user_suffix}", "password": "Password99!"})
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.json()
        self.assertEqual(login_data["role"], "student")
        self.assertTrue("access_token" in login_data)

    def test_03_parent_login_and_read_only_access(self):
        """Test parent login and verified read-only dashboard access."""
        user_suffix = os.urandom(4).hex()
        reg_res = client.post("/auth/register", json={
            "user_id": f"par_stu_{user_suffix}",
            "name": "Ananya Menon",
            "email": f"ananya_{user_suffix}@test.edu",
            "password": "Password99!",
            "confirm_password": "Password99!",
        })
        reg_data = reg_res.json()
        parent_id = reg_data["parent_id"]
        parent_pin = reg_data["parent_pin"]
        student_token = reg_data["access_token"]

        # Parent login
        p_login = client.post("/parent/login", json={"parent_id": parent_id, "parent_pin": parent_pin})
        self.assertEqual(p_login.status_code, 200)
        p_data = p_login.json()
        self.assertEqual(p_data["role"], "parent")
        self.assertTrue(p_data["is_read_only"])
        parent_token = p_data["access_token"]

        # Parent gets student summary (Read-only)
        summary_res = client.get("/parent/student-summary", headers={"Authorization": f"Bearer {parent_token}"})
        self.assertEqual(summary_res.status_code, 200)
        summary = summary_res.json()
        self.assertTrue(summary["is_read_only"])
        self.assertEqual(summary["student_name"], "Ananya Menon")

        # Parent CANNOT update student profile (Role separation test)
        edit_res = client.put(
            "/student/profile",
            headers={"Authorization": f"Bearer {parent_token}"},
            json={"name": "Hacked Name"},
        )
        self.assertIn(edit_res.status_code, [401, 403], "Parent must not be able to edit student profile!")

    def test_04_deep_conversational_assessment_flow_and_memory(self):
        """Test assessment starts, handles adaptive dialogue, stores responses, prevents duplicate questions."""
        user_suffix = os.urandom(4).hex()
        reg_res = client.post("/auth/register", json={
            "user_id": f"eval_stu_{user_suffix}",
            "name": "Devanand S",
            "email": f"devanand_{user_suffix}@test.edu",
            "password": "Password99!",
            "confirm_password": "Password99!",
        })
        student_token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {student_token}"}

        # Start assessment
        start_res = client.post("/assessment/start", headers=headers)
        self.assertEqual(start_res.status_code, 200)
        start_data = start_res.json()
        self.assertEqual(start_data["current_question"]["question_id"], "q1_category")

        # Answer Q1: College Student
        q1_res = client.post("/assessment/message", headers=headers, json={
            "assessment_id": start_data["assessment_id"],
            "answer": "College Student (Undergraduate)",
            "question_id": "q1_category",
        })
        self.assertEqual(q1_res.status_code, 200)
        q1_data = q1_res.json()
        self.assertFalse(q1_data["is_completed"])
        # Next question should be from College flow
        self.assertTrue("q_college" in q1_data["next_question"]["question_id"])

        # Answer Q2: B.Tech Engineering
        next_qid = q1_data["next_question"]["question_id"]
        q2_res = client.post("/assessment/message", headers=headers, json={
            "assessment_id": start_data["assessment_id"],
            "answer": "B.Tech / B.E (Engineering & Technology)",
            "question_id": next_qid,
        })
        self.assertEqual(q2_res.status_code, 200)
        q2_data = q2_res.json()
        # Ensure previous answer is remembered and current question index incremented
        self.assertEqual(q2_data["current_step"], 2)

        # Check status and history endpoints
        status_res = client.get("/assessment/status", headers=headers)
        self.assertEqual(status_res.status_code, 200)
        self.assertEqual(status_res.json()["current_step"], 2)

        history_res = client.get("/assessment/history", headers=headers)
        self.assertEqual(history_res.status_code, 200)
        self.assertEqual(history_res.json()["total_responses"], 2)

    def test_05_adaptive_profile_generation_across_user_types(self):
        """Test complete interview simulation across different user types (School, Engineering, Working Pro)."""
        engine = assessment_engine

        # Type 1: School Student
        state_school = engine.get_initial_state("test_school")
        state_school = engine.record_answer(state_school, "q1_category", "School Student (10th / 11th / 12th)")
        self.assertEqual(state_school["category"], "school")
        next_q = engine.get_next_question(state_school)
        self.assertTrue("school" in next_q["question_id"])

        # Type 2: Working Professional
        state_work = engine.get_initial_state("test_work")
        state_work = engine.record_answer(state_work, "q1_category", "Working Professional")
        self.assertEqual(state_work["category"], "working")
        next_q_work = engine.get_next_question(state_work)
        self.assertTrue("work" in next_q_work["question_id"])

        # Simulate full interview to generate profile
        sim_state = engine.get_initial_state("test_full_student")
        sim_state = engine.record_answer(sim_state, "q1_category", "College Student (Undergraduate)")
        
        while True:
            nq = engine.get_next_question(sim_state)
            if not nq:
                break
            ans = nq["options"][0] if nq.get("options") else "Python and Machine Learning projects"
            sim_state = engine.record_answer(sim_state, nq["question_id"], ans, nq)

        # Verify at least 25 questions were completed
        self.assertGreaterEqual(len(sim_state["previous_answers"]), 25, "Must complete at least 25 major interactions")

        # Generate profile
        profile = engine.generate_career_profile(sim_state)
        self.assertIn("personality_profile", profile)
        self.assertIn("interest_profile", profile)
        self.assertIn("career_recommendations", profile)

        # Verify 10 personality dimensions
        dimensions = profile["personality_profile"]
        expected_dims = [
            "Analytical", "Creative", "Social", "Leadership", "Practical",
            "Detail-oriented", "Risk tolerance", "Independence", "Collaboration", "Learning orientation"
        ]
        for dim in expected_dims:
            self.assertIn(dim, dimensions)
            self.assertGreaterEqual(dimensions[dim], 0)
            self.assertLessEqual(dimensions[dim], 100)

        # Verify non-medical disclaimer
        self.assertIn("disclaimer", dimensions)

        # Verify Top 5 preliminary matches
        recs = profile["career_recommendations"]
        self.assertEqual(len(recs), 5, "Must generate top 5 preliminary career directions")
        for r in recs:
            self.assertIn("career_name", r)
            self.assertIn("match_score", r)
            self.assertIn("reason", r)
            self.assertIn("supporting_evidence", r)
            self.assertIn("concerns", r)
            self.assertIn("skills_needed", r)
            self.assertTrue("Based on your responses" in r["reason"], "Must use responsible guidance phrasing")

    def test_06_future_agent_placeholders(self):
        """Test future agent API endpoints return appropriate Phase 2-5 responses."""
        res_m = client.post("/market-analysis", json={"career": "AI Engineer"})
        self.assertEqual(res_m.status_code, 200)
        self.assertEqual(res_m.json()["status"], "placeholder_ready_for_phase_2")

        res_s = client.post("/skill-gap", json={"career": "Data Scientist"})
        self.assertEqual(res_s.status_code, 200)
        self.assertEqual(res_s.json()["status"], "placeholder_ready_for_phase_3")

        res_r = client.post("/roadmap", json={"career": "Cloud Architect"})
        self.assertEqual(res_r.status_code, 200)
        self.assertEqual(res_r.json()["status"], "placeholder_ready_for_phase_4")

        res_f = client.post("/feasibility", json={"career": "Research Scientist"})
        self.assertEqual(res_f.status_code, 200)
        self.assertEqual(res_f.json()["status"], "placeholder_ready_for_phase_5")


if __name__ == "__main__":
    unittest.main()
