"""
Roadmap Generation Agent
────────────────────────────────────────────────────────────────────────────
Responsibility: Generate a personalized, stage-by-stage career roadmap based
on the student's skill gap and selected career. Each stage includes skills,
topics, projects, resources, and an estimated duration.
"""
from __future__ import annotations
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# ─── Career Roadmap Templates ─────────────────────────────────────────────────
# Each key is a career title. Stages are ordered and can be filtered based
# on the student's skill gap (skipped if all stage skills are already Strong).

ROADMAP_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "Machine Learning Engineer": [
        {
            "stage_number": 1,
            "stage_title": "Programming Fundamentals",
            "description": "Build a solid foundation in Python programming.",
            "skills": ["Python", "Data Structures", "Algorithms"],
            "topics": ["Variables & Types", "Control Flow", "Functions", "OOP", "File I/O"],
            "projects": ["Calculator App", "Student Grade Manager", "Basic CLI Tool"],
            "resources": [
                {"name": "Python for Everybody (Coursera)", "url": "https://coursera.org/specializations/python", "type": "Course"},
                {"name": "Automate the Boring Stuff with Python", "url": "https://automatetheboringstuff.com", "type": "Book"},
            ],
            "estimated_duration": "4-6 weeks",
            "skill_keys": ["Python", "Data Structures"],
        },
        {
            "stage_number": 2,
            "stage_title": "Mathematics & Statistics for ML",
            "description": "Develop the mathematical foundation required for machine learning.",
            "skills": ["Statistics", "Linear Algebra", "Calculus", "Probability"],
            "topics": ["Descriptive Statistics", "Probability Distributions", "Matrix Operations", "Gradient Descent"],
            "projects": ["Statistical Analysis of a Dataset", "Linear Regression from Scratch"],
            "resources": [
                {"name": "Khan Academy - Statistics", "url": "https://khanacademy.org/math/statistics-probability", "type": "Course"},
                {"name": "3Blue1Brown - Linear Algebra", "url": "https://youtube.com/c/3blue1brown", "type": "Video"},
            ],
            "estimated_duration": "6-8 weeks",
            "skill_keys": ["Statistics", "Linear Algebra", "Calculus"],
        },
        {
            "stage_number": 3,
            "stage_title": "Data Analysis & Visualization",
            "description": "Learn to work with data using pandas and visualize insights.",
            "skills": ["NumPy", "Pandas", "Matplotlib", "SQL"],
            "topics": ["DataFrame Operations", "Data Cleaning", "Exploratory Data Analysis", "SQL Queries"],
            "projects": ["COVID-19 Data Analysis", "Sales Dashboard", "Customer Segmentation"],
            "resources": [
                {"name": "Pandas Documentation", "url": "https://pandas.pydata.org/docs", "type": "Documentation"},
                {"name": "Kaggle - Pandas Course", "url": "https://kaggle.com/learn/pandas", "type": "Course"},
            ],
            "estimated_duration": "4-5 weeks",
            "skill_keys": ["NumPy", "Pandas", "SQL"],
        },
        {
            "stage_number": 4,
            "stage_title": "Machine Learning Core",
            "description": "Master classical ML algorithms using Scikit-learn.",
            "skills": ["Machine Learning", "Scikit-learn", "Feature Engineering"],
            "topics": ["Supervised Learning", "Unsupervised Learning", "Model Evaluation", "Cross-Validation", "Hyperparameter Tuning"],
            "projects": ["House Price Prediction", "Spam Email Classifier", "Customer Churn Prediction"],
            "resources": [
                {"name": "Andrew Ng ML Course (Coursera)", "url": "https://coursera.org/learn/machine-learning", "type": "Course"},
                {"name": "Hands-On Machine Learning (O'Reilly)", "url": "https://oreilly.com/library/view/hands-on-machine-learning", "type": "Book"},
            ],
            "estimated_duration": "8-10 weeks",
            "skill_keys": ["Machine Learning"],
        },
        {
            "stage_number": 5,
            "stage_title": "Deep Learning",
            "description": "Explore neural networks and deep learning with TensorFlow/PyTorch.",
            "skills": ["Deep Learning", "TensorFlow", "Neural Networks", "CNN", "RNN"],
            "topics": ["Perceptrons", "Backpropagation", "CNN for Images", "RNN/LSTM for Sequences", "Transfer Learning"],
            "projects": ["Image Classifier (CNN)", "Sentiment Analysis (LSTM)", "Object Detection"],
            "resources": [
                {"name": "Deep Learning Specialization (Coursera)", "url": "https://coursera.org/specializations/deep-learning", "type": "Course"},
                {"name": "TensorFlow Official Tutorials", "url": "https://tensorflow.org/tutorials", "type": "Documentation"},
            ],
            "estimated_duration": "10-12 weeks",
            "skill_keys": ["Deep Learning", "TensorFlow"],
        },
        {
            "stage_number": 6,
            "stage_title": "Projects & Portfolio",
            "description": "Build end-to-end ML projects to demonstrate your skills.",
            "skills": ["Project Development", "GitHub", "Documentation"],
            "topics": ["ML Pipeline", "Model Deployment (Flask/FastAPI)", "Version Control", "Model Monitoring"],
            "projects": ["End-to-End ML Web App", "Kaggle Competition Entry", "GitHub Portfolio"],
            "resources": [
                {"name": "Made With ML", "url": "https://madewithml.com", "type": "Course"},
                {"name": "Full Stack Deep Learning", "url": "https://fullstackdeeplearning.com", "type": "Course"},
            ],
            "estimated_duration": "8-10 weeks",
            "skill_keys": ["GitHub", "Documentation"],
        },
        {
            "stage_number": 7,
            "stage_title": "Job Preparation",
            "description": "Prepare for ML Engineer interviews and job applications.",
            "skills": ["Interview Prep", "System Design", "Behavioral Skills"],
            "topics": ["ML Interview Questions", "Coding Rounds", "ML System Design", "Resume Building"],
            "projects": ["Mock Interviews", "LinkedIn Profile Optimization"],
            "resources": [
                {"name": "ML Interview Preparation", "url": "https://github.com/alexeygrigorev/mlbookcamp-code", "type": "Book"},
                {"name": "LeetCode - ML Track", "url": "https://leetcode.com", "type": "Platform"},
            ],
            "estimated_duration": "4-6 weeks",
            "skill_keys": ["Interview Prep"],
        },
    ],
    "Data Scientist": [
        {
            "stage_number": 1, "stage_title": "Python & Programming Basics",
            "description": "Foundation in Python and data structures.",
            "skills": ["Python", "Data Structures"], "topics": ["Python Basics", "OOP", "Data Structures"],
            "projects": ["Basic Data Analysis Script"], "estimated_duration": "4-6 weeks",
            "resources": [{"name": "Python for Data Science (Coursera)", "url": "https://coursera.org", "type": "Course"}],
            "skill_keys": ["Python"],
        },
        {
            "stage_number": 2, "stage_title": "Statistics & Probability",
            "description": "Core mathematics for data science.",
            "skills": ["Statistics", "Probability", "Linear Algebra"], "topics": ["Hypothesis Testing", "Distributions", "Regression"],
            "projects": ["A/B Testing Analysis"], "estimated_duration": "6-8 weeks",
            "resources": [{"name": "Statistics with Python (Coursera)", "url": "https://coursera.org", "type": "Course"}],
            "skill_keys": ["Statistics"],
        },
        {
            "stage_number": 3, "stage_title": "Data Wrangling & EDA",
            "description": "Data cleaning, exploration and visualization.",
            "skills": ["Pandas", "NumPy", "Matplotlib", "Seaborn", "SQL"], "topics": ["Data Cleaning", "EDA", "Visualization"],
            "projects": ["Exploratory Analysis on Real Dataset"], "estimated_duration": "5-6 weeks",
            "resources": [{"name": "Kaggle EDA Tutorials", "url": "https://kaggle.com/learn", "type": "Course"}],
            "skill_keys": ["Pandas", "SQL"],
        },
        {
            "stage_number": 4, "stage_title": "Machine Learning",
            "description": "Classical ML algorithms and model building.",
            "skills": ["Machine Learning", "Scikit-learn"], "topics": ["Classification", "Regression", "Clustering"],
            "projects": ["Prediction Model for Business Problem"], "estimated_duration": "8-10 weeks",
            "resources": [{"name": "ML Course - Andrew Ng", "url": "https://coursera.org", "type": "Course"}],
            "skill_keys": ["Machine Learning"],
        },
        {
            "stage_number": 5, "stage_title": "Advanced Analytics & Communication",
            "description": "Business communication of data insights.",
            "skills": ["Data Storytelling", "Tableau/Power BI", "Communication"], "topics": ["Dashboard Design", "Stakeholder Presentations"],
            "projects": ["Business Intelligence Dashboard"], "estimated_duration": "4-5 weeks",
            "resources": [{"name": "Tableau Public Tutorials", "url": "https://public.tableau.com", "type": "Platform"}],
            "skill_keys": [],
        },
        {
            "stage_number": 6, "stage_title": "Capstone & Job Preparation",
            "description": "Portfolio projects and interview preparation.",
            "skills": ["Portfolio Building", "Interview Skills"], "topics": ["Case Studies", "Mock Interviews", "Résumé"],
            "projects": ["Data Science Portfolio on GitHub"], "estimated_duration": "6-8 weeks",
            "resources": [{"name": "DS Interview Questions", "url": "https://datascienceinterviewprep.com", "type": "Book"}],
            "skill_keys": [],
        },
    ],
    "Software Engineer": [
        {
            "stage_number": 1, "stage_title": "Core Programming",
            "description": "Master a primary programming language (Python/Java/C++).",
            "skills": ["Python", "Java", "Data Structures", "Algorithms"],
            "topics": ["OOP", "Data Structures", "Sorting Algorithms", "Recursion"],
            "projects": ["CLI Applications", "Mini Games"],
            "resources": [{"name": "CS50 (Harvard)", "url": "https://cs50.harvard.edu", "type": "Course"}],
            "estimated_duration": "6-8 weeks", "skill_keys": ["Python", "Java"],
        },
        {
            "stage_number": 2, "stage_title": "Web Development Fundamentals",
            "description": "Build full-stack web applications.",
            "skills": ["HTML/CSS", "JavaScript", "React", "Node.js"],
            "topics": ["REST APIs", "Frontend Frameworks", "Backend Development"],
            "projects": ["Portfolio Website", "CRUD Web App"],
            "resources": [{"name": "The Odin Project", "url": "https://theodinproject.com", "type": "Course"}],
            "estimated_duration": "8-10 weeks", "skill_keys": ["JavaScript"],
        },
        {
            "stage_number": 3, "stage_title": "Databases & Backend",
            "description": "SQL, NoSQL, and API development.",
            "skills": ["SQL", "PostgreSQL", "MongoDB", "REST APIs"],
            "topics": ["Database Design", "ORM", "API Development", "Authentication"],
            "projects": ["REST API Backend", "Database-driven Web App"],
            "resources": [{"name": "FastAPI Documentation", "url": "https://fastapi.tiangolo.com", "type": "Documentation"}],
            "estimated_duration": "6-8 weeks", "skill_keys": ["SQL"],
        },
        {
            "stage_number": 4, "stage_title": "System Design & DevOps",
            "description": "Scalable systems and deployment.",
            "skills": ["Docker", "Git", "CI/CD", "System Design"],
            "topics": ["Microservices", "Docker", "Git Flow", "Load Balancing"],
            "projects": ["Containerized Deployment", "CI/CD Pipeline"],
            "resources": [{"name": "System Design Primer (GitHub)", "url": "https://github.com/donnemartin/system-design-primer", "type": "Book"}],
            "estimated_duration": "6-8 weeks", "skill_keys": ["Docker", "Git"],
        },
        {
            "stage_number": 5, "stage_title": "DSA & Interview Preparation",
            "description": "Competitive coding and technical interviews.",
            "skills": ["Problem Solving", "LeetCode", "System Design"],
            "topics": ["Trees", "Graphs", "Dynamic Programming", "Behavioral Questions"],
            "projects": ["LeetCode 100 Problems", "Mock System Design Interviews"],
            "resources": [{"name": "NeetCode", "url": "https://neetcode.io", "type": "Platform"}],
            "estimated_duration": "8-10 weeks", "skill_keys": [],
        },
    ],
}

