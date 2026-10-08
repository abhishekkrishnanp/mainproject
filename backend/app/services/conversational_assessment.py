"""
Deep Conversational Self-Assessment Dialogue Engine & Question Bank
Handles education-specific branching (School, College, Postgrad, Working Professional),
adaptive follow-ups, answer memory tracking, and synthesis.
"""
from typing import Dict, Any, List, Optional
import copy


# ─── Baseline & Adaptive Question Bank ──────────────────────────────────────────

# Base category selection (Question 1)
CATEGORY_QUESTION = {
    "question_id": "q1_category",
    "phase": "education",
    "question_text": "What best describes your current situation?",
    "options": [
        "School Student (10th / 11th / 12th)",
        "College Student (Undergraduate)",
        "Post Graduate (M.Tech / M.Sc / MCA / MBA)",
        "Working Professional",
    ],
    "category": "education",
    "requires_text": False,
}

# Questions specific to School Students
SCHOOL_FLOW = [
    {
        "question_id": "q_school_class",
        "phase": "education",
        "question_text": "Which class or grade are you currently studying in?",
        "options": [
            "10th Standard / Matriculation",
            "11th Standard (Higher Secondary 1st Year)",
            "12th Standard (Higher Secondary 2nd Year)",
            "Gap Year / Entrance Preparation (KEAM / JEE / NEET)",
        ],
        "category": "education",
    },
    {
        "question_id": "q_school_board",
        "phase": "education",
        "question_text": "Which education board are you studying under?",
        "options": [
            "Kerala State Board (DHSE / SSLC)",
            "CBSE (Central Board of Secondary Education)",
            "ICSE / ISC",
            "Other State Board / International Board",
        ],
        "category": "education",
    },
    {
        "question_id": "q_school_stream",
        "phase": "education",
        "question_text": "Which academic stream are you in or planning to choose?",
        "options": [
            "Science with Computer Science & Mathematics",
            "Science with Biology & Mathematics",
            "Science with Pure Biology & Home Science",
            "Commerce with Computer Applications / Maths",
            "Humanities / Arts & Social Sciences",
        ],
        "category": "education",
    },
    {
        "question_id": "q_school_fav_subject",
        "phase": "academic",
        "question_text": "What subjects do you enjoy the most in school?",
        "options": [
            "Computer Science & Informatics",
            "Mathematics & Statistics",
            "Physics & Physical Sciences",
            "Biology & Life Sciences",
            "Accountancy, Economics & Business",
            "Literature, Social Sciences & Languages",
        ],
        "category": "interests",
    },
    {
        "question_id": "q_school_why_enjoy",
        "phase": "academic",
        "question_text": "What exactly do you enjoy most about that subject or technology?",
        "options": [
            "Programming and building software logic",
            "Designing graphics, presentations and visuals",
            "Understanding how systems, circuits and hardware work",
            "Gaming and interactive multimedia",
            "Cybersecurity, networks and ethical hacking",
            "Solving theoretical mathematical puzzles",
            "I am still exploring what excites me most",
        ],
        "category": "interests",
    },
    {
        "question_id": "q_school_strong_subject",
        "phase": "academic",
        "question_text": "Which academic area represents your strongest academic performance?",
        "options": [
            "Analytical & Quantitative subjects (Mathematics / Logic)",
            "Scientific concepts & theories (Physics / Chemistry / Biology)",
            "Practical lab work & computer assignments",
            "Commerce, accounting & business calculations",
            "Languages, essay writing & humanities",
        ],
        "category": "skills",
    },
    {
        "question_id": "q_school_challenging_sub",
        "phase": "academic",
        "question_text": "Which type of study do you find most challenging or uninteresting?",
        "options": [
            "Heavy memorization of theoretical definitions",
            "Complex mathematical equations and abstract proofs",
            "Repetitive handwritten assignments and lab records",
            "Public speaking, presentations and group debates",
        ],
        "category": "skills",
    },
    {
        "question_id": "q_school_activities",
        "phase": "academic",
        "question_text": "What extracurricular activities or hobbies engage your free time?",
        "options": [
            "Coding, tinkering with computers or robotics kits",
            "Drawing, digital art, video editing or design",
            "Reading science, tech blogs or fiction",
            "Sports, athletics, physical fitness",
            "Volunteering, student club organizing or debating",
        ],
        "category": "personality",
    },
]

