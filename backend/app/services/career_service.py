"""
Career Seeding Service
────────────────────────────────────────────────────────────────────────────
Seeds the database with 12 career entries, their market data, exams,
scholarships, and career myths. Run once on startup if table is empty.
"""
from __future__ import annotations
from sqlalchemy.orm import Session
from app.models.career import Career, CareerSkill, Exam, Scholarship, CareerMyth, MarketInfo
import logging

logger = logging.getLogger(__name__)

CAREERS_DATA = [
    {
        "title": "Machine Learning Engineer",
        "slug": "machine-learning-engineer",
        "description": (
            "Machine Learning Engineers design, build, and deploy ML models and systems. "
            "They bridge the gap between data science research and production software engineering."
        ),
        "required_degree": "B.Tech / B.E. in CS, ECE, or Mathematics",
        "required_skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "Statistics", "SQL", "Data Structures"],
        "optional_skills": ["PyTorch", "Spark", "Kubernetes", "MLflow", "Airflow"],
        "salary_beginner": 8.0, "salary_mid": 20.0, "salary_senior": 50.0,
        "career_growth": "High",
        "work_type": "Hybrid/Remote",
        "industries": ["Technology", "Finance", "Healthcare", "E-commerce", "Research"],
        "job_roles": ["ML Engineer", "AI Engineer", "Research Engineer", "MLOps Engineer"],
        "interest_tags": ["programming", "mathematics", "data_analysis", "research"],
        "goal_tags": ["high_salary", "research", "international_career"],
        "work_pref_tags": ["individual_work", "research_oriented"],
        "market": {
            "demand_level": "Very High", "demand_growth_pct": 35.0,
            "top_skills": ["Python", "TensorFlow", "PyTorch", "MLOps", "Transformers"],
            "emerging_technologies": ["Large Language Models", "Diffusion Models", "AutoML", "MLOps Platforms"],
            "job_openings_india": 45000,
            "top_companies": ["Google", "Microsoft", "Amazon", "Flipkart", "PhonePe", "Zomato", "NVIDIA", "Adobe"],
            "industry_trends": ["LLM-powered applications", "AI at the edge", "Responsible AI", "AutoML democratization"],
            "avg_salary_fresher": 9.0, "avg_salary_experienced": 30.0,
        },
        "exams": [
            {"name": "TensorFlow Developer Certificate", "category": "Certification", "conducting_org": "Google",
             "eligibility": "Any developer familiar with Python & TensorFlow", "frequency": "On-demand",
             "official_website": "https://tensorflow.org/certificate",
             "description": "Official Google certification for TensorFlow developers."},
            {"name": "AWS Certified Machine Learning – Specialty", "category": "Certification", "conducting_org": "Amazon Web Services",
             "eligibility": "2+ years ML/data science experience", "frequency": "On-demand",
             "official_website": "https://aws.amazon.com/certification/certified-machine-learning-specialty/",
             "description": "Validates ability to design, implement, deploy, and maintain ML solutions on AWS."},
            {"name": "GATE CS", "category": "Government Exam", "conducting_org": "IITs / IISc",
             "eligibility": "B.Tech final year or graduate", "frequency": "Annual",
             "official_website": "https://gate.iitb.ac.in",
             "description": "Gateway to M.Tech at IITs and PSU jobs in India."},
        ],
        "myths": [
            {"myth": "ML Engineering is only for PhDs.", "reality": "Most industry ML roles are held by B.Tech/M.Tech graduates. A strong portfolio matters more than a PhD."},
            {"myth": "You need to be a mathematics genius.", "reality": "You need solid understanding of key concepts (linear algebra, probability, statistics) which can be learnt progressively."},
        ],
    },
    {
        "title": "Data Scientist",
        "slug": "data-scientist",
        "description": (
            "Data Scientists extract insights from large datasets using statistical analysis, "
            "machine learning, and data visualization to guide business decisions."
        ),
        "required_degree": "B.Tech/B.Sc in CS, Statistics, Mathematics or related field",
        "required_skills": ["Python", "Statistics", "Machine Learning", "SQL", "Pandas", "Data Visualization"],
        "optional_skills": ["R", "Spark", "Tableau", "Power BI", "Deep Learning"],
        "salary_beginner": 7.0, "salary_mid": 18.0, "salary_senior": 45.0,
        "career_growth": "High",
        "work_type": "Hybrid/Remote",
        "industries": ["Finance", "Healthcare", "E-commerce", "Technology", "Consulting"],
        "job_roles": ["Data Scientist", "Applied Scientist", "Research Analyst", "ML Researcher"],
        "interest_tags": ["data_analysis", "mathematics", "research", "programming"],
        "goal_tags": ["high_salary", "research", "work_life_balance"],
        "work_pref_tags": ["individual_work", "research_oriented"],
        "market": {
            "demand_level": "Very High", "demand_growth_pct": 28.0,
            "top_skills": ["Python", "SQL", "Statistics", "ML", "Data Visualization"],
            "emerging_technologies": ["AutoML", "Generative AI", "Real-time Analytics", "Feature Stores"],
            "job_openings_india": 55000,
            "top_companies": ["Mu Sigma", "Accenture", "Fractal Analytics", "IBM", "Tiger Analytics", "ThoughtWorks"],
            "industry_trends": ["AI-driven analytics", "Real-time decision systems", "Explainable AI", "Data mesh"],
            "avg_salary_fresher": 7.5, "avg_salary_experienced": 25.0,
        },
        "exams": [
            {"name": "IBM Data Science Professional Certificate", "category": "Certification",
             "conducting_org": "IBM / Coursera", "eligibility": "No prerequisites",
             "frequency": "Self-paced", "official_website": "https://coursera.org/professional-certificates/ibm-data-science",
             "description": "Comprehensive 10-course program covering data science fundamentals."},
            {"name": "Google Professional Data Engineer", "category": "Certification",
             "conducting_org": "Google Cloud", "eligibility": "3+ years industry experience",
             "frequency": "On-demand", "official_website": "https://cloud.google.com/certification/data-engineer",
             "description": "Validates expertise in designing and building data processing systems on Google Cloud."},
        ],
        "myths": [
            {"myth": "Data Scientists only work with Excel and pivot tables.", "reality": "Modern data scientists write complex ML pipelines, work with big data frameworks, and deploy models to production."},
            {"myth": "You need a Masters degree to become a Data Scientist.", "reality": "Many successful data scientists have a B.Tech/B.Sc. What matters is your portfolio and skills."},
        ],
    },
    {
        "title": "Software Engineer",
        "slug": "software-engineer",
        "description": (
            "Software Engineers design, develop, test, and maintain software applications "
            "across web, mobile, backend, and embedded systems."
        ),
        "required_degree": "B.Tech / B.E. in CS, IT, or related field",
        "required_skills": ["Python", "Data Structures", "Algorithms", "SQL", "Git", "System Design"],
        "optional_skills": ["JavaScript", "React", "Node.js", "Docker", "AWS", "Java"],
        "salary_beginner": 5.0, "salary_mid": 16.0, "salary_senior": 40.0,
        "career_growth": "High",
        "work_type": "Office/Hybrid/Remote",
        "industries": ["Technology", "Finance", "Healthcare", "Government", "E-commerce"],
        "job_roles": ["Software Developer", "Backend Engineer", "Full Stack Developer", "SRE", "DevOps Engineer"],
        "interest_tags": ["programming", "mathematics", "design"],
        "goal_tags": ["high_salary", "job_stability", "international_career"],
        "work_pref_tags": ["team_work", "remote_work"],
        "market": {
            "demand_level": "Very High", "demand_growth_pct": 25.0,
            "top_skills": ["Python", "Java", "JavaScript", "Cloud", "System Design"],
            "emerging_technologies": ["Cloud-native development", "Serverless", "AI-integrated apps", "WebAssembly"],
            "job_openings_india": 200000,
            "top_companies": ["TCS", "Infosys", "Wipro", "Google", "Amazon", "Microsoft", "Atlassian", "Freshworks"],
            "industry_trends": ["API-first design", "Microservices", "DevSecOps", "Low-code platforms"],
            "avg_salary_fresher": 5.5, "avg_salary_experienced": 20.0,
        },
        "exams": [
            {"name": "GATE CS", "category": "Government Exam", "conducting_org": "IITs / IISc",
             "eligibility": "B.Tech final year", "frequency": "Annual",
             "official_website": "https://gate.iitb.ac.in", "description": "For M.Tech admission at IITs."},
            {"name": "AWS Solutions Architect Associate", "category": "Certification",
             "conducting_org": "Amazon Web Services", "eligibility": "Basic cloud knowledge",
             "frequency": "On-demand", "official_website": "https://aws.amazon.com/certification/",
             "description": "Most popular cloud certification globally."},
        ],
        "myths": [
            {"myth": "You need to know 10+ programming languages to be a software engineer.", "reality": "Most roles require depth in 1-2 languages. Breadth comes with experience."},
            {"myth": "Only students from IITs get good software jobs.", "reality": "Companies hire from all colleges — your skills, projects, and interview performance matter most."},
        ],
    },
    {
        "title": "AI Engineer",
        "slug": "ai-engineer",
        "description": (
            "AI Engineers build and integrate AI/ML models into production systems, "
            "including LLM applications, AI APIs, and intelligent automation systems."
        ),
        "required_degree": "B.Tech in CS/ECE/Mathematics; M.Tech preferred for research roles",
        "required_skills": ["Python", "Machine Learning", "Deep Learning", "LLMs", "APIs", "Cloud", "MLOps"],
        "optional_skills": ["LangChain", "Hugging Face", "FastAPI", "Kubernetes", "Prompt Engineering"],
        "salary_beginner": 10.0, "salary_mid": 25.0, "salary_senior": 60.0,
        "career_growth": "Very High",
        "work_type": "Remote/Hybrid",
        "industries": ["Technology", "Finance", "Healthcare", "Robotics", "Defense"],
        "job_roles": ["AI Engineer", "Generative AI Engineer", "LLM Engineer", "AI Solutions Architect"],
        "interest_tags": ["programming", "research", "mathematics", "data_analysis"],
        "goal_tags": ["high_salary", "research", "international_career"],
        "work_pref_tags": ["research_oriented", "individual_work"],
        "market": {
            "demand_level": "Extremely High", "demand_growth_pct": 45.0,
            "top_skills": ["Python", "LLMs", "LangChain", "Prompt Engineering", "MLOps"],
            "emerging_technologies": ["GPT-4/Gemini APIs", "RAG systems", "AI Agents", "Multimodal AI"],
            "job_openings_india": 30000,
            "top_companies": ["Google DeepMind", "OpenAI", "Microsoft", "NVIDIA", "Anthropic", "Sarvam AI"],
            "industry_trends": ["Agentic AI", "Enterprise AI", "Edge AI", "AI safety"],
            "avg_salary_fresher": 12.0, "avg_salary_experienced": 40.0,
        },
        "exams": [
            {"name": "Google Professional ML Engineer", "category": "Certification",
             "conducting_org": "Google Cloud", "eligibility": "3+ years ML experience",
             "frequency": "On-demand", "official_website": "https://cloud.google.com/certification/machine-learning-engineer",
             "description": "Validates expertise in designing, building and productionizing ML models."},
        ],
        "myths": [
            {"myth": "AI will replace AI engineers too.", "reality": "AI tools augment AI engineers. The demand for AI Engineering roles is growing faster than any other tech field."},
        ],
    },
    {
        "title": "Data Analyst",
        "slug": "data-analyst",
        "description": (
            "Data Analysts transform raw data into actionable business insights using SQL, "
            "Excel, and visualization tools. They are the bridge between raw data and decision makers."
        ),
        "required_degree": "BBA, B.Sc Statistics, B.Tech, or any bachelor's with analytics skills",
        "required_skills": ["SQL", "Excel", "Data Visualization", "Statistics", "Python"],
        "optional_skills": ["Tableau", "Power BI", "R", "Google Analytics"],
        "salary_beginner": 4.0, "salary_mid": 10.0, "salary_senior": 25.0,
        "career_growth": "Medium",
        "work_type": "Office/Hybrid",
        "industries": ["Finance", "Retail", "Healthcare", "Consulting", "Government"],
        "job_roles": ["Data Analyst", "Business Intelligence Analyst", "Reporting Analyst", "Operations Analyst"],
        "interest_tags": ["data_analysis", "business", "mathematics"],
        "goal_tags": ["job_stability", "work_life_balance"],
        "work_pref_tags": ["individual_work", "office_work"],
        "market": {
            "demand_level": "High", "demand_growth_pct": 20.0,
            "top_skills": ["SQL", "Excel", "Tableau", "Power BI", "Python"],
            "emerging_technologies": ["Self-service BI", "Augmented Analytics", "Real-time Dashboards"],
            "job_openings_india": 80000,
            "top_companies": ["Deloitte", "KPMG", "EY", "PwC", "Gartner", "Nielsen", "MakeMyTrip"],
            "industry_trends": ["Self-service analytics", "Data democratization", "Real-time reporting"],
            "avg_salary_fresher": 4.5, "avg_salary_experienced": 14.0,
        },
        "exams": [
            {"name": "Microsoft Power BI Data Analyst (PL-300)", "category": "Certification",
             "conducting_org": "Microsoft", "eligibility": "Basic data knowledge",
             "frequency": "On-demand", "official_website": "https://learn.microsoft.com/en-us/certifications/power-bi-data-analyst-associate/",
             "description": "Industry-recognized certification for Power BI skills."},
        ],
        "myths": [
            {"myth": "Data Analysts are just glorified Excel users.", "reality": "Modern data analysts use SQL, Python, and BI tools to handle millions of rows and drive strategic decisions."},
        ],
    },
    {
        "title": "Cybersecurity Analyst",
        "slug": "cybersecurity-analyst",
        "description": (
            "Cybersecurity Analysts protect organizations from digital attacks. "
            "They monitor networks, detect threats, and implement security measures."
        ),
        "required_degree": "B.Tech in CS/IT/ECE or equivalent certification path",
        "required_skills": ["Networking", "Linux", "Security Tools", "Python", "Ethical Hacking", "SIEM"],
        "optional_skills": ["Penetration Testing", "Reverse Engineering", "Cloud Security", "Forensics"],
        "salary_beginner": 5.0, "salary_mid": 14.0, "salary_senior": 35.0,
        "career_growth": "Very High",
        "work_type": "Office/Hybrid",
        "industries": ["Banking", "Government", "Defense", "IT Services", "Healthcare"],
        "job_roles": ["SOC Analyst", "Penetration Tester", "Security Engineer", "CISO", "Threat Intelligence Analyst"],
        "interest_tags": ["cybersecurity", "programming", "research"],
        "goal_tags": ["job_stability", "international_career"],
        "work_pref_tags": ["individual_work", "practical_work"],
        "market": {
            "demand_level": "Very High", "demand_growth_pct": 32.0,
            "top_skills": ["Ethical Hacking", "SIEM", "Cloud Security", "Threat Analysis", "Python"],
            "emerging_technologies": ["AI-driven threat detection", "Zero Trust Architecture", "Cloud Security Posture Management"],
            "job_openings_india": 40000,
            "top_companies": ["Quick Heal", "Tata Communications", "IBM Security", "Palo Alto Networks", "CrowdStrike"],
            "industry_trends": ["AI-powered security", "Zero Trust", "Cloud-native security", "Ransomware defense"],
            "avg_salary_fresher": 5.5, "avg_salary_experienced": 18.0,
        },
        "exams": [
            {"name": "CEH (Certified Ethical Hacker)", "category": "Certification",
             "conducting_org": "EC-Council", "eligibility": "2 years IT experience or training",
             "frequency": "On-demand", "official_website": "https://eccouncil.org/train-certify/certified-ethical-hacker-ceh/",
             "description": "Globally recognized ethical hacking certification."},
            {"name": "CompTIA Security+", "category": "Certification",
             "conducting_org": "CompTIA", "eligibility": "No mandatory prerequisites",
             "frequency": "On-demand", "official_website": "https://comptia.org/certifications/security",
             "description": "Entry-level cybersecurity certification widely accepted globally."},
        ],
        "myths": [
            {"myth": "Cybersecurity is only about hacking.", "reality": "Cybersecurity includes cloud security, compliance, governance, forensics, incident response, and more."},
        ],
    },
    {
        "title": "Cloud Engineer",
        "slug": "cloud-engineer",
        "description": (
            "Cloud Engineers design, build, and manage cloud infrastructure on platforms "
            "like AWS, Azure, and GCP. They enable organizations to scale efficiently."
        ),
        "required_degree": "B.Tech in CS/IT/ECE",
        "required_skills": ["AWS/Azure/GCP", "Linux", "Networking", "Python", "Terraform", "Docker", "Kubernetes"],
        "optional_skills": ["CI/CD", "Ansible", "Serverless", "Cost Optimization"],
        "salary_beginner": 6.0, "salary_mid": 18.0, "salary_senior": 45.0,
        "career_growth": "Very High",
        "work_type": "Remote/Hybrid",
        "industries": ["Technology", "Finance", "Healthcare", "E-commerce"],
        "job_roles": ["Cloud Architect", "DevOps Engineer", "Site Reliability Engineer", "Cloud Consultant"],
        "interest_tags": ["cloud", "programming", "research"],
        "goal_tags": ["high_salary", "job_stability", "international_career"],
        "work_pref_tags": ["remote_work", "practical_work"],
        "market": {
            "demand_level": "Very High", "demand_growth_pct": 30.0,
            "top_skills": ["AWS", "Kubernetes", "Terraform", "Python", "CI/CD"],
            "emerging_technologies": ["FinOps", "Cloud-native AI", "Multi-cloud", "Serverless"],
            "job_openings_india": 60000,
            "top_companies": ["Amazon AWS", "Microsoft Azure", "Google Cloud", "Accenture", "Capgemini", "HCL"],
            "industry_trends": ["Multi-cloud strategy", "FinOps", "Platform engineering", "Green cloud"],
            "avg_salary_fresher": 7.0, "avg_salary_experienced": 25.0,
        },
        "exams": [
            {"name": "AWS Certified Cloud Practitioner", "category": "Certification",
             "conducting_org": "Amazon Web Services", "eligibility": "No prerequisites",
             "frequency": "On-demand", "official_website": "https://aws.amazon.com/certification/certified-cloud-practitioner/",
             "description": "Entry-level AWS certification — ideal starting point."},
            {"name": "Google Associate Cloud Engineer", "category": "Certification",
             "conducting_org": "Google Cloud", "eligibility": "6+ months GCP experience",
             "frequency": "On-demand", "official_website": "https://cloud.google.com/certification/cloud-engineer",
             "description": "Validates ability to deploy and manage GCP infrastructure."},
        ],
        "myths": [
            {"myth": "Cloud engineering is just managing servers online.", "reality": "Cloud engineers architect complex distributed systems, automate infrastructure, and optimize costs at scale."},
        ],
    },
    {
        "title": "DevOps Engineer",
        "slug": "devops-engineer",
        "description": (
            "DevOps Engineers bridge development and operations, automating build, test, "
            "and deployment pipelines to enable fast, reliable software delivery."
        ),
        "required_degree": "B.Tech in CS/IT or equivalent",
        "required_skills": ["Linux", "Docker", "Kubernetes", "CI/CD", "Git", "Python/Bash", "Monitoring"],
        "optional_skills": ["Terraform", "Ansible", "Jenkins", "Prometheus", "Grafana"],
        "salary_beginner": 5.5, "salary_mid": 16.0, "salary_senior": 40.0,
        "career_growth": "High",
        "work_type": "Remote/Hybrid",
        "industries": ["Technology", "E-commerce", "Finance", "Gaming"],
        "job_roles": ["DevOps Engineer", "SRE", "Platform Engineer", "Release Engineer"],
        "interest_tags": ["programming", "cloud"],
        "goal_tags": ["job_stability", "high_salary"],
        "work_pref_tags": ["team_work", "practical_work"],
        "market": {
            "demand_level": "High", "demand_growth_pct": 22.0,
            "top_skills": ["Kubernetes", "Docker", "CI/CD", "Terraform", "Monitoring"],
            "emerging_technologies": ["GitOps", "Platform Engineering", "eBPF", "AIOps"],
            "job_openings_india": 45000,
            "top_companies": ["Razorpay", "Swiggy", "Dunzo", "Atlassian", "HashiCorp", "Elastic"],
            "industry_trends": ["Platform engineering", "GitOps", "Observability", "Security-as-code"],
            "avg_salary_fresher": 6.0, "avg_salary_experienced": 22.0,
        },
        "exams": [
            {"name": "Certified Kubernetes Administrator (CKA)", "category": "Certification",
             "conducting_org": "CNCF", "eligibility": "Kubernetes experience",
             "frequency": "On-demand", "official_website": "https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/",
             "description": "Premier Kubernetes administration certification."},
        ],
        "myths": [
            {"myth": "DevOps is just a job title for sysadmins.", "reality": "DevOps requires deep programming, cloud architecture, automation, and security knowledge."},
        ],
    },
    {
        "title": "UI/UX Designer",
        "slug": "ui-ux-designer",
        "description": (
            "UI/UX Designers create intuitive, beautiful, and accessible user interfaces "
            "for web and mobile applications through research, wireframing, and prototyping."
        ),
        "required_degree": "B.Des, B.Tech, BCA, BFA or equivalent with design portfolio",
        "required_skills": ["Figma", "User Research", "Wireframing", "Prototyping", "Design Systems", "HTML/CSS basics"],
        "optional_skills": ["Adobe XD", "Illustrator", "Motion Design", "Usability Testing", "React"],
        "salary_beginner": 4.0, "salary_mid": 12.0, "salary_senior": 30.0,
        "career_growth": "Medium",
        "work_type": "Office/Remote",
        "industries": ["Technology", "E-commerce", "Media", "Healthcare", "EdTech"],
        "job_roles": ["UI Designer", "UX Researcher", "Product Designer", "Interaction Designer"],
        "interest_tags": ["design", "creativity", "ui_ux"],
        "goal_tags": ["work_life_balance", "entrepreneurship"],
        "work_pref_tags": ["creative_work", "team_work"],
        "market": {
            "demand_level": "High", "demand_growth_pct": 18.0,
            "top_skills": ["Figma", "User Research", "Prototyping", "Design Thinking", "Accessibility"],
            "emerging_technologies": ["AI-assisted design", "Design systems", "Spatial computing", "Voice UI"],
            "job_openings_india": 35000,
            "top_companies": ["Flipkart", "Swiggy", "Meesho", "Razorpay", "Groww", "CRED", "Adobe"],
            "industry_trends": ["Design systems at scale", "AI design tools", "Inclusive design", "3D/AR interfaces"],
            "avg_salary_fresher": 4.5, "avg_salary_experienced": 16.0,
        },
        "exams": [
            {"name": "Google UX Design Certificate", "category": "Certification",
             "conducting_org": "Google / Coursera", "eligibility": "No prerequisites",
             "frequency": "Self-paced", "official_website": "https://coursera.org/professional-certificates/google-ux-design",
             "description": "7-course program covering the full UX design process."},
        ],
        "myths": [
            {"myth": "UI/UX designers just make things look pretty.", "reality": "UX design is deeply rooted in psychology, research, accessibility, and user behavior analysis."},
        ],
    },
    {
        "title": "Product Manager",
        "slug": "product-manager",
        "description": (
            "Product Managers define the vision, roadmap, and features of a product. "
            "They work at the intersection of business, technology, and user experience."
        ),
        "required_degree": "Any bachelor's degree; MBA is advantageous but not required",
        "required_skills": ["Product Strategy", "Data Analysis", "Communication", "Agile", "User Research", "SQL basics"],
        "optional_skills": ["A/B Testing", "SQL", "Figma", "OKR frameworks", "Go-to-Market"],
        "salary_beginner": 8.0, "salary_mid": 22.0, "salary_senior": 55.0,
        "career_growth": "High",
        "work_type": "Office/Hybrid",
        "industries": ["Technology", "Finance", "E-commerce", "SaaS", "EdTech"],
        "job_roles": ["Product Manager", "Associate PM", "Senior PM", "Group PM", "CPO"],
        "interest_tags": ["business", "management", "communication"],
        "goal_tags": ["high_salary", "entrepreneurship", "work_life_balance"],
        "work_pref_tags": ["creative_work", "team_work"],
        "market": {
            "demand_level": "High", "demand_growth_pct": 20.0,
            "top_skills": ["Product Thinking", "Data Analysis", "Communication", "Agile", "A/B Testing"],
            "emerging_technologies": ["AI Product Management", "No-code tools", "Product analytics"],
            "job_openings_india": 25000,
            "top_companies": ["Google", "Amazon", "Flipkart", "Swiggy", "Razorpay", "Freshworks", "Zoho"],
            "industry_trends": ["AI-native products", "PLG (Product-Led Growth)", "Data-driven roadmaps"],
            "avg_salary_fresher": 9.0, "avg_salary_experienced": 30.0,
        },
        "exams": [
            {"name": "Pragmatic Institute Product Certification", "category": "Certification",
             "conducting_org": "Pragmatic Institute", "eligibility": "No prerequisites",
             "frequency": "On-demand", "official_website": "https://pragmaticinstitute.com",
             "description": "Industry-recognized PM certification framework."},
        ],
        "myths": [
            {"myth": "PMs need to be able to code.", "reality": "While technical understanding helps, PMs don't write code. Communication, empathy, and analytical thinking are more critical."},
        ],
    },
    {
        "title": "Business Analyst",
        "slug": "business-analyst",
        "description": (
            "Business Analysts bridge the gap between business stakeholders and technical teams, "
            "translating business needs into technical requirements and driving data-informed decisions."
        ),
        "required_degree": "BBA, B.Tech, B.Sc or equivalent",
        "required_skills": ["SQL", "Excel", "Business Analysis", "Communication", "Data Visualization", "Process Mapping"],
        "optional_skills": ["Power BI", "Tableau", "Python", "JIRA", "Agile", "SAP"],
        "salary_beginner": 4.5, "salary_mid": 12.0, "salary_senior": 28.0,
        "career_growth": "Medium",
        "work_type": "Office/Hybrid",
        "industries": ["Consulting", "Banking", "IT Services", "Insurance", "Healthcare"],
        "job_roles": ["Business Analyst", "Systems Analyst", "Product Analyst", "IT Consultant"],
        "interest_tags": ["business", "data_analysis", "communication"],
        "goal_tags": ["job_stability", "work_life_balance"],
        "work_pref_tags": ["team_work", "office_work"],
        "market": {
            "demand_level": "High", "demand_growth_pct": 15.0,
            "top_skills": ["SQL", "Excel", "Process Analysis", "Stakeholder Management", "Documentation"],
            "emerging_technologies": ["AI-assisted requirements", "Digital transformation tools"],
            "job_openings_india": 60000,
            "top_companies": ["Accenture", "Deloitte", "KPMG", "Wipro", "TCS", "Cognizant", "Capgemini"],
            "industry_trends": ["Digital transformation", "Agile BA practices", "AI-driven business process automation"],
            "avg_salary_fresher": 5.0, "avg_salary_experienced": 16.0,
        },
        "exams": [
            {"name": "ECBA (Entry Certificate in Business Analysis)", "category": "Certification",
             "conducting_org": "IIBA", "eligibility": "No experience required",
             "frequency": "On-demand", "official_website": "https://iiba.org/career-resources/a-business-analysis-career-mentor/ecba/",
             "description": "Entry-level business analysis certification from IIBA."},
        ],
        "myths": [
            {"myth": "Business Analysts are just project documentation writers.", "reality": "BAs drive product strategy, stakeholder alignment, and measurable business outcomes — far beyond documentation."},
        ],
    },
    {
        "title": "Research Scientist",
        "slug": "research-scientist",
        "description": (
            "Research Scientists conduct original research to advance knowledge in AI, "
            "ML, computer science, or other technical domains. They publish papers and develop novel algorithms."
        ),
        "required_degree": "M.Tech / M.S. / Ph.D. in CS, Mathematics, or AI preferred",
        "required_skills": ["Python", "Mathematics", "Research Methodology", "Deep Learning", "Statistics", "Academic Writing"],
        "optional_skills": ["PyTorch", "Julia", "MATLAB", "LaTeX", "Experimental Design"],
        "salary_beginner": 8.0, "salary_mid": 22.0, "salary_senior": 60.0,
        "career_growth": "High",
        "work_type": "Research Lab / Remote",
        "industries": ["Academia", "AI Research Labs", "Healthcare", "Government", "Think Tanks"],
        "job_roles": ["Research Scientist", "AI Researcher", "Applied Scientist", "Research Engineer", "Professor"],
        "interest_tags": ["research", "mathematics", "programming"],
        "goal_tags": ["research", "international_career", "work_life_balance"],
        "work_pref_tags": ["research_oriented", "individual_work"],
        "market": {
            "demand_level": "High", "demand_growth_pct": 25.0,
            "top_skills": ["Deep Learning", "Python", "Statistics", "Research", "Publication Writing"],
            "emerging_technologies": ["Foundation Models", "Neuromorphic Computing", "Quantum ML"],
            "job_openings_india": 8000,
            "top_companies": ["Google DeepMind", "Microsoft Research", "IIT", "IISc", "TCS Research", "IBM Research"],
            "industry_trends": ["LLM research", "AI safety", "Multimodal AI", "Foundation models"],
            "avg_salary_fresher": 9.0, "avg_salary_experienced": 35.0,
        },
        "exams": [
            {"name": "CSIR NET (Computer Science)", "category": "Government Exam",
             "conducting_org": "CSIR", "eligibility": "M.Sc/M.Tech",
             "frequency": "Bi-Annual", "official_website": "https://csirhrdg.res.in",
             "description": "National eligibility test for research fellowships and lectureship."},
            {"name": "GATE CS", "category": "Government Exam",
             "conducting_org": "IITs / IISc", "eligibility": "B.Tech final year",
             "frequency": "Annual", "official_website": "https://gate.iitb.ac.in",
             "description": "Required for M.Tech admission and DRDO/BARC/ISRO jobs."},
        ],
        "myths": [
            {"myth": "Only PhD holders can be research scientists.", "reality": "Many industry research roles (Applied Scientist at Amazon, AI Researcher at Google) hire strong M.Tech graduates."},
        ],
    },
    {
        "title": "Data Engineer",
        "slug": "data-engineer",
        "description": (
            "Data Engineers design, construct, test, and maintain data architectures, pipelines, "
            "and large-scale processing systems to supply clean, reliable data for analytics and machine learning."
        ),
        "required_degree": "B.Tech / B.E. in CS, IT, or related technical field",
        "required_skills": ["SQL", "Python", "Data Warehousing", "ETL Pipelines", "Spark", "Data Modeling", "Linux"],
        "optional_skills": ["Kafka", "Airflow", "Snowflake", "dbt", "AWS/GCP", "Kubernetes"],
        "salary_beginner": 6.5, "salary_mid": 18.0, "salary_senior": 45.0,
        "career_growth": "Very High",
        "work_type": "Hybrid/Remote",
        "industries": ["Technology", "Finance", "Healthcare", "E-commerce", "Streaming Services"],
        "job_roles": ["Data Engineer", "Big Data Engineer", "Analytics Engineer", "Data Pipeline Architect"],
        "interest_tags": ["programming", "data_analysis", "cloud"],
        "goal_tags": ["high_salary", "job_stability", "international_career"],
        "work_pref_tags": ["individual_work", "practical_work"],
        "market": {
            "demand_level": "Very High", "demand_growth_pct": 30.0,
            "top_skills": ["SQL", "Python", "Spark", "Airflow", "Kafka"],
            "emerging_technologies": ["Data Lakehouse", "Real-time Streaming", "dbt", "Apache Iceberg"],
            "job_openings_india": 50000,
            "top_companies": ["Amazon", "Uber", "Walmart Labs", "Netflix", "Flipkart", "Accenture", "TCS"],
            "industry_trends": ["Modern Data Stack", "DataOps", "Real-time stream processing"],
            "avg_salary_fresher": 7.0, "avg_salary_experienced": 26.0,
        },
        "exams": [
            {"name": "Google Professional Data Engineer", "category": "Certification",
             "conducting_org": "Google Cloud", "eligibility": "3+ years data engineering experience",
             "frequency": "On-demand", "official_website": "https://cloud.google.com/certification/data-engineer",
             "description": "Validates ability to design and operationalize data processing systems."},
            {"name": "Databricks Certified Data Engineer Associate", "category": "Certification",
             "conducting_org": "Databricks", "eligibility": "Familiarity with Apache Spark & Python/SQL",
             "frequency": "On-demand", "official_website": "https://www.databricks.com/learn/certification",
             "description": "Certifies competence in Spark ETL and Lakehouse architecture."},
        ],
        "myths": [
            {"myth": "Data engineering is just writing SQL queries.", "reality": "Data engineers build distributed systems, manage streaming pipelines, optimize big data storage, and implement resilient CI/CD pipelines."},
        ],
    },
]

