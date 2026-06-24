import os
import re
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Configure clean logging output for the orchestrator pipeline
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CareerReadyOrchestrator")

# Import all agents from their respective modules
try:
    from agents.job_scraper_agent import main as job_scraper_main
    from agents.skills_extractor_agent import main as skills_extractor_main
    from agents.gap_analyzer_agent import main as gap_analyzer_main
    from agents.resume_generator_agent import main as resume_generator_main
    from agents.career_roadmap_agent import main as career_roadmap_main
    from agents.nudge_agent import main as nudge_main
except ImportError as e:
    logger.error(f"Dependency Import Error: Failed to import agent modules. Detail: {e}")
    sys.exit(1)

def print_banner():
    """
    Prints a beautiful visual CLI banner for the orchestrator.
    """
    print("\n" + "="*60)
    print("      🌟 CAREERREADY AGENT PIPELINE ORCHESTRATOR 🌟      ")
    print("======================================================")
    print(" Connecting talent to target job market requirements ")
    print("="*60 + "\n")

async def run_pipeline():
    # Security: Verify that .env configuration file exists before executing
    if not os.path.exists(".env"):
        print("\n[ERROR] Security check failed: .env file does not exist in the root directory.")
        print("Please copy .env.example to .env and configure your Google Gemini API key.")
        return

    print_banner()

    # Step A: Gather inputs from the user at the very beginning
    print("--- STEP A: Gather Professional Profile & Learning Info ---")
    
    # 1. Target Job Role
    role = input("Enter your target job role (e.g., 'Data Analyst'): ").strip()
    if not role:
        print("[ERROR] Target job role cannot be empty.")
        return
    if len(role) > 100 or not re.match(r"^[a-zA-Z0-9\s\-\.\,\(\)\&]+$", role):
        print("[ERROR] Job role input is invalid or exceeds character limit.")
        return

    # 2. Current Skills
    skills = input("Enter your current skills (comma-separated, e.g., 'Python, SQL, Excel'): ").strip()
    if not skills:
        print("[ERROR] Current skills cannot be empty.")
        return
    if len(skills) > 500 or not re.match(r"^[a-zA-Z0-9\s\-\.\,\(\)\&]+$", skills):
        print("[ERROR] Skills input is invalid or exceeds character limit.")
        return

    # 3. Resume Information
    print("\n--- Resume Generator details ---")
    name = input("Full Name: ").strip()
    email = input("Email Address: ").strip()
    phone = input("Phone Number: ").strip()
    education = input("Education Details (e.g. BS in CS, XYZ University): ").strip()
    experience = input("Work Experience (summary, or 'None'): ").strip()

    # Validation on resume details
    resume_details = {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "experience": experience,
        "skills": skills,
        "target_role": role
    }
    for k, v in resume_details.items():
        if not v:
            print(f"[ERROR] Resume details field '{k}' cannot be empty.")
            return

    # 4. Weekly Milestone Progress (for Nudge Agent)
    print("\n--- Weekly Milestone Tracking (for Nudge Agent) ---")
    planned_learning = input("What did you plan to learn this week? (e.g. 'Python Basics'): ").strip()
    if not planned_learning:
        print("[ERROR] Planned learning goal cannot be empty.")
        return
    if len(planned_learning) > 150 or not re.match(r"^[a-zA-Z0-9\s\-\.\,\(\)\&]+$", planned_learning):
        print("[ERROR] Planned learning input is invalid or exceeds character limit.")
        return

    completed_status = input("Did you complete it? (yes/no): ").strip().lower()
    if completed_status not in ["yes", "y", "no", "n"]:
        print("[ERROR] Invalid completion status. Please enter 'yes' or 'no'.")
        return

    print("\n" + "-"*60)
    print(" Starting multi-agent pipeline execution...")
    print("-"*60)

    try:
        # Step 1: Job Scraper Agent
        print("\n[Pipeline Step 1/6] Running Job Scraper Agent...")
        await job_scraper_main(role_input=role)
        print("✔ Job Scraper Agent completed successfully.")

        # Step 2: Skills Extractor Agent
        print("\n[Pipeline Step 2/6] Running Skills Extractor Agent...")
        await skills_extractor_main()
        print("✔ Skills Extractor Agent completed successfully.")

        # Step 3: Gap Analyzer Agent
        print("\n[Pipeline Step 3/6] Running Gap Analyzer Agent...")
        await gap_analyzer_main(skills_input=skills)
        print("✔ Gap Analyzer Agent completed successfully.")

        # Step 4: Resume Generator Agent
        print("\n[Pipeline Step 4/6] Running Resume Generator Agent...")
        await resume_generator_main(details=resume_details)
        print("✔ Resume Generator Agent completed successfully.")

        # Step 5: Career Roadmap Agent
        print("\n[Pipeline Step 5/6] Running Career Roadmap Agent...")
        await career_roadmap_main()
        print("✔ Career Roadmap Agent completed successfully.")

        # Step 6: Nudge Agent
        print("\n[Pipeline Step 6/6] Running Nudge Agent...")
        await nudge_main(planned_input=planned_learning, completed_input=completed_status)
        print("✔ Nudge Agent completed successfully.")

        print("\n" + "="*60)
        print(" 🎉 PIPELINE RUN COMPLETED SUCCESSFULY! 🎉 ")
        print(" All analysis, roadmaps, and resumes have been updated.")
        print(" Run the Streamlit dashboard app to view results.")
        print("="*60 + "\n")

    except Exception as e:
        logger.error(f"Pipeline crashed during execution due to error: {e}")
        print("\n❌ Pipeline execution halted. Please resolve the error and try again.")

def main():
    asyncio.run(run_pipeline())

if __name__ == "__main__":
    main()