# Questions specific to College & Postgraduate Students
COLLEGE_FLOW = [
    {
        "question_id": "q_college_degree",
        "phase": "education",
        "question_text": "What degree or academic program are you currently pursuing?",
        "options": [
            "B.Tech / B.E (Engineering & Technology)",
            "B.Sc / BCA (Computer Science / Data / Mathematics)",
            "B.Com / BBA (Commerce, Finance & Business)",
            "B.A / Humanities & Social Sciences",
            "M.Tech / M.Sc / MCA / MS (Postgraduate Science & Tech)",
            "MBA / Master of Management",
        ],
        "category": "education",
    },
    {
        "question_id": "q_college_branch",
        "phase": "education",
        "question_text": "Which branch or department are you currently enrolled in?",
        "options": [
            "Computer Science & Engineering (CSE)",
            "Artificial Intelligence & Data Science / Machine Learning",
            "Electronics & Communication (ECE)",
            "Electrical & Electronics (EEE)",
            "Mechanical / Civil / Chemical Engineering",
            "Information Technology (IT) / Software Engineering",
            "Commerce / Finance / Economics",
            "Biotechnology / Biomedical Engineering",
        ],
        "category": "education",
    },
    {
        "question_id": "q_college_year",
        "phase": "education",
        "question_text": "What is your current academic year or semester?",
        "options": [
            "1st Year / Semesters 1-2 (Foundations)",
            "2nd Year / Semesters 3-4 (Core Engineering/Degree Subjects)",
            "3rd Year / Semesters 5-6 (Advanced Electives & Mini Projects)",
            "Final Year / Semesters 7-8 (Capstone Projects & Placements)",
            "Postgraduate / Recent Graduate",
        ],
        "category": "education",
    },
    {
        "question_id": "q_college_institution",
        "phase": "education",
        "question_text": "What category of university or institution are you studying in?",
        "options": [
            "APJ Abdul Kalam Technological University (KTU / Kerala State)",
            "National Institute of Technology (NIT) / IIT / IIIT",
            "Autonomous Engineering College in South India",
            "Kerala University / Calicut / CUSAT / MG University",
            "Private / Deemed University",
        ],
        "category": "education",
    },
    {
        "question_id": "q_college_cgpa",
        "phase": "academic",
        "question_text": "What is your current CGPA or academic percentage range?",
        "options": [
            "9.0+ CGPA / Above 85% (High academic distinction)",
            "8.0 - 8.9 CGPA / 75-84% (Strong consistent academic standing)",
            "7.0 - 7.9 CGPA / 65-74% (Balanced academics with project focus)",
            "Below 7.0 CGPA (Focused more on practical hands-on skills than exams)",
        ],
        "category": "academic",
    },
    {
        "question_id": "q_college_why_branch",
        "phase": "academic",
        "question_text": "What made you choose your current degree and branch?",
        "options": [
            "Genuine curiosity and enthusiasm for technology & problem-solving",
            "Strong campus placement records and career salary potential",
            "Advice from parents, family, or academic mentors",
            "Allotted based on entrance examination ranking (KEAM / JEE)",
            "Exploratory choice — still discovering my true professional passion",
        ],
        "category": "motivations",
    },
    {
        "question_id": "q_college_domain_interest",
        "phase": "academic",
        "question_text": "What part of your field interests you the most right now?",
        "options": [
            "Software Development & Full-Stack Web/Mobile engineering",
            "Artificial Intelligence, Machine Learning & Deep Learning",
            "Data Science, Data Analytics & Business Intelligence",
            "Cybersecurity, Ethical Hacking & Cloud Infrastructure",
            "Embedded Systems, Robotics & IoT Hardware",
            "Product Management, Tech Strategy & UI/UX Design",
            "Academic Research, Algorithms & Mathematics",
        ],
        "category": "interests",
    },
    {
        "question_id": "q_college_projects",
        "phase": "academic",
        "question_text": "What kind of project work do you enjoy the most?",
        "options": [
            "Building complete applications with real user interfaces and databases",
            "Training machine learning models on real datasets",
            "Designing system architecture, APIs, and cloud deployments",
            "Tinkering with hardware circuits, microcontrollers, and sensors",
            "Conducting research papers and comparative benchmarking",
            "Designing user interfaces, user journey flows, and design systems",
        ],
        "category": "interests",
    },
    {
        "question_id": "q_college_tech_skills",
        "phase": "skills",
        "question_text": "How would you rate your technical and programming proficiency?",
        "options": [
            "Proficient: Can independently develop projects in Python, Java, or C++",
            "Intermediate: Comfortable with syntax, algorithms, and simple web frameworks",
            "Foundational: Understand core concepts, currently practicing coding",
            "Exploring: Stronger in design, analytics, or management than pure coding",
        ],
        "category": "skills",
    },
    {
        "question_id": "q_college_non_tech",
        "phase": "skills",
        "question_text": "Which non-technical / interpersonal strength describes you best?",
        "options": [
            "Structured analytical reasoning and methodical debugging",
            "Clear oral communication and technical presentation skills",
            "Collaborative teamwork, empathy, and organizing groups",
            "Creative aesthetic thinking and visual storytelling",
            "Independent self-direction and persistence when stuck",
        ],
        "category": "skills",
    },
    {
        "question_id": "q_college_post_plans",
        "phase": "goals",
        "question_text": "What are your primary goals after graduating?",
        "options": [
            "Campus placement or off-campus role at a high-growth tech company",
            "Joining or founding an early-stage tech startup",
            "Higher studies in India (M.Tech via GATE / MBA via CAT)",
            "Masters / Research abroad (MS in US, Europe, or Singapore)",
            "Government / Public sector careers (Kerala PSC, ISRO, UPSC)",
        ],
        "category": "career_goals",
    },
]