SCHOLARSHIPS_DATA = [
    {
        "name": "Prime Minister's Research Fellowship (PMRF)",
        "provider": "Ministry of Education, Government of India",
        "eligibility": "B.Tech/B.Sc graduates with 8.0+ CGPA joining PhD at IITs/IISc",
        "education_level": "Ph.D.",
        "application_period": "December – February (Annually)",
        "description": "Prestigious fellowship for doctoral research in science and technology. Provides ₹70,000-80,000/month stipend.",
        "official_website": "https://pmrf.in",
        "amount": "₹70,000 – ₹80,000/month",
    },
    {
        "name": "INSPIRE Scholarship (SHE)",
        "provider": "Department of Science and Technology, Government of India",
        "eligibility": "Students in top 1% in Class 12 pursuing B.Sc/B.Tech in natural or basic sciences",
        "education_level": "B.Sc / B.Tech",
        "application_period": "July – September (Annually)",
        "description": "Scholarship for Higher Education (SHE) to attract science students. ₹80,000/year for 5 years.",
        "official_website": "https://www.inspire-dst.gov.in",
        "amount": "₹80,000/year",
    },
    {
        "name": "Google Generation Scholarship (India)",
        "provider": "Google",
        "eligibility": "Students from underrepresented groups pursuing Computer Science",
        "education_level": "B.Tech / B.E.",
        "application_period": "October – December (Annually)",
        "description": "Google scholarship supporting diversity in technology. Includes mentorship and Google Summit invitation.",
        "official_website": "https://buildyourfuture.withgoogle.com/scholarships",
        "amount": "₹75,000 (approx.)",
    },
    {
        "name": "Aditya Birla Scholarships",
        "provider": "Aditya Birla Group",
        "eligibility": "Merit-based; students at IITs, NITs, BITS, IIMs",
        "education_level": "B.Tech / MBA",
        "application_period": "August – September (Annually)",
        "description": "Merit scholarship covering tuition fees for top students. Includes networking opportunities with ABG leadership.",
        "official_website": "https://adityabirlascholars.net",
        "amount": "Up to ₹65,000/year",
    },
    {
        "name": "Tata Trusts Scholarships",
        "provider": "Tata Trusts",
        "eligibility": "Financially needy students pursuing professional courses",
        "education_level": "B.Tech / MBBS / Law / CA",
        "application_period": "April – July (Varies by program)",
        "description": "Need-based scholarships from Tata Trusts for students from economically weaker sections pursuing professional degrees.",
        "official_website": "https://www.tatatrusts.org/article/apply/scholarships",
        "amount": "Varies (₹30,000 – ₹2,00,000/year)",
    },
    {
        "name": "HDFC Bank Parivartan's ECS Scholarship",
        "provider": "HDFC Bank Ltd",
        "eligibility": "Students from families with annual income < ₹2.5 lakhs",
        "education_level": "Diploma / B.Tech / B.Sc",
        "application_period": "July – October (Annually)",
        "description": "Educational support scholarship for meritorious students from economically weaker backgrounds.",
        "official_website": "https://www.hdfcbank.com/content/bbp/repositories/723fb80a-2dde-42a3-9793-7ae1be57c87f/?folderPath=/Common/CSR/2023/Scholarship",
        "amount": "Up to ₹75,000/year",
    },
    {
        "name": "Kishore Vaigyanik Protsahan Yojana (KVPY)",
        "provider": "Department of Science and Technology, Government of India",
        "eligibility": "Students in Class 11, 12, and 1st year B.Sc/B.S. pursuing basic sciences",
        "education_level": "Class 11-12 / B.Sc 1st Year",
        "application_period": "July – September (Annually)",
        "description": "Fellowship for students interested in pursuing research careers in basic sciences.",
        "official_website": "https://kvpy.iisc.ac.in",
        "amount": "₹5,000 – ₹7,000/month + Annual Contingency Grant",
    },
]

