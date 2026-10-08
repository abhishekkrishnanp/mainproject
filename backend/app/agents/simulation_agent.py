"""
Career Simulation Agent
────────────────────────────────────────────────────────────────────────────
Responsibility: Generate a realistic 10-year simulated career growth path
for a student based on their selected career.

⚠️ DISCLAIMER: This simulation is an ESTIMATE based on industry trends and
sample data. Actual career progression may vary. This is NOT a guaranteed
prediction.
"""
from __future__ import annotations
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# ─── Career Simulation Templates (10 years) ───────────────────────────────────
SIMULATION_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "Machine Learning Engineer": [
        {"year": 1, "job_title": "Junior ML Engineer / Intern", "experience_level": "Fresher",
         "salary_min": 6.0, "salary_max": 12.0,
         "skills_acquired": ["Python", "Scikit-learn", "Data Preprocessing"],
         "responsibilities": ["Build basic ML models", "Data cleaning and EDA", "Work under senior guidance"],
         "promotion_note": "Focus on completing projects and earning certifications (TF Developer)."},
        {"year": 2, "job_title": "ML Engineer (Associate)", "experience_level": "Junior",
         "salary_min": 10.0, "salary_max": 18.0,
         "skills_acquired": ["TensorFlow", "Model Deployment", "MLflow"],
         "responsibilities": ["Design ML pipelines", "Model evaluation", "Collaborate with data teams"],
         "promotion_note": "Lead a small project. Build expertise in one domain (NLP/CV)."},
        {"year": 3, "job_title": "ML Engineer", "experience_level": "Mid-level",
         "salary_min": 16.0, "salary_max": 28.0,
         "skills_acquired": ["Deep Learning", "Cloud ML (AWS/GCP)", "A/B Testing"],
         "responsibilities": ["Own end-to-end ML features", "Mentor juniors", "Research new techniques"],
         "promotion_note": "Start contributing to architecture decisions."},
        {"year": 4, "job_title": "Senior ML Engineer", "experience_level": "Mid-Senior",
         "salary_min": 25.0, "salary_max": 40.0,
         "skills_acquired": ["MLOps", "Distributed Training", "Production ML Systems"],
         "responsibilities": ["Design scalable ML systems", "Tech lead for ML features", "Cross-team collaboration"],
         "promotion_note": "Consider specializing in LLMs, CV, or recommendation systems."},
        {"year": 5, "job_title": "Senior ML Engineer / Tech Lead", "experience_level": "Senior",
         "salary_min": 35.0, "salary_max": 55.0,
         "skills_acquired": ["System Design", "Team Leadership", "Research Paper Reading"],
         "responsibilities": ["Technical leadership", "Roadmap planning", "Interviewing candidates"],
         "promotion_note": "Apply for Staff/Principal Engineer or Management track."},
        {"year": 6, "job_title": "Staff ML Engineer / ML Architect", "experience_level": "Senior+",
         "salary_min": 45.0, "salary_max": 75.0,
         "skills_acquired": ["Org-wide ML Strategy", "Mentoring", "Open Source"],
         "responsibilities": ["Define ML best practices", "Cross-org technical decisions", "Represent ML at leadership"],
         "promotion_note": "Publish research or open source tools to build external credibility."},
        {"year": 7, "job_title": "Principal ML Engineer", "experience_level": "Principal",
         "salary_min": 60.0, "salary_max": 95.0,
         "skills_acquired": ["Product Strategy", "Business Acumen", "Executive Communication"],
         "responsibilities": ["Set technical direction", "Partner with product and business", "Hire senior talent"],
         "promotion_note": "Consider branching into VP Engineering or AI Director path."},
        {"year": 8, "job_title": "Principal / Distinguished Engineer", "experience_level": "Principal",
         "salary_min": 75.0, "salary_max": 120.0,
         "skills_acquired": ["Strategic Thinking", "AI Ethics", "Research Leadership"],
         "responsibilities": ["Drive org-wide AI strategy", "Board-level AI advisory", "Industry thought leadership"],
         "promotion_note": "Build a strong external brand (talks, publications, patents)."},
        {"year": 9, "job_title": "AI Director / Head of ML", "experience_level": "Director",
         "salary_min": 90.0, "salary_max": 150.0,
         "skills_acquired": ["P&L Management", "Team Building", "Market Analysis"],
         "responsibilities": ["Lead entire ML division", "Budget and hiring decisions", "Executive presentations"],
         "promotion_note": "You may consider founding an AI startup at this stage."},
        {"year": 10, "job_title": "VP of AI / CTO / AI Entrepreneur", "experience_level": "Executive",
         "salary_min": 120.0, "salary_max": 200.0,
         "skills_acquired": ["C-Suite Collaboration", "Fundraising (if startup)", "AI Policy"],
         "responsibilities": ["Organization-level AI vision", "Company strategy", "AI product portfolio ownership"],
         "promotion_note": "Peak of the individual contributor or management track. Entrepreneurship is a viable path."},
    ],
    "Data Scientist": [
        {"year": 1, "job_title": "Junior Data Scientist", "experience_level": "Fresher", "salary_min": 5.0, "salary_max": 10.0,
         "skills_acquired": ["Python", "Pandas", "EDA"], "responsibilities": ["Data cleaning", "Basic analysis", "Reporting"],
         "promotion_note": "Build your Kaggle profile. Earn a data science certification."},
        {"year": 2, "job_title": "Data Scientist", "experience_level": "Junior", "salary_min": 9.0, "salary_max": 16.0,
         "skills_acquired": ["ML Models", "Scikit-learn", "Tableau"], "responsibilities": ["Build predictive models", "A/B testing", "Dashboards"],
         "promotion_note": "Pick a domain specialization (Finance/Healthcare/E-commerce)."},
        {"year": 3, "job_title": "Data Scientist II", "experience_level": "Mid-level", "salary_min": 14.0, "salary_max": 25.0,
         "skills_acquired": ["Deep Learning", "Spark", "Cloud"], "responsibilities": ["Advanced modeling", "Team mentorship", "Business insights"],
         "promotion_note": "Lead a high-impact project from scratch."},
        {"year": 5, "job_title": "Senior Data Scientist", "experience_level": "Senior", "salary_min": 25.0, "salary_max": 45.0,
         "skills_acquired": ["MLOps", "Product Analytics", "Strategy"], "responsibilities": ["Drive data strategy", "Present to stakeholders", "Hire analysts"],
         "promotion_note": "Move toward Lead DS or Data Science Manager."},
        {"year": 7, "job_title": "Lead Data Scientist / Manager", "experience_level": "Lead", "salary_min": 40.0, "salary_max": 70.0,
         "skills_acquired": ["Team Management", "OKR Planning", "Exec Comm"], "responsibilities": ["Manage DS team", "Data-driven product decisions", "Cross-functional leadership"],
         "promotion_note": "Director or VP path opens at this stage."},
        {"year": 10, "job_title": "Chief Data Officer / VP Analytics", "experience_level": "Executive", "salary_min": 80.0, "salary_max": 160.0,
         "skills_acquired": ["Corporate Strategy", "Data Governance", "AI Ethics"], "responsibilities": ["Company-wide data strategy", "Oversee analytics divisions"],
         "promotion_note": "Executive leadership in data-driven organizations."},
    ],
    "Software Engineer": [
        {"year": 1, "job_title": "Junior Software Engineer", "experience_level": "Fresher", "salary_min": 4.0, "salary_max": 9.0,
         "skills_acquired": ["Core Programming", "Git", "Basic Web Dev"], "responsibilities": ["Bug fixes", "Feature development under guidance", "Code reviews"],
         "promotion_note": "Focus on communication and code quality."},
        {"year": 2, "job_title": "Software Engineer", "experience_level": "Junior", "salary_min": 8.0, "salary_max": 16.0,
         "skills_acquired": ["REST APIs", "Databases", "Testing"], "responsibilities": ["Independent feature delivery", "Unit testing", "Team collaboration"],
         "promotion_note": "Take ownership of a service or module."},
        {"year": 3, "job_title": "Software Engineer II", "experience_level": "Mid-level", "salary_min": 14.0, "salary_max": 24.0,
         "skills_acquired": ["System Design", "Cloud", "Microservices"], "responsibilities": ["Design features", "Mentor juniors", "Cross-team projects"],
         "promotion_note": "Lead the design of a major feature."},
        {"year": 5, "job_title": "Senior Software Engineer", "experience_level": "Senior", "salary_min": 22.0, "salary_max": 40.0,
         "skills_acquired": ["Architecture", "Performance Optimization", "DevOps"], "responsibilities": ["Technical decisions", "Architecture reviews", "Interviewing"],
         "promotion_note": "Choose: IC (Staff Eng) or Management track."},
        {"year": 7, "job_title": "Staff / Principal Engineer", "experience_level": "Staff", "salary_min": 40.0, "salary_max": 70.0,
         "skills_acquired": ["Org Strategy", "Tech Evangelism", "Open Source"], "responsibilities": ["Org-wide technical influence", "Major architectural initiatives"],
         "promotion_note": "VP Engineering or CTO path if management chosen."},
        {"year": 10, "job_title": "VP Engineering / CTO / Founder", "experience_level": "Executive", "salary_min": 80.0, "salary_max": 150.0,
         "skills_acquired": ["Leadership", "Business Strategy", "Product Vision"], "responsibilities": ["Engineering org leadership", "Tech vision", "Board reporting"],
         "promotion_note": "Many senior SWEs start their own companies at this stage."},
    ],
}