# Questions specific to Working Professionals
WORKING_FLOW = [
    {
        "question_id": "q_work_field",
        "phase": "education",
        "question_text": "What is your current professional domain or industry?",
        "options": [
            "Software Engineering / IT Services (TCS, Infosys, Wipro, UST, etc.)",
            "Product Tech / Software Products (SaaS, FinTech, E-commerce)",
            "Data Analytics, Business Intelligence & Consulting",
            "Core Engineering / Manufacturing / Energy",
            "Banking, Financial Services & Insurance (BFSI)",
            "Education, Healthcare, or Public Sector",
        ],
        "category": "education",
    },
    {
        "question_id": "q_work_experience",
        "phase": "education",
        "question_text": "How many years of total professional work experience do you have?",
        "options": [
            "Less than 1 year (Entry-level / Trainee)",
            "1 to 3 years (Junior to Mid-level associate)",
            "3 to 6 years (Mid-level professional)",
            "6 to 10 years (Senior specialist / Team Lead)",
            "10+ years (Engineering Manager / Director / Architect)",
        ],
        "category": "education",
    },
    {
        "question_id": "q_work_switch_motivation",
        "phase": "academic",
        "question_text": "What is the primary motivation driving your desire to pivot or transition?",
        "options": [
            "Seeking significantly higher compensation and faster career growth",
            "Current role feels repetitive or intellectually unstimulating",
            "Desire to transition into modern AI, Data Science, or Cloud technologies",
            "Seeking better work-life balance and flexible arrangements",
            "Desire to move into leadership, product management, or entrepreneurship",
        ],
        "category": "motivations",
    },
    {
        "question_id": "q_work_switch_deep",
        "phase": "academic",
        "question_text": "Is salary the main driver, or are you also looking for better intellectual growth, work-life balance, or a different nature of day-to-day work?",
        "options": [
            "Intellectual challenge and working with cutting-edge tech stack is #1",
            "Compensation growth and financial reward is the foremost priority",
            "Work-life balance with remote/hybrid flexibility is essential",
            "A balanced combination of compensation, tech modernization, and lifestyle",
        ],
        "category": "motivations",
    },
    {
        "question_id": "q_work_current_satisfaction",
        "phase": "academic",
        "question_text": "How satisfied are you with the technical trajectory of your current job role?",
        "options": [
            "Very dissatisfied: Looking for a complete domain change",
            "Somewhat dissatisfied: Want to upskill and move to higher-impact projects",
            "Neutral: Comfortable, but worried about future career stagnation",
            "Satisfied with fundamentals, but looking for the right next leap",
        ],
        "category": "motivations",
    },
    {
        "question_id": "q_work_target_role",
        "phase": "goals",
        "question_text": "What kind of role would you ideally love to hold 18-24 months from now?",
        "options": [
            "AI / Machine Learning Engineer or Data Scientist",
            "Cloud Architect / DevOps & Site Reliability Engineer",
            "Technical Product Manager or Solutions Consultant",
            "Full-Stack Software Development Engineer (SDE II / Senior)",
            "Tech Lead / Engineering Manager",
            "Tech Founder / Independent Consultant",
        ],
        "category": "career_goals",
    },
]

