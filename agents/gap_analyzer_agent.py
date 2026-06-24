import os
import json
import logging
from dotenv import load_dotenv

# Try to import Google Antigravity SDK components.
# If they are not available, the script will fall back to local execution.
try:
    from google.antigravity import Agent, LocalAgentConfig
    HAS_ANTIGRAVITY = True
except ImportError:
    HAS_ANTIGRAVITY = False

# Configure logging for the agent execution
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_market_skills(file_path: str = "skills_analysis.json") -> dict:
    """
    Reads the market skills data from a JSON file.

    This function attempts to load the market skills definition. If the file is 
    missing or contains invalid JSON, it raises an exception or returns a fallback error.
    
    Args:
        file_path (str): The path to the skills analysis JSON file. Defaults to "skills_analysis.json".

    Returns:
        dict: A dictionary containing the target role and required skills list.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not a valid JSON.
    """
    # Check if the market skills database file exists at the given location
    if not os.path.exists(file_path):
        # Log an error message indicating the file is missing
        logger.error(f"Market skills file '{file_path}' not found.")
        # Raise FileNotFoundError to halt execution with a clear message
        raise FileNotFoundError(f"Missing required input file: {file_path}")
        
    try:
        # Open the JSON file in read-only mode with UTF-8 encoding
        with open(file_path, "r", encoding="utf-8") as f:
            # Parse the JSON content into a Python dictionary
            data = json.load(f)
            # Log a success message confirming the data has been loaded
            logger.info(f"Successfully loaded market skills from {file_path}")
            # Return the parsed dictionary structure
            return data
    except json.JSONDecodeError as e:
        # Log the specific error if the JSON is malformed
        logger.error(f"Error parsing market skills JSON file: {e}")
        # Re-raise the exception to be handled by the caller
        raise

def parse_user_skills(skills_input: str) -> list[str]:
    """
    Parses and normalizes the user's comma-separated input of skills.

    This function takes the raw user input, splits it by commas, strips leading/trailing
    whitespace, removes empty values, and normalizes the skills for comparison.

    Args:
        skills_input (str): Raw string input from the user (e.g. "Python, Excel, Tableau").

    Returns:
        list[str]: A list of clean, normalized skill strings.
    """
    # Verify if the input string is empty or contains only whitespace
    if not skills_input or not skills_input.strip():
        # Return an empty list if there are no skills entered
        return []
        
    # Split the input string by commas, strip leading/trailing whitespace from each skill,
    # and exclude any empty entries resulting from extra commas
    skills = [s.strip() for s in skills_input.split(",") if s.strip()]
    # Log the total number of valid user skills extracted
    logger.info(f"Parsed {len(skills)} skills from user input.")
    # Return the list of cleaned, parsed skill names
    return skills

def calculate_readiness_score(user_skills: list[str], market_skills: list[dict]) -> tuple[int, list[dict], list[dict]]:
    """
    Compares user skills with market requirements to compute a weighted readiness score.
    
    This function performs a case-insensitive comparison between user-provided skills
    and the list of market requirements. It scores readiness based on the importance weights:
    - High importance: Weight of 3
    - Medium importance: Weight of 2
    - Low importance: Weight of 1 (Default fallback)
    
    The readiness score is calculated as:
        Score = (Sum of weights of matched skills / Sum of weights of all market skills) * 100

    Args:
        user_skills (list[str]): A list of user-provided skills.
        market_skills (list[dict]): A list of dicts with keys 'name' and 'importance'.

    Returns:
        tuple[int, list[dict], list[dict]]: A tuple containing:
            - readiness_score (int): Computed readiness percentage (0 to 100).
            - matched_list (list[dict]): Skills from market requirements that the user possesses.
            - missing_list (list[dict]): Skills from market requirements that the user lacks.
    """
    # Create a set of lowercase user skills to ensure comparison is case-insensitive
    user_skills_set = {s.lower() for s in user_skills}
    
    # Initialize accumulators for total required weight and matched weight
    total_weight = 0
    matched_weight = 0
    
    # Initialize lists to separate skills the user matches vs. skills they are missing
    matched_list = []
    missing_list = []
    
    # Define mapping of importance levels to numeric weights for score calculation
    importance_weights = {
        "high": 3,
        "medium": 2,
        "low": 1
    }
    
    # Iterate through all market skills required for the role
    for skill_info in market_skills:
        # Safely extract skill name, fallback to 'skill' key or 'Unknown'
        skill_name = skill_info.get("name") or skill_info.get("skill") or "Unknown"
        # Safely extract importance, default to 'low' and convert to lowercase
        importance = skill_info.get("importance", "low").lower()
        
        # Get weight based on importance, defaulting to 1 if importance label is unrecognized
        weight = importance_weights.get(importance, 1)
        # Add the weight to the total denominator weight
        total_weight += weight
        
        # Perform case-insensitive search in user skills set
        if skill_name.lower() in user_skills_set:
            # If the user has this skill, add its weight to the matched numerator
            matched_weight += weight
            # Add to the list of matched skills
            matched_list.append({
                "name": skill_name,
                "importance": importance
            })
        else:
            # If the user lacks this skill, add to the missing/gap list
            missing_list.append({
                "name": skill_name,
                "importance": importance
            })
            
    # Calculate readiness score as a rounded percentage
    if total_weight == 0:
        # Fallback to 0 if the market requirements list is empty
        readiness_score = 0
    else:
        # Divide matched weight by total weight, round, and convert to integer percentage
        readiness_score = int(round((matched_weight / total_weight) * 100))
        
    # Log progress statistics for debugging and auditing
    logger.info(f"Calculated readiness score: {readiness_score}% based on matched weight {matched_weight}/{total_weight}.")
    # Return the score, matched list, and missing list
    return readiness_score, matched_list, missing_list

