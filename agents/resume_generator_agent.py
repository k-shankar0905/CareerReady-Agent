import os
import json
import logging
from dotenv import load_dotenv
from google.antigravity import Agent, LocalAgentConfig

# Configure logging to output information and error messages cleanly
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def prompt_user_details() -> dict:
    """
    Prompts the user via terminal for their personal details and professional background.
    
    Returns:
        dict: A dictionary containing the user's name, email, phone, education,
              experience, current skills, and target job role.
    """
    print("\n==================================================")
    print("      Resume Generator: Input Personal Details    ")
    print("==================================================")
    
    details = {}
    details["name"] = input("Full Name: ").strip()
    details["email"] = input("Email Address: ").strip()
    details["phone"] = input("Phone Number: ").strip()
    details["education"] = input("Education Details (e.g. BS in Computer Science, XYZ University): ").strip()
    details["experience"] = input("Work Experience (brief summary, or type 'None'): ").strip()
    details["skills"] = input("Current Skills (comma-separated, e.g. SQL, Python, Excel): ").strip()
    details["target_role"] = input("Target Job Role (e.g. Data Analyst): ").strip()
    
    return details

def read_gap_analysis() -> dict:
    """
    Reads the gap analysis data from 'gap_analysis.json' in the root workspace directory.
    This allows the agent to analyze the gap between the candidate and the target job requirements.
    
    Returns:
        dict: The parsed gap analysis data, or an empty dict if the file is missing or invalid.
    """
    file_path = "gap_analysis.json"
    if not os.path.exists(file_path):
        logger.warning(f"'{file_path}' not found in the current directory.")
        return {}
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Successfully loaded gap analysis from '{file_path}'.")
        return data
    except Exception as e:
        logger.error(f"Error reading '{file_path}': {e}")
        return {}

def save_resume(content: str) -> str:
    """
    Saves the generated resume content to 'resume_output.txt' and 'generated_resume.md'
    in the root workspace directory.
    
    Args:
        content (str): The plain-text formatted resume content.
        
    Returns:
        str: A status message confirming that the resume was saved successfully.
    """
    file_paths = ["resume_output.txt", "generated_resume.md"]
    saved_paths = []
    try:
        for path in file_paths:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            saved_paths.append(path)
        logger.info(f"Successfully saved generated resume to {saved_paths}.")
        return f"Successfully saved the resume to: {', '.join(saved_paths)}."
    except Exception as e:
        error_msg = f"Failed to save resume: {e}"
        logger.error(error_msg)
        return error_msg

def generate_resume_locally(details: dict, gap_data: dict) -> str:
    """
    Generates a structured, ATS-friendly professional resume locally using a Python template.
    This serves as a fallback when running in Demo Mode (without a valid Gemini API Key).
    
    Args:
        details (dict): The user's personal details.
        gap_data (dict): The gap analysis data from gap_analysis.json.
        
    Returns:
        str: The filled-out plain-text resume content.
    """
    name = details.get("name", "Name Not Provided")
    email = details.get("email", "Email Not Provided")
    phone = details.get("phone", "Phone Not Provided")
    education = details.get("education", "Education Not Provided")
    experience = details.get("experience", "No experience provided.")
    skills = details.get("skills", "Skills Not Provided")
    target_role = details.get("target_role", "Target Role Not Provided")
    
    # Extract matched and missing skills from the gap data if available
    matched_skills = gap_data.get("matched_skills", [])
    missing_skills = gap_data.get("missing_skills", [])
    
    # Construct a list of skills highlighting both current and matched skills
    highlighted_skills = skills
    if matched_skills:
        # Clean and filter duplicates
        current_set = {s.strip().lower() for s in skills.split(",")}
        additional = [s for s in matched_skills if s.strip().lower() not in current_set]
        if additional:
            highlighted_skills += f", {', '.join(additional)}"
            
    resume_text = f"""================================================================================
                                  {name.upper()}
================================================================================
Email: {email} | Phone: {phone}
Target Role: {target_role}

--------------------------------------------------------------------------------
PROFESSIONAL SUMMARY
--------------------------------------------------------------------------------
Results-driven professional seeking to transition into a {target_role} role. 
Possesses core strengths in {skills}. Highly motivated and aligned with current target
market requirements, demonstrating matching technical capabilities in {', '.join(matched_skills) if matched_skills else 'essential industry skills'}.

--------------------------------------------------------------------------------
EDUCATION
--------------------------------------------------------------------------------
{education}

--------------------------------------------------------------------------------
WORK EXPERIENCE
--------------------------------------------------------------------------------
{experience}

--------------------------------------------------------------------------------
TECHNICAL & PROFESSIONAL SKILLS
--------------------------------------------------------------------------------
- Core Proficiencies: {highlighted_skills}
- Key Alignments for {target_role}: {', '.join(matched_skills) if matched_skills else 'Standard industry competencies'}
"""
    if missing_skills:
        resume_text += f"- Professional Development Areas: {', '.join(missing_skills)}\n"
        
    resume_text += "================================================================================\n"
    return resume_text