GENERAL_MYTHS_DATA = [
    {
        "myth": "Tech careers are only for men.",
        "reality": "The tech industry is actively working towards gender diversity. Organizations like Women Who Code, AnitaB.org, and many companies have specific initiatives to support women in technology.",
        "category": "General",
    },
    {
        "myth": "You need to be from an IIT/NIT to get a good tech job.",
        "reality": "While premium colleges help, companies like Google, Amazon, and startups hire from all colleges based on skills, projects, and interview performance. A strong GitHub portfolio beats college pedigree.",
        "category": "General",
    },
    {
        "myth": "AI will take away all software jobs.",
        "reality": "AI is creating more software jobs than it eliminates. New roles like AI Engineer, Prompt Engineer, and MLOps are emerging. Developers who use AI tools become significantly more productive.",
        "category": "General",
    },
    {
        "myth": "You must know everything before applying for a job.",
        "reality": "Companies hire based on problem-solving ability and learning potential. Nobody knows everything — continuous learning is a core part of every tech career.",
        "category": "General",
    },
    {
        "myth": "High salary careers require a postgraduate degree.",
        "reality": "Many high-paying roles (SDE at Google, ML Engineer at a startup) hire freshers with a B.Tech. Skills and projects matter far more than the degree level for industry roles.",
        "category": "General",
    },
    {
        "myth": "Career switches in tech are nearly impossible.",
        "reality": "Tech allows relatively smooth career transitions. Many data scientists started as software engineers; many PMs started as developers. Skills transfer between adjacent domains.",
        "category": "General",
    },
]


