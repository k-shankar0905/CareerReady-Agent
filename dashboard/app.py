import os
import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dotenv import load_dotenv
import requests

# Load environment variables from a .env file if it exists
load_dotenv()

# Resolve directories relative to this file to allow running the app from any location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB_RESULTS_PATH = os.path.join(BASE_DIR, "job_results.json")
SKILLS_ANALYSIS_PATH = os.path.join(BASE_DIR, "skills_analysis.json")
GAP_ANALYSIS_PATH = os.path.join(BASE_DIR, "gap_analysis.json")
ROADMAP_PATH = os.path.join(BASE_DIR, "career_roadmap.json")
RESUME_PATH = os.path.join(BASE_DIR, "generated_resume.md")


def apply_custom_css():
    """
    Injects custom HTML and CSS styles into the Streamlit app to create a
    premium, dark-themed, glassmorphic UI. This overrides standard Streamlit
    styling for headings, buttons, badges, metrics, and cards.
    """
    st.markdown(
        """
        <style>
        /* Import Google Font Inter for a modern look */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Apply fonts globally */
        html, body, [class*="css"], .stApp {
            font-family: 'Inter', sans-serif;
            background-color: #0F0F1A;
            color: #FFFFFF;
        }

        /* Glassmorphic Container/Card Styling */
        .glass-card {
            background: rgba(30, 30, 47, 0.65);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        
        .glass-card:hover {
            border-color: rgba(108, 99, 255, 0.3);
            transform: translateY(-2px);
        }

        /* Title with Glowing Effect */
        .glow-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #A78BFA, #6C63FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(108, 99, 255, 0.25);
            margin-bottom: 8px;
            margin-top: 10px;
        }
        
        .glow-subtitle {
            font-size: 1.1rem;
            color: #A0A0B0;
            margin-bottom: 30px;
            font-weight: 300;
        }

        /* Metric widget styling */
        .readiness-container {
            text-align: center;
            padding: 20px;
            border-radius: 50%;
            width: 140px;
            height: 140px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            margin: 0 auto 10px auto;
            background: radial-gradient(circle, rgba(30, 30, 47, 1) 0%, rgba(15, 15, 26, 1) 100%);
            border: 4px solid #10B981;
            box-shadow: 0 0 25px rgba(16, 185, 129, 0.35);
        }

        .readiness-val {
            font-size: 42px;
            font-weight: 800;
            color: #10B981;
            line-height: 1;
        }

        .readiness-lbl {
            font-size: 10px;
            color: #A0A0B0;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 4px;
        }

        /* Custom Tags/Badges */
        .badge-match {
            background-color: rgba(16, 185, 129, 0.12);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.25);
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
            margin: 6px 4px;
            font-size: 0.85rem;
        }

        .badge-gap {
            background-color: rgba(239, 68, 68, 0.12);
            color: #EF4444;
            border: 1px solid rgba(239, 68, 68, 0.25);
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
            margin: 6px 4px;
            font-size: 0.85rem;
        }

        .badge-trend {
            background-color: rgba(108, 99, 255, 0.12);
            color: #A78BFA;
            border: 1px solid rgba(108, 99, 255, 0.25);
            padding: 6px 12px;
            border-radius: 12px;
            font-weight: 500;
            display: inline-block;
            margin: 4px;
            font-size: 0.8rem;
        }

        /* Action/Success message styling */
        .market-pulse-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #A78BFA;
            margin-top: 15px;
            margin-bottom: 10px;
            border-left: 3px solid #6C63FF;
            padding-left: 10px;
        }

        /* Custom roadmaps timeline card layout */
        .timeline-card {
            background: rgba(30, 30, 47, 0.45);
            border-left: 4px solid #6C63FF;
            padding: 16px;
            border-radius: 0 12px 12px 0;
            margin-bottom: 16px;
        }
        
        .timeline-header {
            font-weight: 700;
            color: #6C63FF;
            margin-bottom: 4px;
            font-size: 1rem;
            text-transform: uppercase;
        }

        .timeline-topic {
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 8px;
            color: #FFFFFF;
        }

        /* Nice welcome container styling */
        .welcome-container {
            text-align: center;
            padding: 50px 20px;
            margin-top: 20px;
        }
        
        .feature-card {
            background: rgba(30, 30, 47, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            height: 100%;
        }

        .feature-icon {
            font-size: 2.2rem;
            color: #6C63FF;
            margin-bottom: 12px;
        }

        .feature-title {
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 8px;
        }

        .feature-text {
            color: #A0A0B0;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def load_data():
    """
    Attempts to read data from the local JSON and Markdown files.
    
    Returns:
        dict: A dictionary containing 'jobs', 'skills', 'gap', 'roadmap', and 'resume' data,
              or None if any required file is missing or contains invalid data.
    """
    try:
        # Check if all key files exist
        if not (os.path.exists(JOB_RESULTS_PATH) and
                os.path.exists(SKILLS_ANALYSIS_PATH) and
                os.path.exists(GAP_ANALYSIS_PATH) and
                os.path.exists(ROADMAP_PATH)):
            return None

        # Read job scraper results
        with open(JOB_RESULTS_PATH, "r", encoding="utf-8") as f:
            jobs = json.load(f)

        # Read market skills analysis
        with open(SKILLS_ANALYSIS_PATH, "r", encoding="utf-8") as f:
            skills = json.load(f)

        # Read gap analysis
        with open(GAP_ANALYSIS_PATH, "r", encoding="utf-8") as f:
            gap = json.load(f)

        # Read week-by-week career roadmap
        with open(ROADMAP_PATH, "r", encoding="utf-8") as f:
            roadmap = json.load(f)

        # Read resume markdown text (optional file, handle gracefully if missing)
        resume_md = ""
        if os.path.exists(RESUME_PATH):
            with open(RESUME_PATH, "r", encoding="utf-8") as f:
                resume_md = f.read()

        return {
            "jobs": jobs,
            "skills": skills,
            "gap": gap,
            "roadmap": roadmap,
            "resume": resume_md
        }
    except Exception as e:
        st.error(f"Error reading JSON files: {str(e)}")
        return None


def generate_mock_data(job_role: str, current_skills_str: str):
    """
    Generates high-quality mock data dynamically for the entered job role
    and user skills. This serves as the local backup when no Gemini API
    key is available, ensuring a clean and interactive demo.
    
    Args:
        job_role (str): Target job role entered by the user.
        current_skills_str (str): Comma-separated current skills.
    """
    # Normalize user inputs
    role_clean = job_role.strip()
    role_lower = role_clean.lower()
    
    # Standardize skills list
    user_skills = [s.strip() for s in current_skills_str.split(",") if s.strip()]
    user_skills_lower = [s.lower() for s in user_skills]
    
    # 1. Define typical market profiles for popular domains
    profiles = {
        "data analyst": {
            "skills": {"SQL": 95, "Python": 85, "Excel": 80, "Tableau": 75, "Power BI": 70, "Data Modeling": 65, "Statistics": 60, "ETL": 55},
            "trending": [{"skill": "dbt", "trend": "up"}, {"skill": "Snowflake", "trend": "up"}, {"skill": "Python (Pandas)", "trend": "stable"}],
            "roadmap_topics": [
                ("Advanced SQL & Query Optimization", "Master window functions, Common Table Expressions (CTEs), and query tuning for analytical reporting.", ["LeetCode SQL Study Plan", "Mode Analytics SQL Tutorial"]),
                ("Python Data Wrangling (Pandas/NumPy)", "Learn data cleaning, data profiling, aggregation, and preprocessing using pandas.", ["Kaggle Pandas Course", "Pandas Documentation"]),
                ("Dashboard Design & BI Tools (Tableau/Power BI)", "Build interactive dashboards following data visualization and visual storytelling principles.", ["Tableau Public Academy", "Microsoft Power BI Learning Path"]),
                ("Data Warehousing & ETL Basics", "Understand dimensional modeling, star schemas, and basic ETL pipeline orchestration.", ["The Data Warehouse Toolkit (Book)", "dbt Fundamentals Course"])
            ]
        },
        "software engineer": {
            "skills": {"Python": 90, "JavaScript": 85, "Git & GitHub": 88, "Data Structures": 95, "Docker": 75, "SQL": 70, "System Design": 80, "CI/CD": 65},
            "trending": [{"skill": "TypeScript", "trend": "up"}, {"skill": "Kubernetes", "trend": "up"}, {"skill": "Rust", "trend": "up"}],
            "roadmap_topics": [
                ("Algorithms & Data Structures", "Focus on time/space complexity (Big O), trees, graphs, and dynamic programming.", ["LeetCode Top 75", "NeetCode.io Roadmap"]),
                ("Object-Oriented Programming & Web Frameworks", "Build robust backend microservices using FastAPI, Django, or Express.", ["FastAPI Official Tutorial", "RealPython Backend Guides"]),
                ("Git Workflows, Code Testing & CI/CD", "Learn advanced branching strategies, unit testing with PyTest, and automated pipelines.", ["Git Pro Book", "GitHub Actions Learning Center"]),
                ("System Design & Scale", "Study load balancers, caching strategies, database sharding, and message queues.", ["Grokking System Design", "ByteByteGo YouTube Channel"])
            ]
        },
        "data scientist": {
            "skills": {"Python": 95, "Machine Learning": 90, "Statistics": 88, "SQL": 80, "Deep Learning": 75, "Data Visualization": 70, "Big Data (Spark)": 60, "Model Deployment": 55},
            "trending": [{"skill": "PyTorch", "trend": "up"}, {"skill": "LLMs & RAG", "trend": "up"}, {"skill": "MLflow", "trend": "up"}],
            "roadmap_topics": [
                ("Statistical Analysis & EDA", "Focus on probability distributions, hypothesis testing, A/B test styling, and exploratory data analysis.", ["OpenIntro Statistics", "Towards Data Science EDA Guides"]),
                ("Supervised & Unsupervised ML", "Master classification, regression, clustering, and tree-based ensemble models using Scikit-Learn.", ["ISLR Book", "Scikit-Learn Official User Guide"]),
                ("Deep Learning & LLM Foundations", "Build neural networks using PyTorch/TensorFlow and explore fine-tuning techniques.", ["Fast.ai Deep Learning Course", "Hugging Face Course"]),
                ("MLOps & Production Deployments", "Learn to containerize models and deploy them as APIs with monitoring.", ["Made With ML", "Coursera MLOps Specialization"])
            ]
        },
        "product manager": {
            "skills": {"Agile/Scrum": 92, "Product Roadmap": 90, "User Research": 85, "SQL & Analytics": 70, "A/B Testing": 75, "Jira": 80, "Stakeholder Management": 88, "Market Analysis": 65},
            "trending": [{"skill": "AI Strategy", "trend": "up"}, {"skill": "Product-Led Growth", "trend": "up"}, {"skill": "Figma Prototypes", "trend": "stable"}],
            "roadmap_topics": [
                ("Product Strategy & Vision", "Develop core market research frameworks, competitor analysis, and customer personas.", ["Inspired by Marty Cagan", "Product School Resources"]),
                ("Agile Product Management & Writing PRDs", "Learn to draft comprehensive Product Requirement Documents and run agile rituals.", ["Atlassian Agile Guide", "PRD Templates on Product Hunt"]),
                ("Product Analytics & A/B Testing", "Track retention metrics, define North Star KPIs, and run statistically sound experiments.", ["Amplitude Analytics Academy", "Optimizely A/B Testing Guide"]),
                ("UX Principles & Prototyping", "Collaborate effectively with design teams and build simple wireframes.", ["Figma for Beginners", "Interaction Design Foundation"])
            ]
        }
    }

    # Match predefined profile, or generate dynamically for unknown roles
    target_profile = None
    for key, profile in profiles.items():
        if key in role_lower:
            target_profile = profile
            break
            
    if not target_profile:
        # Dynamic profile generation logic for custom/unknown roles
        default_skills = ["Python", "SQL", "Git & GitHub", "Cloud Computing (AWS)", "System Architecture", "Data Analysis", "API Development", "Agile Methodologies"]
        market_demand_pct = [90, 85, 80, 75, 70, 65, 60, 55]
        
        # Build skills map
        skills_map = {}
        for s, pct in zip(default_skills, market_demand_pct):
            skills_map[s] = pct
            
        target_profile = {
            "skills": skills_map,
            "trending": [{"skill": "Generative AI", "trend": "up"}, {"skill": "Serverless Architecture", "trend": "up"}, {"skill": "Docker", "trend": "stable"}],
            "roadmap_topics": [
                (f"Core {role_clean} Fundamentals", f"Establish foundational concepts and tools standard in modern {role_clean} roles.", ["Udemy Foundation Course", "Google Technical Documentation"]),
                ("Version Control & Database Integration", "Learn Git workflows and relational database modeling.", ["Git Book", "W3Schools SQL Tutorial"]),
                ("Cloud Architecture & Orchestration", "Understand cloud resource management, server deployment, and virtualization.", ["AWS Cloud Practitioner Guide", "Docker Labs"]),
                ("Agile Practices & CI/CD Pipelines", "Master sprint planning, issue tracking, and setting up automated testing pipelines.", ["Atlassian Jira Guide", "GitHub Actions Quickstart"])
            ]
        }

    market_skills_dict = target_profile["skills"]
    trending_skills = target_profile["trending"]
    
    # 2. Perform Gap Analysis
    matching_skills = []
    missing_skills = []
    
    for skill, pct in market_skills_dict.items():
        # Match if the skill keyword exists in user's inputs
        is_matched = False
        for u_skill in user_skills_lower:
            if u_skill in skill.lower() or skill.lower() in u_skill:
                is_matched = True
                break
        
        if is_matched:
            matching_skills.append(skill)
        else:
            missing_skills.append(skill)

    # Compute readiness score based on matched percentage weights
    total_weight = sum(market_skills_dict.values())
    matched_weight = sum([market_skills_dict[s] for s in matching_skills])
    
    if total_weight > 0:
        readiness_score = int((matched_weight / total_weight) * 100)
    else:
        readiness_score = 0
        
    # Bound the score between a realistic 30% baseline (if they have at least one skill) and 100%
    if len(matching_skills) > 0:
        readiness_score = max(30, readiness_score)
    else:
        readiness_score = max(5, readiness_score)
    readiness_score = min(100, readiness_score)

    # 3. Create Career Roadmap
    weeks_roadmap = []
    # If the user has missing skills, assign them to weeks. Otherwise assign enhancement topics.
    topics_to_use = target_profile["roadmap_topics"]
    
    for i, (topic, details, resources) in enumerate(topics_to_use):
        weeks_roadmap.append({
            "week": i + 1,
            "topic": topic,
            "details": details,
            "resources": resources
        })

    # 4. Generate Job Results
    mock_companies = ["NovaTech Solutions", "Apex Systems", "Vertex AI", "Quant Dynamics", "Stellar Softwares", "Enterprise Partners", "CoreData Corp", "SyncLabs", "CloudPillar", "NexGen Digital"]
    mock_locations = ["San Francisco, CA (Hybrid)", "New York, NY (Onsite)", "Austin, TX (Remote)", "Chicago, IL (Hybrid)", "Seattle, WA (Remote)", "Remote (US)", "London, UK (Hybrid)", "Boston, MA (Onsite)", "Austin, TX (Onsite)", "Denver, CO (Remote)"]
    
    jobs = []
    for i in range(10):
        jobs.append({
            "job_id": f"mock_job_{i+1}",
            "title": f"Senior {role_clean}" if i % 3 == 0 else (f"Associate {role_clean}" if i % 2 == 0 else f"{role_clean}"),
            "company": mock_companies[i],
            "location": mock_locations[i],
            "description": (
                f"We are seeking an enthusiastic {role_clean} to join our growing team. "
                f"In this role, you will apply core skills in {', '.join(list(market_skills_dict.keys())[:4])} "
                "to solve challenging projects, collaborate with cross-functional partners, "
                "and deploy production-ready solutions.\n\n"
                "Key Responsibilities:\n"
                f"- Architect data-driven/software tools centered on {role_clean} objectives.\n"
                f"- Leverage tools like {', '.join(matching_skills + ['Git'])} to support key objectives.\n"
                "- Write clean code, generate comprehensive documentations, and present key indicators to stakeholders.\n\n"
                "Requirements:\n"
                "- Bachelor's degree in CS, Data Science, Math, or equivalent field experience.\n"
                f"- Solid expertise in: {', '.join(list(market_skills_dict.keys())[:5])}.\n"
                "- Strong analytical background and clear verbal/written communicator."
            )
        })

    # 5. Generate tailored Resume Markdown
    resume_md = f"""# {role_clean.upper()} CANDIDATE
City, State | email@example.com | (555) 019-2834 | github.com/candidate

---

## PROFESSIONAL SUMMARY
Results-driven professional transitioning into a **{role_clean}** role. Equipped with foundational skills in {", ".join(matching_skills) if matching_skills else "software development"}. Demonstrated capacity for quantitative problem solving, technical analysis, and rapid skill acquisition. Committed to bridging the current skill gaps in {", ".join(missing_skills[:3])} to deliver high-quality, scalable contributions in team environments.

---

## TECHNICAL SKILLS
* **Core Proficiencies (Matching)**: {", ".join(matching_skills) if matching_skills else "None listed"}
* **In-Progress Learning Goals**: {", ".join(missing_skills) if missing_skills else "None listed"}
* **Developer Tools & Workflows**: Git, GitHub, VS Code, Agile/Scrum methodologies

---

## PROFESSIONAL EXPERIENCE
**Technical Associate** | *Alpha Tech Systems* | 2024 - Present
* Spearheaded data reporting processes, cutting manual data collation efforts by 20%.
* Utilized {matching_skills[0] if matching_skills else "database queries"} to produce visual summaries for corporate leaders.
* Collaborative partner in agile sprints, participating in daily standups and tracking work items.

**Analyst / Intern** | *Beta Global Analytics* | 2023 - 2024
* Researched industry benchmarks and organized data sheets to support project decisions.
* Automated file conversions using basic scripts, increasing team operating efficiency.

---

## PROJECTS
**Domain-Specific Optimization Tool**
* Designed an open-source application to automate analysis and generate domain visualizer graphs.
* Leveraged key data processes, version-controlled repository on GitHub, and documented operational procedures.

**Personal Project Portfolio**
* Built a custom dashboard using python showcasing analytics summaries.
* Integrated CSV data parsing modules and deployed it as a local testing site.

---

## EDUCATION
* **B.S. in Applied Sciences / Business Administration** | State University, 2023
* **CareerReady Professional Certifications**: {", ".join(matching_skills)} (In Progress: {", ".join(missing_skills[:2])})
"""

    # 6. Structure output & save files
    skills_analysis = {
        "job_role": role_clean,
        "market_skills": [{"skill": k, "demand_percentage": v} for k, v in market_skills_dict.items()],
        "trending_skills": trending_skills
    }
    
    gap_analysis = {
        "readiness_score": readiness_score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills
    }
    
    career_roadmap = {
        "weeks": weeks_roadmap
    }

    # Write files to root folder
    with open(JOB_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=4, ensure_ascii=False)
        
    with open(SKILLS_ANALYSIS_PATH, "w", encoding="utf-8") as f:
        json.dump(skills_analysis, f, indent=4, ensure_ascii=False)
        
    with open(GAP_ANALYSIS_PATH, "w", encoding="utf-8") as f:
        json.dump(gap_analysis, f, indent=4, ensure_ascii=False)
        
    with open(ROADMAP_PATH, "w", encoding="utf-8") as f:
        json.dump(career_roadmap, f, indent=4, ensure_ascii=False)
        
    with open(RESUME_PATH, "w", encoding="utf-8") as f:
        f.write(resume_md)


def generate_llm_data(job_role: str, current_skills_str: str, api_key: str) -> bool:
    """
    Calls the Google Gemini API directly via REST to generate custom analysis
    data based on the target job role and user's skills. If the call succeeds,
    it saves the structures to local JSON and Markdown files.
    
    Args:
        job_role (str): Target job role.
        current_skills_str (str): Comma-separated list of skills.
        api_key (str): Gemini API Key.
        
    Returns:
        bool: True if generation succeeded, False otherwise (falls back to mock).
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    You are an expert career advisor and technical recruiter.
    Analyze the career path for someone wanting to become a '{job_role}' who currently possesses these skills: '{current_skills_str}'.
    
    You must output a single, valid JSON object with the following structure (do NOT include markdown code blocks like ```json or any other text outside the JSON):
    {{
      "jobs": [
        {{
          "job_id": "job_1",
          "title": "Job Title (e.g. Junior/Senior {job_role})",
          "company": "Realistic Company Name",
          "location": "City, State or Remote",
          "description": "Short, realistic job description containing duties and required skills."
        }},
        ... (generate exactly 5 realistic job postings)
      ],
      "skills_analysis": {{
        "job_role": "{job_role}",
        "market_skills": [
          {{"skill": "SkillName1", "demand_percentage": 95}},
          {{"skill": "SkillName2", "demand_percentage": 85}}
          // (generate exactly 6-8 key market skills for this role, with demand percentages)
        ],
        "trending_skills": [
          {{"skill": "TrendingSkill1", "trend": "up"}},
          {{"skill": "TrendingSkill2", "trend": "stable"}}
          // (generate exactly 3-4 trending tools/skills in this domain)
        ]
      }},
      "gap_analysis": {{
        "readiness_score": 65,  // An integer score from 0 to 100 based on how well the current skills match the market demand
        "matching_skills": ["SkillA", "SkillB"], // List of skills the user has that match the market skills
        "missing_skills": ["SkillC", "SkillD"] // List of market skills the user is missing
      }},
      "career_roadmap": {{
        "weeks": [
          {{
            "week": 1,
            "topic": "Week 1 Learning Topic",
            "details": "Specific tasks, concepts, and technologies to study this week.",
            "resources": ["Resource Name/Link 1", "Resource Name/Link 2"]
          }},
          ... (generate a week-by-week learning roadmap for exactly 4 weeks to bridge the gap)
        ]
      }},
      "resume": "A professional Markdown-formatted resume optimized for the target job role. Categorize the skills section into 'Core Proficiencies' (user's matching skills) and 'In-Progress Learning Goals' (missing skills). Include placeholders for contact details, a brief summary, realistic work experience templates, and projects."
    }}
    """
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        response.raise_for_status()
        res_data = response.json()
        
        # Extract text response from Gemini output structure
        content_text = res_data["contents"][0]["parts"][0]["text"]
        data = json.loads(content_text.strip())
        
        # Save output data to the respective JSON and Markdown files
        with open(JOB_RESULTS_PATH, "w", encoding="utf-8") as f:
            json.dump(data["jobs"], f, indent=4, ensure_ascii=False)
            
        with open(SKILLS_ANALYSIS_PATH, "w", encoding="utf-8") as f:
            json.dump(data["skills_analysis"], f, indent=4, ensure_ascii=False)
            
        with open(GAP_ANALYSIS_PATH, "w", encoding="utf-8") as f:
            json.dump(data["gap_analysis"], f, indent=4, ensure_ascii=False)
            
        with open(ROADMAP_PATH, "w", encoding="utf-8") as f:
            json.dump(data["career_roadmap"], f, indent=4, ensure_ascii=False)
            
        with open(RESUME_PATH, "w", encoding="utf-8") as f:
            f.write(data["resume"])
            
        return True
    except Exception as e:
        # Gracefully handle exceptions, show warnings, and return False to trigger fallback
        st.sidebar.warning(f"Gemini API request failed: {str(e)}. Falling back to local demo generator.")
        return False


def main():
    """
    Main entry point for the Streamlit Dashboard. Coordinates theme setups,
    sidebars, data generation execution, welcome screen, and results rendering.
    """
    # 1. Setup Streamlit page defaults
    st.set_page_config(
        page_title="CareerReady AI Dashboard",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply CSS for dark mode and premium look
    apply_custom_css()

    # Get API keys from environment
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    has_api = bool(gemini_key and "your_gemini" not in gemini_key and gemini_key.strip() != "")

    # 2. Sidebar Configuration
    st.sidebar.markdown(
        """
        <div style='text-align: center; margin-bottom: 20px;'>
            <h2 style='margin-bottom: 0px; color: #6C63FF; font-weight: 700;'>🎯 CareerReady</h2>
            <p style='color: #A0A0B0; font-size: 0.85rem; margin-top: 4px;'>Agentic Talent Pipeline</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Configure Target Role")
    
    # Input box for job role
    job_role_input = st.sidebar.text_input(
        "Job Role",
        value="",
        placeholder="e.g. Data Analyst",
        help="Enter the exact job title you are aiming to transition into."
    )
    
    # Input box for current skills
    current_skills_input = st.sidebar.text_area(
        "Your Current Skills",
        value="",
        placeholder="e.g. SQL, Excel, Communication",
        help="List your current skills separated by commas."
    )
    
    # Active mode indicators
    st.sidebar.markdown("---")
    if has_api:
        st.sidebar.markdown(
            """
            <div style='background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 10px; margin-bottom: 20px;'>
                <span style='color: #10B981; font-weight: 600;'>🟢 Gemini AI Mode Active</span><br/>
                <span style='color: #A0A0B0; font-size: 0.75rem;'>Full LLM analysis enabled.</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.sidebar.markdown(
            """
            <div style='background-color: rgba(108, 99, 255, 0.1); border: 1px solid rgba(108, 99, 255, 0.3); border-radius: 8px; padding: 10px; margin-bottom: 20px;'>
                <span style='color: #A78BFA; font-weight: 600;'>🔵 Demo Mode Active</span><br/>
                <span style='color: #A0A0B0; font-size: 0.75rem;'>Using rules engine for local datasets.</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    submit_button = st.sidebar.button(
        "Analyze Career Path",
        use_container_width=True,
        type="primary"
    )

    # 3. Form submission execution
    if submit_button:
        if not job_role_input:
            st.sidebar.error("Please enter a target Job Role.")
        else:
            with st.spinner("Executing agentic gap analysis and generating roadmap..."):
                success = False
                if has_api:
                    # Run LLM-driven generation
                    success = generate_llm_data(job_role_input, current_skills_input, gemini_key)
                
                # Fallback to local rule-based generation if LLM failed or API key was missing
                if not success:
                    generate_mock_data(job_role_input, current_skills_input)
                    
            st.sidebar.success("Analysis generated successfully!")
            # Force streamlit to reload and read the new local JSON files
            st.rerun()

    # 4. Main Panel Layout
    # Attempt to load data from JSON files
    data = load_data()

    if data is None:
        # Welcome screen state (Render if files don't exist yet)
        st.markdown("<div class='glow-title' style='text-align: center;'>CareerReady AI</div>", unsafe_allow_html=True)
        st.markdown("<div class='glow-subtitle' style='text-align: center;'>AI-Powered Competency Mapping & Career Roadmap Dashboard</div>", unsafe_allow_html=True)
        
        st.markdown(
            """
            <div class='glass-card' style='text-align: center; max-width: 800px; margin: 0 auto 40px auto; padding: 40px 20px;'>
                <h3 style='color: #6C63FF; font-weight: 600; margin-bottom: 12px;'>No active profile loaded</h3>
                <p style='color: #A0A0B0; font-size: 1.1rem; margin-bottom: 24px;'>
                    Provide your target job role and current skill competencies in the sidebar configuration to execute the agent analysis.
                </p>
                <div style='display: inline-block; animation: pulse 2s infinite;'>
                    <span style='font-size: 2.5rem;'>⬅️</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### Core Platform Pillars")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                """
                <div class='feature-card'>
                    <div class='feature-icon'>📊</div>
                    <div class='feature-title'>Market Scraping & Pulse</div>
                    <div class='feature-text'>Extract real-time core skill expectations directly from job boards.</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                """
                <div class='feature-card'>
                    <div class='feature-icon'>⚡</div>
                    <div class='feature-title'>Competency & Gap Analysis</div>
                    <div class='feature-text'>Instantly check missing proficiencies and receive your career readiness rating.</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                """
                <div class='feature-card'>
                    <div class='feature-icon'>🗺️</div>
                    <div class='feature-title'>Syllabus Roadmap & Resume</div>
                    <div class='feature-text'>Gain a structured weekly learning schedule and acquire a tailored resume.</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        # Results display state
        role_title = data["skills"].get("job_role", "Target Role")
        st.markdown(f"<div class='glow-title'>🎯 CareerReady — {role_title} Analysis</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='glow-subtitle'>Interactive Competency Model & Readiness Insights</div>", unsafe_allow_html=True)

        # 5. Core Metric KPI Header
        kpi_col1, kpi_col2, kpi_col3 = st.columns([1, 2, 1])
        readiness_score = data["gap"].get("readiness_score", 0)
        
        with kpi_col1:
            # Display score in custom styled gauge circle
            st.markdown(
                f"""
                <div class='readiness-container'>
                    <div class='readiness-val'>{readiness_score}%</div>
                    <div class='readiness-lbl'>Readiness</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with kpi_col2:
            # Display matching and missing stats
            num_match = len(data["gap"].get("matching_skills", []))
            num_missing = len(data["gap"].get("missing_skills", []))
            total_skills = num_match + num_missing
            
            # Map description matches
            if readiness_score >= 80:
                match_status = "Excellent Fit"
                status_color = "#10B981"
                status_desc = "You match the vast majority of market requirements! Consider applying for active roles immediately."
            elif readiness_score >= 50:
                match_status = "Moderate Fit"
                status_color = "#F59E0B"
                status_desc = "You have standard core capabilities but need to acquire key technical proficiencies to stand out."
            else:
                match_status = "Emerging Fit"
                status_color = "#EF4444"
                status_desc = "You are starting your transition. Focus heavily on the week-by-week learning roadmap."
                
            st.markdown(
                f"""
                <div style='margin-top: 15px;'>
                    <h3 style='margin: 0px;'>Fit Assessment: <span style='color: {status_color}; font-weight: 700;'>{match_status}</span></h3>
                    <p style='color: #A0A0B0; font-size: 0.95rem; margin-top: 6px;'>{status_desc}</p>
                    <div style='margin-top: 12px; color: #E0E0E0;'>
                        <b>Skill Match Ratio:</b> {num_match} out of {total_skills} top proficiencies identified.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with kpi_col3:
            # Display job listings count
            num_jobs = len(data["jobs"])
            st.markdown(
                f"""
                <div style='text-align: center; border: 1px solid rgba(255,255,255,0.06); background: rgba(30, 30, 47, 0.4); border-radius: 12px; padding: 20px; height: 100%; display: flex; flex-direction: column; justify-content: center;'>
                    <span style='font-size: 2.2rem;'>💼</span>
                    <span style='font-size: 1.5rem; font-weight: 700; color: #6C63FF; margin-top: 4px;'>{num_jobs} Jobs</span>
                    <span style='color: #A0A0B0; font-size: 0.8rem;'>Analyzed from Market</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br/>", unsafe_allow_html=True)

        # 6. Tab Section Structure
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Market Demand & Pulse",
            "🔴 Skill Gap Profiles",
            "🗺️ Weekly Learning Roadmap",
            "📄 Optimized Resume",
            "💼 Scraped Job Postings"
        ])

        # TAB 1: Market Demand Plotly Chart
        with tab1:
            col_chart, col_pulse = st.columns([3, 2])
            
            with col_chart:
                st.subheader("Competency Distribution in Job Openings")
                
                # Format skills data for Plotly
                skills_list = data["skills"].get("market_skills", [])
                if skills_list:
                    df = pd.DataFrame(skills_list)
                    df = df.sort_values(by="demand_percentage", ascending=True)
                    
                    # Create custom colored Plotly Horizontal Bar Chart
                    fig = px.bar(
                        df,
                        x="demand_percentage",
                        y="skill",
                        orientation='h',
                        labels={"demand_percentage": "Market Demand Frequency (%)", "skill": "Competency Skill"},
                        template="plotly_dark",
                        color_discrete_sequence=["#6C63FF"]
                    )
                    
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', range=[0, 100]),
                        yaxis=dict(showgrid=False),
                        margin=dict(l=20, r=20, t=10, b=10),
                        height=350,
                        font=dict(family="Inter, sans-serif")
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No skill demand metrics found.")
                    
            with col_pulse:
                st.subheader("Market Pulse Insights")
                st.markdown(
                    """
                    <div class='glass-card' style='height: 350px; overflow-y: auto;'>
                        <div class='market-pulse-title'>Trending Tools & Concepts</div>
                        <p style='color: #A0A0B0; font-size: 0.85rem; margin-bottom: 15px;'>
                            These modern tools are experiencing high search frequency growth in technical listings:
                        </p>
                    """,
                    unsafe_allow_html=True
                )
                
                # Print trending skills with custom icons
                for ts in data["skills"].get("trending_skills", []):
                    trend_icon = "📈" if ts.get("trend") == "up" else ("📉" if ts.get("trend") == "down" else "➡️")
                    trend_text = "Rising Demand" if ts.get("trend") == "up" else ("Declining" if ts.get("trend") == "down" else "Stable Trend")
                    trend_color = "#10B981" if ts.get("trend") == "up" else ("#EF4444" if ts.get("trend") == "down" else "#A0A0B0")
                    
                    st.markdown(
                        f"""
                        <div style='margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 8px;'>
                            <div>
                                <span class='badge-trend'>{ts['skill']}</span>
                            </div>
                            <div style='color: {trend_color}; font-size: 0.85rem; font-weight: 600;'>
                                {trend_icon} {trend_text}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)

        # TAB 2: Skill Gaps (Badges in columns)
        with tab2:
            st.subheader("Skills Competency Comparison")
            
            gap_col1, gap_col2 = st.columns(2)
            with gap_col1:
                st.markdown(
                    """
                    <div class='glass-card'>
                        <h4 style='color: #EF4444; margin-top: 0px;'>🔴 Gap Analysis (Missing Competencies)</h4>
                        <p style='color: #A0A0B0; font-size: 0.85rem; margin-bottom: 15px;'>
                            These critical competencies were found frequently in job postings, but were missing from your current list. Focus your learning roadmap here:
                        </p>
                    """,
                    unsafe_allow_html=True
                )
                
                missing = data["gap"].get("missing_skills", [])
                if missing:
                    for ms in missing:
                        st.markdown(f"<span class='badge-gap'>{ms}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color: #10B981;'>🎉 None! You match all top market capabilities.</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
            with gap_col2:
                st.markdown(
                    """
                    <div class='glass-card'>
                        <h4 style='color: #10B981; margin-top: 0px;'>🟢 Matching Strengths</h4>
                        <p style='color: #A0A0B0; font-size: 0.85rem; margin-bottom: 15px;'>
                            Great job! You possess these competencies which align directly with active industry postings:
                        </p>
                    """,
                    unsafe_allow_html=True
                )
                
                matching = data["gap"].get("matching_skills", [])
                if matching:
                    for mt in matching:
                        st.markdown(f"<span class='badge-match'>{mt}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color: #A0A0B0;'>Add skills in the sidebar to check matching metrics.</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # TAB 3: Week-by-Week Roadmap
        with tab3:
            st.subheader("Bridging The Gap: Weekly Plan")
            st.markdown("This timeline maps out target topics to learn the missing competencies over a 4-week sprint:")
            
            weeks = data["roadmap"].get("weeks", [])
            if weeks:
                for w in weeks:
                    st.markdown(
                        f"""
                        <div class='timeline-card'>
                            <div class='timeline-header'>Week {w['week']}</div>
                            <div class='timeline-topic'>{w['topic']}</div>
                            <p style='color: #D1D1E0; font-size: 0.95rem; line-height: 1.5; margin-bottom: 10px;'>
                                {w['details']}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    # Resources sub-bullets
                    if w.get("resources"):
                        st.markdown("**Recommended Resources & Study Paths:**")
                        for res in w["resources"]:
                            st.markdown(f"- 🔗 [{res}](https://www.google.com/search?q={requests.utils.quote_plus(res)})")
                        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
            else:
                st.info("No roadmap generated.")

        # TAB 4: Resume Download & Viewer
        with tab4:
            st.subheader("Optimized Portfolio Resume")
            st.markdown(
                "This resume has been compiled to highlight your matches while framing your missing skills "
                "positively as active learning goals. Perfect template to import into templates/docs."
            )
            
            resume_text = data.get("resume", "")
            if resume_text:
                # Custom container for the Markdown view
                st.markdown(
                    """
                    <div style='background-color: #12121F; padding: 25px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); max-height: 500px; overflow-y: auto;'>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(resume_text)
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<br/>", unsafe_allow_html=True)
                
                # Direct download button
                st.download_button(
                    label="Download Resume (Markdown)",
                    data=resume_text,
                    file_name="optimized_resume.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            else:
                st.info("No resume generated yet. Click Analyze in the sidebar.")

        # TAB 5: Scraped Jobs List
        with tab5:
            st.subheader("Target Market Openings")
            st.markdown("These listings were scraped/mocked based on your targeted job search:")
            
            jobs_list = data.get("jobs", [])
            if jobs_list:
                for idx, job in enumerate(jobs_list):
                    # Show listing summary inside expanders for readability
                    with st.expander(f"💼 {job['title']} — {job['company']} ({job['location']})"):
                        st.markdown(f"**Employer:** {job['company']}")
                        st.markdown(f"**Location:** {job['location']}")
                        st.markdown("**Description:**")
                        st.write(job["description"])
            else:
                st.info("No job listings scraped yet.")


if __name__ == "__main__":
    main()
