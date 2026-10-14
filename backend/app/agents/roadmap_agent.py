"""
Roadmap Generation Agent
────────────────────────────────────────────────────────────────────────────
Responsibility:
Produce an actionable, personalized 12–24 month roadmap helping the user progress
from their current educational or career stage toward a selected career.

Adapts explicitly for:
- School students (stream choices, board preparation, KEAM/JEE/NEET/CUET, coding clubs)
- College & Postgraduate students (internships, capstone projects, GATE/certifications, GitHub portfolio)
- Working professionals (evening/weekend upskilling, bridge projects, lateral transitions)

Milestones include:
- Target outcome
- Concrete tasks
- Required skills or prerequisites
- Recommended resources (documentation, courses, books)
- Estimated duration
- Estimated cost (highlighting free & low-cost pathways)
- Measurable completion criterion
- Relevant projects or portfolio evidence
- Next milestone linkage
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import logging

from app.agents.base import CareerAgent

logger = logging.getLogger(__name__)


class RoadmapAgent(CareerAgent):
    """
    Agent 4: Career Roadmap Generator Agent
    Constructs multi-stage, 12-24 month milestone roadmaps tailored to user category and skill gaps.
    """

    agent_name: str = "RoadmapAgent"
    description: str = "Generates actionable 12-24 month milestone plans with measurable completion criteria."
    AGENT_ID = "roadmap_agent"

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "active", "career": data.get("career_title", "Unknown")}

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        career = data.get("career")
        skill_gap = data.get("skill_gap", {})
        profile = data.get("profile", {})
        return {
            "stages": self.generate(career, skill_gap, profile),
            "status": "completed",
        }

    def generate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.process(data)

    def generate(
        self,
        career: Any,
        skill_gap: Dict[str, Any],
        profile: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Builds tailored stages adapting for school students, college students, or working professionals.
        """
        profile = profile or {}
        edu_level = (profile.get("education_level") or "").lower()
        missing_skills = [e["skill"] if isinstance(e, dict) else str(e) for e in skill_gap.get("missing_skills", [])]
        improve_skills = [e["skill"] if isinstance(e, dict) else str(e) for e in skill_gap.get("skills_to_improve", [])]

        is_school = "school" in edu_level or "10th" in edu_level or "12th" in edu_level
        is_professional = "working" in edu_level or "professional" in edu_level

        if is_school:
            return self._build_school_student_roadmap(career, missing_skills, improve_skills)
        elif is_professional:
            return self._build_working_professional_roadmap(career, missing_skills, improve_skills)
        else:
            return self._build_college_student_roadmap(career, missing_skills, improve_skills)

    def _build_college_student_roadmap(
        self, career: Any, missing: List[str], improve: List[str]
    ) -> List[Dict[str, Any]]:
        title = career.title
        c_req = list(career.required_skills or ["Core Skills"])
        
        stages = [
            {
                "stage_number": 1,
                "stage_title": "Foundational Mastery & Environment Setup",
                "target_outcome": f"Solidify foundational problem solving and version control needed for {title}.",
                "description": f"Focus on core programming ({c_req[0] if c_req else 'Python'}), data structures, and Git workflow.",
                "skills": [c_req[0]] if c_req else ["Python", "Git"],
                "topics": ["Syntax & Idiomatic Coding", "Object-Oriented Design", "Data Structures", "Git & GitHub Workflow"],
                "projects": [f"{title} Foundations CLI App", "Data Processing Utilities"],
                "resources": [
                    {"name": "NPTEL / Coursera Core Computer Science", "url": "https://nptel.ac.in", "type": "Free Government Course"},
                    {"name": "Official Documentation & Language Guide", "url": "https://docs.python.org/3/", "type": "Documentation"}
                ],
                "estimated_duration": "4–6 weeks (10 hrs/week)",
                "estimated_cost": "Free (Open Courseware)",
                "completion_criterion": "Publish a clean, documented repository on GitHub with unit tests and clear README.",
                "suggested_next_milestone": "Stage 2: Core Domain Competencies",
            },
            {
                "stage_number": 2,
                "stage_title": "Core Technical Competencies & Tooling",
                "target_outcome": "Master the primary frameworks and mathematical/analytical foundations.",
                "description": f"Bridge identified skill gaps in {', '.join((missing + improve)[:3]) or 'specialized tooling'}.",
                "skills": (missing + improve)[:3] or c_req[1:3],
                "topics": ["Algorithms & Statistical Modeling", "Framework Architecture", "Database & Query Optimization"],
                "projects": [f"End-to-End {title} Prototype", "Database-driven Analytics Service"],
                "resources": [
                    {"name": "FastAPI & Scikit-learn Official Labs", "url": "https://scikit-learn.org", "type": "Hands-on Lab"},
                    {"name": "Kaggle Applied Micro-Courses", "url": "https://kaggle.com/learn", "type": "Interactive Platform"}
                ],
                "estimated_duration": "6–8 weeks (12 hrs/week)",
                "estimated_cost": "Free",
                "completion_criterion": "Deploy an interactive web API or dashboard accessible via public URL (HuggingFace Spaces / Render).",
                "suggested_next_milestone": "Stage 3: Advanced Pipeline & Cloud Integration",
            },
            {
                "stage_number": 3,
                "stage_title": "Production Deployment & Cloud Integration",
                "target_outcome": "Understand deployment, containerization, and industry reliability standards.",
                "description": "Containerize workflows with Docker, configure CI/CD pipelines, and connect cloud services.",
                "skills": ["Docker", "REST APIs", "Cloud Services", "CI/CD"],
                "topics": ["Containerization", "Automated Testing", "Cloud Deployment (AWS/GCP)", "Monitoring"],
                "projects": ["Containerized Production Microservice with GitHub Actions CI/CD"],
                "resources": [
                    {"name": "Docker & Cloud Native Computing Foundation Guides", "url": "https://docs.docker.com", "type": "Documentation"},
                    {"name": "AWS Skill Builder Free Tier", "url": "https://explore.skillbuilder.aws", "type": "Official Lab"}
                ],
                "estimated_duration": "5–7 weeks (10 hrs/week)",
                "estimated_cost": "₹0 – ₹500 (Free tier cloud accounts)",
                "completion_criterion": "Continuous integration build passing on GitHub with automated deployment.",
                "suggested_next_milestone": "Stage 4: Industry Capstone & Internship Outreach",
            },
            {
                "stage_number": 4,
                "stage_title": "Capstone Portfolio & Regional Placement Preparation",
                "target_outcome": "Establish proof of job readiness tailored to Kerala tech clusters and national recruiters.",
                "description": "Build an impressive capstone solving a regional or industry problem, polish resume, and practice interviews.",
                "skills": ["System Architecture", "Technical Communication", "Mock Coding Interviews"],
                "topics": ["System Design Basics", "Portfolio Curation", "Technical Interview Problem Solving", "Kerala Tech Ecosystem Networking"],
                "projects": [f"Flagship Capstone Project for {title} addressing a real-world dataset or problem"],
                "resources": [
                    {"name": "Kerala Startup Mission (KSUM) Placement Portal", "url": "https://startupmission.kerala.gov.in", "type": "Regional Hub"},
                    {"name": "NeetCode / LeetCode Interview Tracks", "url": "https://neetcode.io", "type": "Practice Platform"}
                ],
                "estimated_duration": "6–8 weeks (15 hrs/week)",
                "estimated_cost": "Free",
                "completion_criterion": "Portfolio reviewed with 3 complete showcase repositories and 5 applied internship applications.",
                "suggested_next_milestone": "Stage 5: Entry-Level Role Transition",
            },
            {
                "stage_number": 5,
                "stage_title": "Targeted Hiring & Industry Onboarding",
                "target_outcome": "Secure an entry-level position or industrial trainee role in Thiruvananthapuram, Kochi, or national tech hubs.",
                "description": "Engage with Technopark/Infopark campus hiring drives, off-campus referrals, and off-campus hackathons.",
                "skills": ["Professional Presentation", "Negotiation", "Workplace Execution"],
                "topics": ["Behavioral Interviews", "Technical Presentation", "First 90 Days Success Strategy"],
                "projects": ["Live Technical Presentation / Code Walkthrough"],
                "resources": [
                    {"name": "Technopark Careers Portal", "url": "https://technopark.org/careers", "type": "Job Board"},
                    {"name": "Infopark Kochi Opportunities", "url": "https://infopark.in/companies", "type": "Job Board"}
                ],
                "estimated_duration": "4–8 weeks",
                "estimated_cost": "Free",
                "completion_criterion": "Receive and evaluate offer letters or structured internship placements.",
                "suggested_next_milestone": "Ongoing Career Growth & Professional Networking",
            }
        ]
        return stages

    def _build_school_student_roadmap(
        self, career: Any, missing: List[str], improve: List[str]
    ) -> List[Dict[str, Any]]:
        title = career.title
        return [
            {
                "stage_number": 1,
                "stage_title": "Academic Foundation & Stream Alignment (Class 10–12)",
                "target_outcome": f"Ensure strong scholastic foundation in subjects critical for {title}.",
                "description": "Excel in Mathematics, Physics/Sciences, or Commerce according to required degree eligibility.",
                "skills": ["Analytical Reasoning", "Mathematics", "Basic Computer Logic"],
                "topics": ["Board Syllabus Mastery", "Conceptual Understanding", "Logic Building"],
                "projects": ["School Science / Math Exhibition Project or Simple Scratch/Python Script"],
                "resources": [
                    {"name": "DIKSHA / Kerala SCERT Digital Textbooks", "url": "https://diksha.gov.in", "type": "Government Portal"},
                    {"name": "Khan Academy Foundation Series", "url": "https://khanacademy.org", "type": "Free Education"}
                ],
                "estimated_duration": "Ongoing during academic terms",
                "estimated_cost": "Free",
                "completion_criterion": "Maintain strong board grades (>80%) in quantitative and scientific subjects.",
                "suggested_next_milestone": "Stage 2: Entrance Exam & Degree Selection",
            },
            {
                "stage_number": 2,
                "stage_title": "Entrance Examination Strategy (KEAM / JEE / CUET)",
                "target_outcome": "Prepare for college admissions in top Kerala and national institutes.",
                "description": "Systematic practice for engineering/science entrance examinations.",
                "skills": ["Time Management", "Speed & Accuracy", "Exam Problem Solving"],
                "topics": ["Entrance Syllabus", "Previous Years Question Papers (PYQs)", "Mock Tests"],
                "projects": ["Weekly Full-Length Entrance Mock Assessments"],
                "resources": [
                    {"name": "National Testing Agency (NTA) Mock Tests", "url": "https://nta.ac.in", "type": "Government Mock Engine"},
                    {"name": "CEE Kerala KEAM Guidance", "url": "https://cee.kerala.gov.in", "type": "Official Examination Portal"}
                ],
                "estimated_duration": "6–12 months",
                "estimated_cost": "Low (Government & self-study guides)",
                "completion_criterion": "Consistently score in qualifying percentiles in timed practice exams.",
                "suggested_next_milestone": "Stage 3: Undergraduate College Degree Enrollment",
            },
            {
                "stage_number": 3,
                "stage_title": "College Degree Enrollment & Early Coding Exploration",
                "target_outcome": f"Enroll in recommended degree ({career.required_degree}) and start practical coding.",
                "description": "Join college coding clubs, learn Python basics, and build first portfolio software.",
                "skills": ["Python", "Algorithms Basics", "Peer Collaboration"],
                "topics": ["Programming Fundamentals", "Campus Tech Chapters (IEEE/FOSS)"],
                "projects": ["First Independent GitHub Coding Project"],
                "resources": [
                    {"name": "CS50 Introduction to Computer Science (Harvard/edX)", "url": "https://cs50.harvard.edu", "type": "Free Elite Course"}
                ],
                "estimated_duration": "First Year of College (2–4 months)",
                "estimated_cost": "Free",
                "completion_criterion": "Complete CS50 or equivalent foundational programming series.",
                "suggested_next_milestone": "Transition into College Undergraduate Roadmap",
            }
        ]

    def _build_working_professional_roadmap(
        self, career: Any, missing: List[str], improve: List[str]
    ) -> List[Dict[str, Any]]:
        title = career.title
        return [
            {
                "stage_number": 1,
                "stage_title": "Transferable Skills Inventory & Evening Upskilling",
                "target_outcome": f"Map existing workplace experience to {title} requirements without leaving current job.",
                "description": "Dedicate 8–10 hours per week outside work hours to bridge critical prerequisites.",
                "skills": (missing[:2] or ["Target Domain Tools"]),
                "topics": ["Core Technical Bridge", "Modern Tooling", "Industry Vocabulary"],
                "projects": ["Mini-project automating a workflow in current domain using new tools"],
                "resources": [
                    {"name": "Self-Paced Specialization (Coursera / edX)", "url": "https://coursera.org", "type": "Flexible Course"},
                    {"name": "Documentation & Hands-on Quickstarts", "url": "https://github.com", "type": "Practical Labs"}
                ],
                "estimated_duration": "6–8 weeks (8 hrs/week)",
                "estimated_cost": "₹0 – ₹3,000 (Optional certification)",
                "completion_criterion": "Complete foundational hands-on certification or capstone module.",
                "suggested_next_milestone": "Stage 2: Domain Pivot Project",
            },
            {
                "stage_number": 2,
                "stage_title": "Domain Pivot Capstone & Proof of Execution",
                "target_outcome": "Build a substantial project demonstrating direct capability in the new domain.",
                "description": "Create a production-grade portfolio project that replaces lack of formal job title history.",
                "skills": ["End-to-End Implementation", "Deployment", "Architecture"],
                "topics": ["System Design", "Cloud Deployment", "Case Study Writing"],
                "projects": [f"Full-Stack / Applied Capstone for {title} solving a concrete business problem"],
                "resources": [
                    {"name": "Open-Source Community Contributions", "url": "https://github.com/explore", "type": "Practical Contribution"}
                ],
                "estimated_duration": "8–10 weeks (10 hrs/week)",
                "estimated_cost": "Free",
                "completion_criterion": "Publish a comprehensive LinkedIn article and GitHub project detailing problem, solution, and metrics.",
                "suggested_next_milestone": "Stage 3: Internal Transfer or Lateral Market Outreach",
            },
            {
                "stage_number": 3,
                "stage_title": "Internal Transfer or Targeted Career Pivot",
                "target_outcome": f"Transition into {title} via internal team lateral movement or targeted hiring.",
                "description": "First explore adjacent teams in current employer, then engage recruiters with modernized resume.",
                "skills": ["Strategic Networking", "Interview Narrative", "Salary Negotiation"],
                "topics": ["Framing Career Transition Story", "Technical Screen Mastery"],
                "projects": ["Interview Portfolio Deck"],
                "resources": [
                    {"name": "LinkedIn Career Transition Network", "url": "https://linkedin.com", "type": "Networking"}
                ],
                "estimated_duration": "8–12 weeks",
                "estimated_cost": "Free",
                "completion_criterion": "Secure role transition or external offer aligned with new career path.",
                "suggested_next_milestone": "Continuous Growth & Leadership Pathway",
            }
        ]


roadmap_agent = RoadmapAgent()