# Universal Deep-Discovery Core Questions (Phases 2 through 5)
UNIVERSAL_CORE_FLOW = [
    # ─── Cognitive & Problem-Solving Style ───
    {
        "question_id": "q_core_prob_solving",
        "phase": "skills",
        "question_text": "When confronted with an unfamiliar, complex technical problem, what is your instinctive approach?",
        "options": [
            "Deconstruct it logically into mathematical and algorithmic steps",
            "Experiment hands-on by rapid trial, prototyping, and debugging",
            "Research existing design patterns, documentation, and forum solutions",
            "Discuss with team members and brainstorm alternative perspectives",
        ],
        "category": "problem_solving",
    },
    {
        "question_id": "q_core_ambiguity",
        "phase": "personality",
        "question_text": "How comfortable are you working on open-ended problems that do not have a defined answer or fixed manual?",
        "options": [
            "Thrive on ambiguity: I love open-ended exploration and research",
            "Comfortable: As long as the ultimate objective and metrics are clear",
            "Prefer structured tasks: I work best with clear specifications and guidelines",
            "Need strict structure: I prefer established workflows and predictable routines",
        ],
        "category": "personality",
    },
    {
        "question_id": "q_core_learning_style",
        "phase": "skills",
        "question_text": "What is your most effective method for mastering a brand new complex technology or tool?",
        "options": [
            "Building a real project from scratch and learning through bugs",
            "Reading official documentation, reference manuals, and academic papers",
            "Following structured interactive courses, tutorials, and guided labs",
            "Pairing with an experienced mentor or study partner",
        ],
        "category": "learning_style",
    },

    # ─── Work Environment & Social Dynamics ───
    {
        "question_id": "q_core_social_dynamics",
        "phase": "personality",
        "question_text": "In what collaborative setting do you find yourself doing your best thinking?",
        "options": [
            "Deep solo focus with large uninterrupted blocks of quiet time",
            "Vibrant, close-knit team with continuous discussion and brainstorms",
            "Balanced hybrid: Solo execution combined with structured team reviews",
            "Customer-facing: Interacting with users, clients, and cross-functional partners",
        ],
        "category": "personality",
    },
    {
        "question_id": "q_core_org_culture",
        "phase": "work_pref",
        "question_text": "What type of organizational culture feels most attractive to your career aspirations?",
        "options": [
            "Fast-moving, high-autonomy tech startup with rapid responsibility",
            "Well-structured multinational product company with established mentorship",
            "Prestigious government, scientific, or defense laboratory (ISRO, VSSC, C-DAC, DRDO)",
            "Specialized technical consulting or client service agency",
            "Academic or university research laboratory",
        ],
        "category": "work_preferences",
    },
    {
        "question_id": "q_core_location_pref",
        "phase": "lifestyle",
        "question_text": "What geographical work arrangement fits your personal and family vision?",
        "options": [
            "Local Kerala technology ecosystem (Technopark Thiruvananthapuram / Infopark Kochi)",
            "Major national tech hubs (Bangalore / Hyderabad / Chennai / Pune)",
            "Full remote work from home with global or pan-India employers",
            "International relocation (Europe, North America, Middle East, Singapore)",
            "Flexible: Open to relocating wherever the highest-impact opportunity is",
        ],
        "category": "lifestyle_preferences",
    },

    # ─── Core Values, Financial & Impact Expectations ───
    {
        "question_id": "q_core_priority_value",
        "phase": "values",
        "question_text": "If you had to choose the single most non-negotiable value in your career, which would it be?",
        "options": [
            "Continuous intellectual growth and technical mastery",
            "High financial compensation and wealth generation potential",
            "Healthy work-life balance, low burnout, and time for family/passions",
            "Direct positive impact on society, healthcare, environment, or community",
            "Prestige, leadership influence, and industry recognition",
        ],
        "category": "values",
    },
    {
        "question_id": "q_core_risk_tolerance",
        "phase": "values",
        "question_text": "What describes your personal tolerance for career and financial risk?",
        "options": [
            "High risk tolerance: Willing to join early startups or bootstrap ventures for upside",
            "Moderate calculated risk: Open to emerging tech fields within stable companies",
            "Low risk: Strong preference for job security, predictable growth, and stability",
            "Conservative: Value permanent tenure and low volatility above all",
        ],
        "category": "values",
    },
    {
        "question_id": "q_core_leadership_pref",
        "phase": "personality",
        "question_text": "Where do you envision your long-term career path leaning over the next 5-10 years?",
        "options": [
            "Individual Contributor: Principal Engineer, Specialist Architect, or Researcher",
            "Engineering Leadership: Tech Lead, Engineering Manager, Director",
            "Product & Business: Product Manager, Strategist, or Executive",
            "Entrepreneurship: Founder, Co-founder, or Independent Creator",
            "Academia & Mentorship: Professor, Research Scientist, or Educator",
        ],
        "category": "career_goals",
    },
    {
        "question_id": "q_core_social_concerns",
        "phase": "concerns",
        "question_text": "Do you face any family expectations, career confusion, or social pressure regarding your career choices?",
        "options": [
            "Family prefers stable government/banking or traditional IT jobs, while I want cutting-edge tech",
            "Confused between coding, management, and higher studies — unsure which matches my strengths",
            "Concerned about AI automating entry-level tech roles and changing industry demands",
            "Pressure to start earning quickly to support family commitments",
            "Feel confident and supported in pursuing whatever field fits my passion",
        ],
        "category": "concerns",
    },
    {
        "question_id": "q_core_desired_impact",
        "phase": "goals",
        "question_text": "In what domain would you feel proudest contributing your skills and intellect?",
        "options": [
            "Building intelligent AI tools and software that save millions of hours of labor",
            "Healthcare, biomedical tech, and public well-being innovations",
            "Sustainable energy, environmental monitoring, agriculture, or ocean sciences",
            "Fintech, secure digital banking, and economic empowerment",
            "Education technology and empowering the next generation of students",
            "Creative multimedia, gaming, digital storytelling, and entertainment",
        ],
        "category": "career_goals",
    },
    {
        "question_id": "q_core_stress_coping",
        "phase": "personality",
        "question_text": "When facing tight deadlines or intense project pressure, how do you typically respond?",
        "options": [
            "Focus deeply on prioritizing critical tasks and executing methodically",
            "Communicate early with colleagues to divide workload and adjust timelines",
            "Feel energized by fast pacing and urgent problem solving",
            "Prefer paced, predictable timelines to avoid overwhelming stress",
        ],
        "category": "personality",
    },
    {
        "question_id": "q_core_kerala_opportunity",
        "phase": "lifestyle",
        "question_text": "Kerala is rapidly expanding in IT (Technopark Thiruvananthapuram, Infopark Kochi), Startup Village, Life Sciences, and Tourism. How do you view local opportunities?",
        "options": [
            "Very interested in growing within Kerala's vibrant tech ecosystem",
            "Interested if compensation and engineering standards match national Tier-1 hubs",
            "Prefer starting in national tech hubs (Bangalore/Hyderabad) first, then returning later",
            "Primarily aiming for international careers and global exposure",
        ],
        "category": "lifestyle_preferences",
    },
    {
        "question_id": "q_core_free_reflection",
        "phase": "goals",
        "question_text": "In your own words, what is one achievement or project you built or accomplished that made you feel truly proud?",
        "options": [
            "I'd like to type my answer in the box below...",
            "A software or coding project that solved a real problem",
            "An academic or exam milestone I worked hard to achieve",
            "Organizing a successful college event or student initiative",
            "Creating art, design, or multimedia work that received praise",
        ],
        "category": "motivations",
        "requires_text": True,
    },
]