# Generic fallback template (year-by-year)
def _build_generic_simulation(career: Any) -> List[Dict]:
    base_min = career.salary_beginner or 5.0
    base_max = (career.salary_mid or base_min * 2.5)
    senior_min = career.salary_senior or base_min * 5
    levels = [
        (1, "Fresher / Intern", base_min, base_min * 1.5),
        (2, "Junior Professional", base_min * 1.4, base_min * 2.2),
        (3, "Mid-level Professional", base_min * 2.0, base_max),
        (4, "Mid-Senior", base_max * 1.1, base_max * 1.5),
        (5, "Senior", base_max * 1.5, base_max * 2.0),
        (6, "Senior+", base_max * 2.0, senior_min),
        (7, "Lead / Principal", senior_min, senior_min * 1.3),
        (8, "Principal", senior_min * 1.2, senior_min * 1.6),
        (9, "Director", senior_min * 1.5, senior_min * 2.0),
        (10, "Executive / VP", senior_min * 2.0, senior_min * 3.0),
    ]
    result = []
    for year, level, s_min, s_max in levels:
        result.append({
            "year": year,
            "job_title": f"{level} {career.title}",
            "experience_level": level,
            "salary_min": round(s_min, 1),
            "salary_max": round(s_max, 1),
            "skills_acquired": (career.required_skills or [])[:3],
            "responsibilities": ["Build expertise in core skills", "Work on live projects", "Team collaboration"],
            "promotion_note": f"Year {year} milestone: focus on skill depth and portfolio building.",
        })
    return result


class CareerSimulationAgent:
    """
    Agent ID: simulation_agent
    Input:  career ORM object
    Output: list of 10-year simulation dicts
    """

    AGENT_ID = "simulation_agent"

    DISCLAIMER = (
        "⚠️ This is an estimated career simulation based on industry trends and sample data. "
        "Actual career progression depends on individual performance, market conditions, company, "
        "location, and many other factors. This is NOT a guaranteed prediction."
    )

    def simulate(self, career: Any) -> List[Dict[str, Any]]:
        template = SIMULATION_TEMPLATES.get(career.title)
        if template:
            years = template
        else:
            years = _build_generic_simulation(career)

        # Fill missing years (some templates skip years)
        year_nums = {y["year"] for y in years}
        filled = list(years)
        for yr in range(1, 11):
            if yr not in year_nums:
                prev = max((y for y in filled if y["year"] < yr), key=lambda y: y["year"], default=filled[0])
                filled.append({**prev, "year": yr, "promotion_note": "Continue building on previous year's achievements."})
        filled.sort(key=lambda y: y["year"])
        logger.info(f"[SimulationAgent] Simulated {len(filled)} years for {career.title}")
        return filled