# Default template for careers without specific templates
DEFAULT_STAGES = [
    {
        "stage_number": 1, "stage_title": "Foundation Skills",
        "description": "Build the fundamental skills required for this career.",
        "skills": [], "topics": ["Core Concepts", "Industry Overview", "Basic Tools"],
        "projects": ["Beginner Project"], "resources": [], "estimated_duration": "4-6 weeks", "skill_keys": [],
    },
    {
        "stage_number": 2, "stage_title": "Core Technical Skills",
        "description": "Master the primary technical competencies.",
        "skills": [], "topics": ["Advanced Concepts", "Practical Applications"],
        "projects": ["Intermediate Project"], "resources": [], "estimated_duration": "6-8 weeks", "skill_keys": [],
    },
    {
        "stage_number": 3, "stage_title": "Specialization",
        "description": "Deepen expertise in your chosen specialization area.",
        "skills": [], "topics": ["Specialized Knowledge", "Case Studies"],
        "projects": ["Capstone Project"], "resources": [], "estimated_duration": "8-10 weeks", "skill_keys": [],
    },
    {
        "stage_number": 4, "stage_title": "Portfolio & Internship",
        "description": "Build your professional portfolio and gain real-world experience.",
        "skills": ["Portfolio Building", "Networking"], "topics": ["Resume Writing", "LinkedIn", "GitHub"],
        "projects": ["Portfolio Website", "Open Source Contribution"], "resources": [], "estimated_duration": "4-6 weeks", "skill_keys": [],
    },
    {
        "stage_number": 5, "stage_title": "Job Preparation",
        "description": "Prepare for interviews and job applications.",
        "skills": ["Interview Skills", "Communication"], "topics": ["Mock Interviews", "Technical Tests"],
        "projects": ["Interview Practice"], "resources": [], "estimated_duration": "4 weeks", "skill_keys": [],
    },
]


