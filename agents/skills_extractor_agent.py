import os
import re
import json
import logging
from collections import Counter
from dotenv import load_dotenv
from google.antigravity import Agent, LocalAgentConfig

# Configure logging to output information and error messages cleanly
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_job_postings() -> list[dict]:
    """
    Reads job postings from 'job_results.json' in the root workspace directory.
    This tool allows the agent to access the raw data collected by the scraper.
    
    Returns:
        list[dict]: A list of job postings, each with job_id, title, company, and description.
                    Returns an empty list if the file is not found or is invalid.
    """
    file_path = "job_results.json"
    
    # Check if the job results file exists in the directory
    if not os.path.exists(file_path):
        logger.warning(f"'{file_path}' not found in the current directory.")
        return []
        
    try:
        # Open and load the json file content with utf-8 encoding
        with open(file_path, "r", encoding="utf-8") as f:
            jobs = json.load(f)
            
        # Ensure the content is structured as a list
        if not isinstance(jobs, list):
            logger.error(f"'{file_path}' does not contain a list of job listings.")
            return []
            
        logger.info(f"Successfully read {len(jobs)} jobs from '{file_path}'.")
        return jobs
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from '{file_path}': {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error reading '{file_path}': {e}")
        return []

def save_skills_analysis(skills_per_job: list[list[str]]) -> str:
    """
    Counts the frequency of each skill across all job postings,
    calculates the percentage of job postings that mention each skill,
    and saves the results to 'skills_analysis.json' in the root workspace directory.
    
    Args:
        skills_per_job (list[list[str]]): A list where each element is a list of skills
                                          extracted from a single job posting.
                                          
    Returns:
        str: A status message confirming success and listing the saved stats.
    """
    # Security: Input validation on internal parameters
    if not isinstance(skills_per_job, list):
        logger.error("Input validation failed: skills_per_job must be a list.")
        return "Failed due to invalid input type."

    if not skills_per_job:
        logger.warning("No skills provided to save_skills_analysis tool.")
        return "No skills provided. Nothing was saved."
        
    total_jobs = len(skills_per_job)
    
    # We want to count how many job postings each skill appears in.
    # To do this correctly, we convert the skills list of each job to a set
    # so we count a skill at most once per job posting.
    skill_counts = Counter()
    for job_skills in skills_per_job:
        # Normalize/clean up skills extracted (whitespace cleaning)
        unique_skills = set(skill.strip() for skill in job_skills if skill.strip())
        for skill in unique_skills:
            skill_counts[skill] += 1
            
    # Calculate percentage for each skill and construct the analysis dictionary.
    # Percentage is (jobs_with_skill / total_jobs) * 100, rounded to the nearest integer.
    analysis_results = {}
    for skill, count in skill_counts.items():
        percentage = int(round((count / total_jobs) * 100))
        analysis_results[skill] = percentage
        
    # Sort results by percentage descending (and then alphabetically by skill name)
    sorted_analysis = dict(sorted(analysis_results.items(), key=lambda item: (-item[1], item[0])))
    
    # Determine the target role from the scraped jobs
    job_role = "Target Role"
    try:
        if os.path.exists("job_results.json"):
            with open("job_results.json", "r", encoding="utf-8") as rf:
                jobs = json.load(rf)
                if jobs and isinstance(jobs, list):
                    # Use the title of the first job as reference
                    job_role = jobs[0].get("title", "Target Role")
    except Exception as e:
        logger.warning(f"Could not determine role from job results: {e}")

    # Build structured list for backward compatibility with gap analyzer and dashboard
    market_skills = []
    for skill, percentage in sorted_analysis.items():
        if percentage >= 75:
            importance = "high"
        elif percentage >= 50:
            importance = "medium"
        else:
            importance = "low"
            
        market_skills.append({
            "name": skill,
            "skill": skill,
            "importance": importance,
            "demand_percentage": percentage
        })

    trending_skills = [
        {"skill": "Generative AI", "trend": "up"},
        {"skill": "Git", "trend": "stable"}
    ]

    # Combine into unified schema
    unified_output = {
        "role": job_role,
        "job_role": job_role,
        "skills": market_skills,
        "market_skills": market_skills,
        "trending_skills": trending_skills,
        **sorted_analysis
    }

    try:
        # Save the unified analysis results to skills_analysis.json
        with open("skills_analysis.json", "w", encoding="utf-8") as f:
            json.dump(unified_output, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Successfully saved skills analysis for {total_jobs} jobs to 'skills_analysis.json'.")
        return f"Successfully saved skill analysis of {total_jobs} jobs to 'skills_analysis.json'. Results: {json.dumps(sorted_analysis)}"
    except Exception as e:
        error_msg = f"Failed to write skills_analysis.json: {e}"
        logger.error(error_msg)
        return error_msg

def run_demo_mode():
    """
    Runs the skills extraction in Demo Mode.
    This reads 'job_results.json', uses a regex keyword matching parser to extract
    skills from job descriptions, and saves the results to 'skills_analysis.json'.
    This is used as a fallback if no valid GEMINI_API_KEY is configured.
    """
    logger.warning("Running in Demo Mode: Using local python keyword matching instead of Google Gemini.")
    
    # Read jobs from the job results file
    jobs = read_job_postings()
    if not jobs:
        print("[ERROR] No job postings found in job_results.json. Please run the Job Scraper Agent first.")
        return
        
    # Pre-defined list of common industry skills to match case-insensitively
    common_skills = [
        "Python", "SQL", "Excel", "Power BI", "Tableau", "Machine Learning", 
        "AWS", "Azure", "Git", "R", "Java", "C++", "Communication", "Data Analysis"
    ]
    
    skills_per_job = []
    for job in jobs:
        desc = job.get("description", "").lower()
        title = job.get("title", "").lower()
        text_to_search = f"{title} {desc}"
        
        extracted = []
        for skill in common_skills:
            # Build appropriate regex pattern to avoid partial word match issues (like 'R' in 'are')
            if skill == "C++":
                pattern = r'\bc\+\+(?=[ \s,.;:!?]|$)'
            elif skill == "R":
                pattern = r'\br\b'
            else:
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                
            # Perform regex search
            if re.search(pattern, text_to_search):
                extracted.append(skill)
        skills_per_job.append(extracted)
        
    # Process the extracted skills list and save results
    result_msg = save_skills_analysis(skills_per_job)
    
    print("\n==================================================")
    print("      Demo Mode: Local Skills Analysis Output      ")
    print("==================================================")
    print(result_msg)
    print("==================================================\n")

async def main():
    """
    Main asynchronous CLI driver for the Skills Extractor Agent.
    Loads environment configurations, initializes the Google ADK Agent with tools,
    executes the skill extraction prompt, and falls back to Demo Mode if authentication fails.
    """
    # Security: Verify that .env file exists before running
    if not os.path.exists(".env"):
        print("[ERROR] Security check failed: .env file does not exist in the root directory.")
        raise FileNotFoundError("Missing required .env configuration file in the project root.")

    # Load environment variables from .env file
    load_dotenv()
    
    # Security: Ensure all API keys are loaded ONLY from .env file (no hardcoding)
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    # Security: Validate that job_results.json exists and is not empty before parsing
    if not os.path.exists("job_results.json") or os.path.getsize("job_results.json") == 0:
        print("[ERROR] Security/Input check failed: job_results.json does not exist or is empty.")
        raise FileNotFoundError("job_results.json is missing or empty. Please run job scraper agent first.")

    # Determine if we should start directly in demo mode due to missing key
    is_demo = not gemini_key or "your_" in gemini_key or gemini_key == ""

    if is_demo:
        run_demo_mode()
        return

    # Configure the local Agent using the Google ADK configurations
    logger.info("Initializing Google Antigravity Agent...")
    config = LocalAgentConfig(
        system_instructions=(
            "You are the Skills Extractor Agent, a member of the CareerReady agent team.\n"
            "Your objective is to extract and analyze skills from job postings.\n"
            "You have access to two tools:\n"
            "1. `read_job_postings`: Reads job listings from 'job_results.json'.\n"
            "2. `save_skills_analysis`: Takes a list of lists of skills (one list of skills per job posting), "
            "calculates counts and percentages, and saves them to 'skills_analysis.json'.\n\n"
            "Follow these steps to complete your task:\n"
            "1. Call `read_job_postings` to retrieve the job listings.\n"
            "2. If `read_job_postings` returns an empty list, inform the user that no job listings were found "
            "and suggest they run the Job Scraper Agent first to generate job results.\n"
            "3. If job listings are present, analyze all job descriptions. For each job posting, extract a list of required technical and professional skills "
            "(e.g., programming languages, tools, frameworks, soft skills, methodologies).\n"
            "4. Standardize the skill names. Use clear, common names (e.g. 'Python', 'SQL', 'Excel', 'Power BI', 'Machine Learning', 'Communication'). "
            "Ensure names are consistent (e.g., don't mix 'Python' and 'python script').\n"
            "5. Call `save_skills_analysis` with the list of skill lists you extracted (one list of strings per job posting).\n"
            "6. Once the tool returns success, summarize the findings for the user. Present the top skills "
            "and their percentages in a professional, clear format."
        ),
        tools=[read_job_postings, save_skills_analysis],
        api_key=gemini_key
    )

    try:
        # Initialize and run the agent in an async context manager
        async with Agent(config) as agent:
            print("\n==================================================")
            print("    CareerReady - Skills Extractor Agent CLI      ")
            print("==================================================")
            print("[Agent] Beginning skills analysis and extraction...")
            
            # Start conversational chat session with the agent
            response = await agent.chat(
                "Please read the job postings from job_results.json, extract required skills from "
                "each description, standardize them, and save the results using save_skills_analysis."
            )
            
            # Get and display the agent response text
            agent_response = await response.text()
            print("\n==================================================")
            print("                Agent Response                    ")
            print("==================================================")
            print(agent_response)
            print("==================================================\n")
            
    except Exception as e:
        logger.error(f"An unexpected error occurred during agent execution: {e}")
        logger.warning("Attempting fallback execution in Demo Mode...")
        run_demo_mode()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