def rank_skills_by_importance(skills: list[dict]) -> list[dict]:
    """
    Sorts/ranks a list of skills by their importance level.

    The ranking order is High importance first, followed by Medium, and then Low.
    
    Args:
        skills (list[dict]): A list of skills containing 'importance'.

    Returns:
        list[dict]: The sorted list of skills.
    """
    # Define custom sort order dictionary where High is 0 (first), Medium is 1, Low is 2
    importance_order = {"high": 0, "medium": 1, "low": 2}
    
    # Use python's built-in sorted function with a key matching the importance rank.
    # We default any unrecognized importance level to 'low' (value 2).
    sorted_skills = sorted(
        skills, 
        key=lambda x: importance_order.get(x.get("importance", "low").lower(), 2)
    )
    # Return the ordered list of skills
    return sorted_skills

def save_gap_analysis(
    file_path: str,
    role: str,
    user_skills: list[str],
    readiness_score: int,
    matched_skills: list[dict],
    missing_skills: list[dict]
) -> None:
    """
    Saves the calculated skill gap analysis results to a JSON file.

    This compiles the inputs, matched skills, readiness score, and the missing skills gap
    list into a structured output dictionary and writes it to the designated file.

    Args:
        file_path (str): File path where results should be written (e.g. "gap_analysis.json").
        role (str): Target job role (e.g., "Data Analyst").
        user_skills (list[str]): The raw list of input skills.
        readiness_score (int): Calculated score out of 100.
        matched_skills (list[dict]): List of skills matching the market requirements.
        missing_skills (list[dict]): List of missing market skills ranked by importance.
    """
    # Construct the JSON output dictionary containing all analysis metrics
    output_data = {
        "target_role": role,
        "user_skills": user_skills,
        "readiness_score": f"{readiness_score}%",
        "readiness_percentage": readiness_score,
        "matched_skills": matched_skills,
        "skill_gap": missing_skills
    }
    
    try:
        # Open output file in write mode using UTF-8 to correctly handle any special character names
        with open(file_path, "w", encoding="utf-8") as f:
            # Write JSON data to the file with a clean 4-space indentation and unicode characters intact
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        # Log file save status success
        logger.info(f"Successfully saved gap analysis results to {file_path}")
    except Exception as e:
        # Log a failure message with the detailed exception context
        logger.error(f"Failed to write gap analysis results to file: {e}")
        # Re-raise the exception for error visibility
        raise

def perform_local_analysis(user_skills_input: str) -> dict:
    """
    Executes the core logical flow of the skill gap analysis locally.

    This function coordinates reading files, parsing input, matching skills,
    calculating scores, ranking missing requirements, and saving results.

    Args:
        user_skills_input (str): Raw string of comma-separated skills input by the user.

    Returns:
        dict: A dictionary containing all computed metrics of the analysis.
    """
    # 1. Load the market skills requirements from JSON database file
    market_data = load_market_skills("skills_analysis.json")
    # Retrieve target job role name, defaulting to "Target Role" if missing
    role = market_data.get("role", "Target Role")
    # Retrieve required skills list, defaulting to empty list if key is missing
    required_skills = market_data.get("skills", [])
    
    # 2. Parse and sanitize user's comma-separated input string into a list of skills
    user_skills = parse_user_skills(user_skills_input)
    
    # 3. Calculate weighted readiness score, matched skills list, and initial missing list
    readiness_score, matched_skills, missing_skills = calculate_readiness_score(user_skills, required_skills)
    
    # 4. Rank the missing skills by importance (High -> Medium -> Low)
    ranked_missing = rank_skills_by_importance(missing_skills)
    
    # 5. Save the complete gap analysis results to gap_analysis.json file
    save_gap_analysis("gap_analysis.json", role, user_skills, readiness_score, matched_skills, ranked_missing)
    
    # Return a structured result dictionary containing the calculation metrics
    return {
        "role": role,
        "user_skills": user_skills,
        "readiness_score": readiness_score,
        "matched_skills": matched_skills,
        "missing_skills": ranked_missing
    }