from app.agents.base import CareerAgent


class RoadmapAgent(CareerAgent):
    """
    Agent ID: roadmap_agent
    Phase 4 Target: 12-24 month milestone roadmap with courses, certifications, internships.
    """

    agent_name: str = "RoadmapAgent"
    description: str = "Generates actionable 12-24 month learning and career progression roadmaps."
    AGENT_ID = "roadmap_agent"

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze career goal and skill gaps to plan milestone duration."""
        return {"status": "ready_for_phase_4", "career": data.get("career_title", "Unknown")}

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process roadmap stages."""
        return {"status": "skeleton_ready", "message": "Roadmap Agent ready for Phase 4 expansion."}

    def generate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final roadmap output."""
        return {"agent": self.agent_name, "status": "skeleton_ready", "result": data}

    def generate(self, career: Any, skill_gap: Dict[str, Any]) -> List[Dict[str, Any]]:
        template = ROADMAP_TEMPLATES.get(career.title)
        if template:
            stages = self._build_from_template(template, skill_gap)
        else:
            stages = self._build_generic(career, skill_gap)
        logger.info(f"[RoadmapAgent] Generated {len(stages)} stages for {career.title}")
        return stages

    def _build_from_template(
        self, template: List[Dict], skill_gap: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        missing_and_improve = {
            e["skill"].lower()
            for e in (skill_gap.get("skills_to_improve", []) + skill_gap.get("missing_skills", []))
        }

        result = []
        for stage in template:
            skill_keys = [s.lower() for s in stage.get("skill_keys", [])]
            # Always include the stage; mark which skills are still needed
            stage_copy = dict(stage)
            stage_copy.pop("skill_keys", None)
            # Highlight missing skills
            if skill_keys:
                stage_copy["_needs_attention"] = any(k in missing_and_improve for k in skill_keys)
            result.append(stage_copy)
        return result

    def _build_generic(self, career: Any, skill_gap: Dict[str, Any]) -> List[Dict[str, Any]]:
        stages = []
        missing_skills = [e["skill"] for e in skill_gap.get("missing_skills", [])]
        improve_skills = [e["skill"] for e in skill_gap.get("skills_to_improve", [])]

        for i, stage in enumerate(DEFAULT_STAGES):
            s = dict(stage)
            if i == 0 and improve_skills:
                s["skills"] = improve_skills[:3]
                s["description"] = f"Improve foundational skills: {', '.join(improve_skills[:3])}"
            elif i == 1 and missing_skills:
                s["skills"] = missing_skills[:4]
                s["description"] = f"Learn the core required skills: {', '.join(missing_skills[:4])}"
            elif i == 2 and len(missing_skills) > 4:
                s["skills"] = missing_skills[4:]
                s["description"] = f"Master advanced required skills: {', '.join(missing_skills[4:])}"
            s.pop("skill_keys", None)
            stages.append(s)
        return stages