def run_demo_mode(details: dict):
    """
    Runs the resume generation in Demo Mode.
    Reads 'gap_analysis.json', generates the resume using local template, and saves it.
    This is used as a fallback if no valid GEMINI_API_KEY is configured.
    
    Args:
        details (dict): The user's personal details.
    """
    logger.warning("Running in Demo Mode: Using local python resume generation template instead of Google Gemini.")
    
    # Load local gap analysis data
    gap_data = read_gap_analysis()
    
    # Format resume locally
    resume_content = generate_resume_locally(details, gap_data)
    
    # Save formatted resume
    save_msg = save_resume(resume_content)
    
    print("\n==================================================")
    # Print the saved resume output preview in terminal
    print("      Demo Mode: Generated Resume (Preview)       ")
    print("==================================================")
    print(resume_content)
    print(save_msg)
    print("==================================================\n")

async def main(details: dict = None):
    """
    Main asynchronous CLI driver for the Resume Generator Agent.
    Loads env configurations, prompts user details (if not programmatically supplied),
    initializes the Google ADK Agent with tools, executes the resume generation prompt,
    and falls back to Demo Mode if key is missing or invalid.
    """
    # Security: Verify that .env file exists before running
    if not os.path.exists(".env"):
        print("[ERROR] Security check failed: .env file does not exist in the root directory.")
        raise FileNotFoundError("Missing required .env configuration file in the project root.")

    # Load env variables from .env file
    load_dotenv()
    
    # Security: Ensure all API keys are loaded ONLY from .env file (no hardcoding)
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    # Prompt the user for details first if not supplied programmatically
    if details is None:
        details = prompt_user_details()
    
    # Security: Input validation on details fields (empty checks & lengths)
    required_keys = ["name", "email", "phone", "education", "experience", "skills", "target_role"]
    for key in required_keys:
        if key not in details:
            print(f"[ERROR] Input validation failed: '{key}' is missing in user details.")
            raise ValueError(f"Invalid Input: User details must contain '{key}'.")
            
        details[key] = str(details[key]).strip()
        if not details[key]:
            print(f"[ERROR] Input validation failed: User details field '{key}' cannot be empty.")
            raise ValueError(f"Invalid Input: '{key}' cannot be empty.")
            
    if len(details["name"]) > 100:
        raise ValueError("Name exceeds max length of 100.")
    if len(details["email"]) > 100 or "@" not in details["email"]:
        raise ValueError("Email is invalid or exceeds max length of 100.")
    if len(details["phone"]) > 20:
        raise ValueError("Phone exceeds max length of 20.")
    if len(details["education"]) > 200:
        raise ValueError("Education exceeds max length of 200.")
    if len(details["experience"]) > 1000:
        raise ValueError("Experience exceeds max length of 1000.")
    if len(details["skills"]) > 500:
        raise ValueError("Skills exceed max length of 500.")
    if len(details["target_role"]) > 100:
        raise ValueError("Target Role exceeds max length of 100.")

    # Security: Validate that gap_analysis.json exists and is not empty before parsing
    if not os.path.exists("gap_analysis.json") or os.path.getsize("gap_analysis.json") == 0:
        print("[ERROR] Security/Input check failed: gap_analysis.json does not exist or is empty.")
        raise FileNotFoundError("gap_analysis.json is missing or empty. Please run gap analyzer agent first.")

    # Determine if we should start directly in demo mode due to missing key
    is_demo = not gemini_key or "your_" in gemini_key or gemini_key == ""

    if is_demo:
        run_demo_mode(details)
        return

    # Configure the local Agent using the Google ADK configurations
    logger.info("Initializing Google Antigravity Agent...")
    config = LocalAgentConfig(
        system_instructions=(
            "You are the Resume Generator Agent, part of the CareerReady agent team.\n"
            "Your objective is to generate an ATS-friendly, professional text resume.\n"
            "You have access to two tools:\n"
            "1. `read_gap_analysis`: Reads gap analysis data (matched skills, missing skills, requirements) from 'gap_analysis.json'.\n"
            "2. `save_resume`: Takes a plain-text resume content string and saves it to 'resume_output.txt'.\n\n"
            "Follow these steps to complete your task:\n"
            "1. Call `read_gap_analysis` to check job market requirements for the target role.\n"
            "2. Using the user's details and the gap analysis data, write a tailored professional resume in plain text.\n"
            "3. Make the resume ATS-friendly. Structure it with standard headers (Professional Summary, Education, Experience, Skills).\n"
            "4. Highlight candidate skills that match the target role requirements from the gap analysis.\n"
            "5. Save the final resume using the `save_resume` tool.\n"
            "6. After saving, summarize the resume generation to the user and confirm the resume has been saved."
        ),
        tools=[read_gap_analysis, save_resume],
        api_key=gemini_key
    )

    try:
        # Initialize and run the agent in an async context manager
        async with Agent(config) as agent:
            print("\n[Agent] Starting resume generation session...")
            
            # Format conversational prompt with user details
            prompt = (
                f"Please load the gap analysis from gap_analysis.json using the read_gap_analysis tool.\n"
                f"Use that gap analysis to understand target role requirements.\n"
                f"Then, construct a professional, ATS-friendly plain-text resume for the candidate based on these details:\n"
                f"- Name: {details['name']}\n"
                f"- Email: {details['email']}\n"
                f"- Phone: {details['phone']}\n"
                f"- Education: {details['education']}\n"
                f"- Work Experience: {details['experience']}\n"
                f"- Candidate's Current Skills: {details['skills']}\n"
                f"- Target Job Role: {details['target_role']}\n\n"
                f"Structure the resume professionally, highlighting candidate skills that match the target role requirements "
                f"from the gap analysis. Once generated, save the full resume text using the save_resume tool."
            )
            
            # Start conversational chat session with the agent
            response = await agent.chat(prompt)
            
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
        run_demo_mode(details)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