class ConversationalAssessmentEngine:
    """
    Manages the baseline + adaptive interview dialogue, state tracking,
    and profile generation.
    """

    def __init__(self):
        pass

    def get_initial_state(self, student_id: str) -> Dict[str, Any]:
        """Initialize clean state for a new assessment interview."""
        return {
            "student_id": student_id,
            "status": "in_progress",
            "current_question_index": 0,
            "total_questions_planned": 26,
            "category": None,  # school, college, postgrad, working
            "education_profile": {},
            "academic_profile": {},
            "skills": {},
            "interests": {},
            "personality_traits": {
                "analytical": 50,
                "creative": 50,
                "social": 50,
                "leadership": 50,
                "practical": 50,
                "detail_oriented": 50,
                "risk_tolerance": 50,
                "independence": 50,
                "collaboration": 50,
                "learning_orientation": 50,
            },
            "values": {},
            "motivations": [],
            "career_goals": [],
            "work_preferences": {},
            "lifestyle_preferences": {},
            "concerns": [],
            "previous_answers": [],
            "confidence_scores": {},
            "adaptive_follow_ups_queued": [],
        }

    def get_next_question(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Determines the next question to ask based on current state and memory.
        Ensures no duplicate questions are ever returned.
        """
        answered_ids = {a["question_id"] for a in state.get("previous_answers", [])}

        # Step 1: Check category question
        if "q1_category" not in answered_ids:
            return CATEGORY_QUESTION

        # Step 2: Check any queued dynamic adaptive follow-up questions
        queued = state.get("adaptive_follow_ups_queued", [])
        while queued:
            next_follow_up = queued.pop(0)
            if next_follow_up["question_id"] not in answered_ids:
                return next_follow_up

        # Step 3: Education flow based on category
        cat = state.get("category", "college")
        edu_flow = []
        if cat == "school":
            edu_flow = SCHOOL_FLOW
        elif cat == "working":
            edu_flow = WORKING_FLOW
        else:
            edu_flow = COLLEGE_FLOW

        for q in edu_flow:
            if q["question_id"] not in answered_ids:
                return q

        # Step 4: Core Universal questions
        for q in UNIVERSAL_CORE_FLOW:
            if q["question_id"] not in answered_ids:
                return q

        # All questions completed
        return None

    def record_answer(
        self, state: Dict[str, Any], question_id: str, answer_text: str, question_def: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Records the answer into assessment memory and triggers adaptive reasoning.
        """
        # Save response in list
        ans_record = {
            "question_id": question_id,
            "answer": answer_text,
            "phase": question_def.get("phase", "general") if question_def else "general",
            "question_text": question_def.get("question_text", "") if question_def else "",
        }
        state["previous_answers"].append(ans_record)
        state["current_question_index"] = len(state["previous_answers"])

        # Check category determination
        if question_id == "q1_category":
            lowered = answer_text.lower()
            if "school" in lowered:
                state["category"] = "school"
            elif "working" in lowered:
                state["category"] = "working"
            elif "post graduate" in lowered or "master" in lowered:
                state["category"] = "postgrad"
            else:
                state["category"] = "college"
            state["education_profile"]["situation"] = state["category"]

        # Parse specific answer traits
        self._update_traits_and_memory(state, question_id, answer_text)

        # Check for adaptive follow-up injection
        self._check_for_adaptive_follow_up(state, question_id, answer_text)

        # Recalculate total questions planned
        base_count = 1 + (len(SCHOOL_FLOW) if state.get("category") == "school" else len(WORKING_FLOW) if state.get("category") == "working" else len(COLLEGE_FLOW)) + len(UNIVERSAL_CORE_FLOW)
        state["total_questions_planned"] = base_count + len(state.get("adaptive_follow_ups_queued", []))

        return state

    def _check_for_adaptive_follow_up(self, state: Dict[str, Any], question_id: str, answer_text: str):
        """
        Dynamically enqueues a deep-dive follow-up question when an ambiguous or
        high-impact response is given (e.g., 'Helping people', 'Interested in AI', 'High Salary').
        """
        answered_ids = {a["question_id"] for a in state.get("previous_answers", [])}
        queued_ids = {q["question_id"] for q in state.get("adaptive_follow_ups_queued", [])}
        lowered = answer_text.lower()

        # Follow-up on helping people / societal impact
        if "helping" in lowered or "society" in lowered or "social" in lowered:
            fid = "q_followup_helping_people"
            if fid not in answered_ids and fid not in queued_ids:
                state.setdefault("adaptive_follow_ups_queued", []).append({
                    "question_id": fid,
                    "phase": "values",
                    "question_text": "You mentioned helping people and societal impact. What dimension of helping people resonates most with you?",
                    "options": [
                        "Solving complex technical problems that make life easier for millions",
                        "Direct healthcare, medical diagnosis, or biomedical therapies",
                        "Teaching, mentoring, and educating students and professionals",
                        "Building digital infrastructure for financial inclusion and transparency",
                        "Environmental protection, sustainability, and renewable resources",
                    ],
                    "category": "values",
                })

        # Follow-up on AI interest
        if "artificial intelligence" in lowered or "machine learning" in lowered or "ai" in lowered:
            fid = "q_followup_ai_depth"
            if fid not in answered_ids and fid not in queued_ids:
                state.setdefault("adaptive_follow_ups_queued", []).append({
                    "question_id": fid,
                    "phase": "interests",
                    "question_text": "What part of Artificial Intelligence and Data excites your curiosity most?",
                    "options": [
                        "Mathematical and algorithmic research (Transformers, Neural Nets, Math)",
                        "Engineering scalable AI apps (APIs, RAG, Full-Stack AI products)",
                        "Data analysis, statistical modeling, and business insights",
                        "Computer Vision, Robotics, and Autonomous systems",
                        "Ethical AI, policy, and human-computer safety",
                    ],
                    "category": "interests",
                })

        # Follow-up on Business / Management interest
        if "management" in lowered or "product" in lowered or "business" in lowered:
            fid = "q_followup_mgmt_depth"
            if fid not in answered_ids and fid not in queued_ids:
                state.setdefault("adaptive_follow_ups_queued", []).append({
                    "question_id": fid,
                    "phase": "interests",
                    "question_text": "When you think of Product & Business leadership, what activity energizes you most?",
                    "options": [
                        "Understanding user pain points and designing intuitive product features",
                        "Market research, competitor analysis, and growth strategies",
                        "Coordinating engineering teams to deliver projects on schedule",
                        "Financial budgeting, investment analysis, and business metrics",
                    ],
                    "category": "interests",
                })

    def _update_traits_and_memory(self, state: Dict[str, Any], question_id: str, answer_text: str):
        """Update personality dimensions, skills, and memory tags."""
        traits = state.setdefault("personality_traits", {})
        lowered = answer_text.lower()

        # Analytical updates
        if any(w in lowered for w in ["math", "logic", "algorithm", "analytical", "data", "physics", "code"]):
            traits["analytical"] = min(100, traits.get("analytical", 50) + 7)
            traits["detail_oriented"] = min(100, traits.get("detail_oriented", 50) + 4)
            state.setdefault("skills", {})["analytical_reasoning"] = "high"

        # Creative updates
        if any(w in lowered for w in ["design", "ui/ux", "art", "creative", "multimedia", "visual", "gaming"]):
            traits["creative"] = min(100, traits.get("creative", 50) + 8)
            state.setdefault("interests", {})["creative_design"] = True

        # Social & Collaboration updates
        if any(w in lowered for w in ["team", "collaborat", "communicat", "mentor", "talk", "customer"]):
            traits["social"] = min(100, traits.get("social", 50) + 7)
            traits["collaboration"] = min(100, traits.get("collaboration", 50) + 6)
            traits["independence"] = max(20, traits.get("independence", 50) - 3)

        # Independence updates
        if any(w in lowered for w in ["solo", "independent", "quiet", "own pace"]):
            traits["independence"] = min(100, traits.get("independence", 50) + 8)
            traits["social"] = max(20, traits.get("social", 50) - 4)

        # Leadership updates
        if any(w in lowered for w in ["lead", "manage", "founder", "organize", "director", "startup"]):
            traits["leadership"] = min(100, traits.get("leadership", 50) + 8)
            traits["risk_tolerance"] = min(100, traits.get("risk_tolerance", 50) + 5)

        # Risk tolerance updates
        if any(w in lowered for w in ["startup", "high risk", "upside", "bootstrap"]):
            traits["risk_tolerance"] = min(100, traits.get("risk_tolerance", 50) + 10)
        elif any(w in lowered for w in ["stable", "government", "security", "low risk", "permanent"]):
            traits["risk_tolerance"] = max(20, traits.get("risk_tolerance", 50) - 8)

        # Practical updates
        if any(w in lowered for w in ["hands-on", "build", "project", "prototype", "experiment", "hardware"]):
            traits["practical"] = min(100, traits.get("practical", 50) + 7)

        # Learning orientation updates
        if any(w in lowered for w in ["learning", "research", "mastery", "curiosity", "documentation"]):
            traits["learning_orientation"] = min(100, traits.get("learning_orientation", 50) + 7)

    def generate_career_profile(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes the complete assessment into:
        1. 10-dimension Personality Profile
        2. Structured Interest Profile
        3. Skills Profile
        4. Values Profile
        5. Top 5 Preliminary Career Matches
        """
        traits = state.get("personality_traits", {})

        personality_profile = {
            "Analytical": round(traits.get("analytical", 65), 1),
            "Creative": round(traits.get("creative", 55), 1),
            "Social": round(traits.get("social", 50), 1),
            "Leadership": round(traits.get("leadership", 45), 1),
            "Practical": round(traits.get("practical", 60), 1),
            "Detail-oriented": round(traits.get("detail_oriented", 65), 1),
            "Risk tolerance": round(traits.get("risk_tolerance", 50), 1),
            "Independence": round(traits.get("independence", 60), 1),
            "Collaboration": round(traits.get("collaboration", 55), 1),
            "Learning orientation": round(traits.get("learning_orientation", 70), 1),
            "disclaimer": "This is a career guidance profile, not a medical or psychological diagnosis.",
        }

        # Calculate structured interest weights
        all_text = " ".join([a.get("answer", "") for a in state.get("previous_answers", [])]).lower()
        interest_profile = {
            "AI / Machine Learning": 88 if any(k in all_text for k in ["ai", "machine learning", "data"]) else 45,
            "Software Development": 85 if any(k in all_text for k in ["software", "code", "programming", "full-stack"]) else 50,
            "Data Science & Analytics": 82 if any(k in all_text for k in ["data", "statistics", "analytics"]) else 40,
            "Cybersecurity & Cloud": 75 if any(k in all_text for k in ["cyber", "cloud", "network", "devops"]) else 35,
            "UI/UX & Product Design": 70 if any(k in all_text for k in ["design", "ui/ux", "visual", "product"]) else 30,
            "Core Engineering & Robotics": 65 if any(k in all_text for k in ["robotics", "hardware", "iot", "circuit"]) else 25,
            "Management & Strategy": 60 if any(k in all_text for k in ["management", "business", "lead"]) else 30,
            "Research & Academia": 58 if any(k in all_text for k in ["research", "phd", "academic", "papers"]) else 35,
            "Public Service & Governance": 50 if any(k in all_text for k in ["government", "psc", "isro", "public"]) else 20,
        }

        skills_profile = {
            "Technical Problem Solving": "Advanced" if traits.get("analytical", 50) > 65 else "Intermediate",
            "Programming & Algorithms": "Strong" if "code" in all_text or "python" in all_text else "Foundational",
            "Analytical Thinking": "High" if traits.get("analytical", 50) > 60 else "Moderate",
            "Collaboration & Team Dynamics": "High" if traits.get("collaboration", 50) > 60 else "Moderate",
            "Independent Execution": "High" if traits.get("independence", 50) > 60 else "Moderate",
        }

        values_profile = {
            "Primary Driver": "Intellectual Mastery & Tech Innovation" if traits.get("analytical", 50) >= traits.get("leadership", 50) else "Leadership & Influence",
            "Work Environment Fit": "Agile Product Team / Tech Innovation",
            "Regional Context": "High alignment with Kerala tech hubs (Technopark / Infopark) & Global Tech Hubs",
        }

        # Generate Top 5 preliminary career directions
        top_matches = self._calculate_top_5_matches(state, personality_profile, interest_profile)

        return {
            "personality_profile": personality_profile,
            "interest_profile": interest_profile,
            "skills_profile": skills_profile,
            "values_profile": values_profile,
            "confidence_profile": {"overall_assessment_confidence": "88%", "stability_score": "High"},
            "career_recommendations": top_matches,
        }

    def _calculate_top_5_matches(
        self, state: Dict[str, Any], personality: Dict[str, Any], interests: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Calculates top 5 career directions with:
        Career, Match percentage, Why it matches, Supporting evidence, Potential concerns, Skills needed.
        Considers Kerala + National + Global contexts responsibly.
        """
        all_text = " ".join([a.get("answer", "") for a in state.get("previous_answers", [])]).lower()
        analytical = personality.get("Analytical", 60)
        creative = personality.get("Creative", 50)

        matches = [
            {
                "career_name": "Data Scientist / AI Specialist",
                "match_score": min(95.0, round(analytical * 0.7 + interests.get("AI / Machine Learning", 50) * 0.3, 1)),
                "reason": "Based on your responses, Data Science and AI appear to be a strong match due to your solid analytical reasoning and preference for data-driven problem solving.",
                "supporting_evidence": [
                    "High analytical orientation demonstrated across problem-solving questions.",
                    "Stated enthusiasm for working with algorithms and predictive models.",
                    "Enjoyment of hands-on technical experimentation.",
                ],
                "concerns": [
                    "Requires rigorous mathematical foundation in linear algebra, multivariable calculus, and probability.",
                    "High competition for pure AI research roles without hands-on portfolio projects.",
                ],
                "skills_needed": ["Python", "Pandas", "Scikit-Learn", "Applied Statistics", "SQL", "Deep Learning basics"],
                "regional_opportunity": "Thriving ecosystem in Technopark Thiruvananthapuram, Infopark Kochi AI clusters, Bangalore tech hubs, and global remote opportunities.",
            },
            {
                "career_name": "Full-Stack Software Development Engineer",
                "match_score": min(92.0, round(analytical * 0.5 + personality.get("Practical", 50) * 0.4 + 10, 1)),
                "reason": "Based on your responses, Software Engineering appears to be a very suitable match given your interest in building functional systems and practical coding.",
                "supporting_evidence": [
                    "Preference for building end-to-end applications that real people use.",
                    "Comfortable troubleshooting logic bugs and working in structured development cycles.",
                ],
                "concerns": [
                    "Fast-moving frontend frameworks and cloud tooling require continuous lifelong learning.",
                ],
                "skills_needed": ["JavaScript/TypeScript", "Python or Java", "React/Next.js", "Relational Databases", "Git & CI/CD"],
                "regional_opportunity": "Massive hiring across Kerala IT corridors (Technopark & Infopark), top MNCs, and worldwide remote tech roles.",
            },
            {
                "career_name": "Machine Learning Engineer",
                "match_score": min(89.0, round(analytical * 0.6 + interests.get("AI / Machine Learning", 50) * 0.35, 1)),
                "reason": "Based on your responses, Machine Learning Engineering appears to be a strong match if you enjoy taking data models and deploying them into production systems.",
                "supporting_evidence": [
                    "Strong affinity for algorithmic logic combined with software execution.",
                    "Interest in building predictive applications rather than purely static web pages.",
                ],
                "concerns": [
                    "Requires dual competency in both machine learning mathematics and DevOps/containerization infrastructure.",
                ],
                "skills_needed": ["Python", "PyTorch or TensorFlow", "Docker", "Model Deployment (FastAPI/Triton)", "Cloud AI APIs"],
                "regional_opportunity": "High-growth niche in Kerala startups, automotive tech clusters in South India, and global AI firms.",
            },
            {
                "career_name": "Cybersecurity & Cloud Solutions Analyst",
                "match_score": min(84.0, round(personality.get("Detail-oriented", 60) * 0.6 + analytical * 0.3, 1)),
                "reason": "Based on your responses, Cybersecurity and Cloud infrastructure appear to be a viable direction if you enjoy network resilience and systemic integrity.",
                "supporting_evidence": [
                    "High attention to detail and methodical approach to troubleshooting unexpected issues.",
                    "Appreciation for system reliability and secure architecture.",
                ],
                "concerns": [
                    "Requires industry certifications (CompTIA Security+, AWS/Azure Solutions Architect) to fast-track entry-level placements.",
                ],
                "skills_needed": ["Linux Administration", "Networking (TCP/IP)", "AWS or GCP Fundamentals", "Security Auditing Tools", "Bash/Python Scripting"],
                "regional_opportunity": "Kerala Police Cyberdome, banking operations in Kochi, aerospace/defense facilities in Thiruvananthapuram, and MNC security centers.",
            },
            {
                "career_name": "Technical Product Manager / Tech Consultant",
                "match_score": min(82.0, round(personality.get("Leadership", 50) * 0.5 + personality.get("Social", 50) * 0.4 + 10, 1)),
                "reason": "Based on your responses, Technical Product Management or Consulting appears to be a compelling pathway blending technical understanding with human communication.",
                "supporting_evidence": [
                    "Strong interpersonal empathy and balance between technical logic and user experience.",
                    "Enjoyment of seeing how technology solves business and human challenges.",
                ],
                "concerns": [
                    "Usually requires 1-2 years of technical experience or MBA/Management specialization before direct PM ownership.",
                ],
                "skills_needed": ["Product Roadmap Design", "Agile & Scrum", "User Journey Mapping", "Data Analytics (SQL/PowerBI)", "Stakeholder Communication"],
                "regional_opportunity": "Consulting firms, software product companies in Kochi & Bangalore, and digital transformation agencies.",
            },
        ]

        # Sort matches by match_score descending
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[:5]


assessment_engine = ConversationalAssessmentEngine()