async def main():
    """
    Main entry point for running the Gap Analyzer Agent.

    It reads the configuration and prompts the user for their skills.
    If the GEMINI_API_KEY is available and Google Antigravity SDK is present, 
    it initiates an Agent session to present the gap analysis with smart, personalized 
    learning recommendations. Otherwise, it runs in purely local CLI mode.
    """
    # Load configuration environment variables from the standard dotenv (.env) file
    load_dotenv()
    # Retrieve the Gemini API key from the environment variables to check for connectivity
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    # Print welcome banners
    print("\n==================================================")
    print("      CareerReady - Gap Analyzer Agent CLI        ")
    print("==================================================")
    
    # Check if the essential input database 'skills_analysis.json' is present
    if not os.path.exists("skills_analysis.json"):
        # Print error and abort if the file doesn't exist
        print("[ERROR] 'skills_analysis.json' is missing. Please run job scraping or add skills first.")
        return
        
    # Ask the user to input their current skills as a comma-separated list
    skills_input = input("Enter your current skills (e.g. 'Python, Excel, Tableau'): ").strip()
    # Ensure input is not empty
    if not skills_input:
        print("[ERROR] Input skills cannot be empty.")
        return
        
    # Determine whether to use Google Antigravity Agent or fall back to local computation.
    # We use agent if SDK is imported, API key is present and is not placeholder string.
    use_agent = HAS_ANTIGRAVITY and gemini_key and "your_gemini_api_key_here" not in gemini_key
    
    if use_agent:
        # Log agent activation state
        logger.info("Initializing Google Antigravity Agent for skill gap reporting...")
        
        # Tool wrapped specifically for the Agent context to calculate metrics
        def analyze_skills(user_input: str) -> str:
            """
            Analyzes the skill gap between user input and market requirements,
            saves the results, and returns a raw representation for the agent.
            """
            try:
                # Perform the core gap analysis logic and retrieve result dictionary
                results = perform_local_analysis(user_input)
                # Return the results serialized as a formatted JSON string
                return json.dumps(results, indent=2)
            except Exception as e:
                # Return error message to the agent if calculations fail
                return f"Error conducting gap analysis: {str(e)}"
                
        # Define settings and instructions for the Google Antigravity Agent
        config = LocalAgentConfig(
            system_instructions=(
                "You are the Gap Analyzer Agent, part of the CareerReady agent team.\n"
                "Your goal is to guide the user on their readiness for the target role.\n"
                "1. Run the `analyze_skills` tool with the user's input skills.\n"
                "2. Parse the JSON results returned by the tool.\n"
                "3. Present the analysis beautifully. Specifically: \n"
                "   - State the target role and the readiness score out of 100 (e.g., 'You are 65% ready for Data Analyst role').\n"
                "   - List matched skills.\n"
                "   - List missing skills ranked by importance (High first, then Medium, then Low).\n"
                "   - Mention that detailed results are saved to `gap_analysis.json`.\n"
                "4. Provide 2-3 actionable, high-quality recommendations for how the user can close the gaps (e.g. recommend learning High importance missing skills first)."
            ),
            tools=[analyze_skills],
            api_key=gemini_key
        )
        
        try:
            # Create and start the Agent context session asynchronously
            async with Agent(config) as agent:
                print("\n[Agent] Running skill gap analysis...")
                # Dispatch the user query to the agent
                response = await agent.chat(f"Analyze skill gap for: {skills_input}")
                # Wait for the agent to return a text response
                agent_response = await response.text()
                
                # Print the final agent analysis report
                print("\n==================================================")
                print("                Agent Analysis                    ")
                print("==================================================")
                print(agent_response)
                print("==================================================\n")
        except Exception as e:
            # If the Agent invocation fails, log the error and fall back to local offline mode
            logger.error(f"Error running agent: {e}. Falling back to local mode.")
            use_agent = False
            
    if not use_agent:
        # Local analysis mode (runs purely offline/deterministically without Gemini API keys)
        print("\n[Local Mode] Running local skill gap analysis...")
        try:
            # Run the deterministic analyzer locally using the parsed input
            results = perform_local_analysis(skills_input)
            
            # Print the computed results to terminal output
            print("\n==================================================")
            print("                 ANALYSIS RESULTS                 ")
            print("==================================================")
            print(f"Target Role: {results['role']}")
            print(f"Readiness Score: {results['readiness_score']}/100")
            print(f"Status: You are {results['readiness_score']}% ready for {results['role']} role.")
            
            print("\nMatched Skills:")
            # If there are matched skills, print them individually
            if results['matched_skills']:
                for skill in results['matched_skills']:
                    print(f"  - {skill['name']} (Importance: {skill['importance'].capitalize()})")
            else:
                # Print None if there are no matches
                print("  - None")
                
            print("\nMissing Skills (Ranked by Importance):")
            # If there are missing skills, iterate and print them
            if results['missing_skills']:
                for skill in results['missing_skills']:
                    print(f"  - {skill['name']} (Importance: {skill['importance'].capitalize()})")
            else:
                # Print congrats if there are no missing skills
                print("  - None! You match all requirements!")
                
            print("\n--------------------------------------------------")
            print("Results saved to `gap_analysis.json` successfully.")
            print("==================================================\n")
            
        except Exception as e:
            # Output an error message if any part of the execution fails
            print(f"\n[ERROR] Analysis failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
