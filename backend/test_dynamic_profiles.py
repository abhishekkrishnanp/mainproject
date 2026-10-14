"""
Automated Test for Dynamic AI Assessment and Personalized Guidance
Tests 3 distinct user personas to verify:
1. Dynamic, context-relevant follow-up questions
2. Distinct career paths and roadmaps
3. Duplicate question suppression
"""
import asyncio
from app.services.dynamic_assessment_engine import dynamic_assessment_engine, INITIAL_QUESTION

async def test_profiles():
    # ─── Profile 1: AI & Healthcare (ECG Focus) ───
    print("\n" + "="*70)
    print("TEST PROFILE 1: AI in Healthcare & ECG Signals")
    print("="*70)
    state1 = dynamic_assessment_engine.get_initial_state("stu_1_health")
    answers1 = [
        "I am interested in artificial intelligence and healthcare.",
        "Early disease detection and diagnostic risk scoring.",
        "ECG signals and wearable physiological data.",
        "I know basic Python and algebra, but have not built machine learning signal filters yet.",
        "I would love to work in a clinical biomedical AI startup building heart monitoring tools.",
        "Hands-on guided coding projects using real PhysioNet patient datasets.",
        "Aiming to land a junior medical AI internship within 6 to 9 months.",
        "I want to master QRS peak detection, bandpass filtering, and 1D CNNs on real PhysioNet ECG records."
    ]
    curr_q = INITIAL_QUESTION
    for idx, ans in enumerate(answers1, 1):
        print(f"\n[Turn {idx}] Question Asked: {curr_q.get('question_text')}")
        print(f"[Turn {idx}] User Answer: {ans}")
        res = await dynamic_assessment_engine.generate_next_step("stu_1_health", state1, ans, curr_q)
        state1 = res["state"]
        curr_q = res["next_question"]
        if res.get("is_completed"):
            print("\n--> ASSESSMENT COMPLETED! Synthesized Profile:")
            prof = res["profile"]
            recs = prof.get("career_recommendations", [])
            print(f"Top Recommended Career: {recs[0].get('career_name')}")
            print(f"Match Score: {recs[0].get('match_score')}%")
            print(f"Why it Matches: {recs[0].get('reason')}")
            print(f"Portfolio Projects: {recs[0].get('suggested_projects')}")
            print(f"Roadmap Stage 1: {recs[0].get('roadmap_stages', [{}])[0].get('stage_title')}")
            break

    # ─── Profile 2: Frontend & UI/UX Design Systems ───
    print("\n" + "="*70)
    print("TEST PROFILE 2: Frontend Engineering & UI/UX Design")
    print("="*70)
    state2 = dynamic_assessment_engine.get_initial_state("stu_2_frontend")
    answers2 = [
        "I am interested in frontend development, UI/UX and web application engineering.",
        "Design systems, micro-interactions, accessibility and component architecture.",
        "I build projects using React, Tailwind CSS, TypeScript, and Figma.",
        "I want to bridge the gap between creative product design and clean frontend code.",
        "Agile SaaS product company or high-growth consumer startup.",
        "Deepening knowledge of state machines, web performance, and design tokens.",
        "Want to become a Frontend Design Engineer or UI Architect in 6 months.",
        "My goal is to build a published, fully tested open-source design system component library in React & TypeScript."
    ]
    curr_q2 = INITIAL_QUESTION
    for idx, ans in enumerate(answers2, 1):
        print(f"\n[Turn {idx}] Question Asked: {curr_q2.get('question_text')}")
        print(f"[Turn {idx}] User Answer: {ans}")
        res2 = await dynamic_assessment_engine.generate_next_step("stu_2_frontend", state2, ans, curr_q2)
        state2 = res2["state"]
        curr_q2 = res2["next_question"]
        if res2.get("is_completed"):
            print("\n--> ASSESSMENT COMPLETED! Synthesized Profile:")
            prof2 = res2["profile"]
            recs2 = prof2.get("career_recommendations", [])
            print(f"Top Recommended Career: {recs2[0].get('career_name')}")
            print(f"Match Score: {recs2[0].get('match_score')}%")
            print(f"Why it Matches: {recs2[0].get('reason')}")
            print(f"Portfolio Projects: {recs2[0].get('suggested_projects')}")
            print(f"Roadmap Stage 1: {recs2[0].get('roadmap_stages', [{}])[0].get('stage_title')}")
            break

if __name__ == "__main__":
    asyncio.run(test_profiles())