def seed_careers(db: Session) -> None:
    """Seed all career data if the careers table is empty."""
    if db.query(Career).count() > 0:
        logger.info("[CareerService] Careers already seeded. Skipping.")
        return

    logger.info("[CareerService] Seeding career data...")

    for c_data in CAREERS_DATA:
        market_data = c_data.pop("market", {})
        exams_data = c_data.pop("exams", [])
        myths_data = c_data.pop("myths", [])

        career = Career(**c_data)
        db.add(career)
        db.flush()  # get the ID

        # Market info
        if market_data:
            market = MarketInfo(career_id=career.id, **market_data)
            db.add(market)

        # Exams
        for e in exams_data:
            exam = Exam(career_id=career.id, **e)
            db.add(exam)

        # Career-specific myths
        for m in myths_data:
            myth = CareerMyth(career_id=career.id, **m, category=career.title)
            db.add(myth)

    # General myths (not tied to specific career)
    for m in GENERAL_MYTHS_DATA:
        myth = CareerMyth(career_id=None, **m)
        db.add(myth)

    # Scholarships
    for s in SCHOLARSHIPS_DATA:
        scholarship = Scholarship(**s)
        db.add(scholarship)

    db.commit()
    logger.info(f"[CareerService] Seeded {len(CAREERS_DATA)} careers, {len(SCHOLARSHIPS_DATA)} scholarships, {len(GENERAL_MYTHS_DATA)} general myths.")
