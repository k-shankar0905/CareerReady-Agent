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

def load_career_roadmap(file_path: str = "career_roadmap.json") -> dict:
    """
    Loads the career roadmap database from a JSON file.

    This function checks if the roadmap configuration exists, loads its contents
    as a Python dictionary, and handles missing files or parsing errors.

    Args:
        file_path (str): The path to the career roadmap JSON file. Defaults to "career_roadmap.json".

    Returns:
        dict: The parsed career roadmap data containing target role and weekly milestones.

    Raises:
        FileNotFoundError: If the career roadmap file does not exist.
        json.JSONDecodeError: If the file is not a valid JSON structure.
    """
    # Verify that the career roadmap database exists
    if not os.path.exists(file_path):
        logger.error(f"Career roadmap file '{file_path}' not found.")
        raise FileNotFoundError(f"Missing required roadmap file: {file_path}")
        
    try:
        # Open and load the JSON database using UTF-8 encoding
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"Successfully loaded career roadmap from {file_path}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse career roadmap JSON: {e}")
        raise

def load_progress(file_path: str = "progress.json") -> dict:
    """
    Loads the user's learning progress from a progress.json file.

    If the progress file does not exist, it initializes and returns a default
    progress dictionary structure to start tracking from scratch.

    Args:
        file_path (str): The path to the progress tracking file. Defaults to "progress.json".

    Returns:
        dict: A dictionary containing the user's completed week list.
    """
    # Check if progress file already exists
    if not os.path.exists(file_path):
        logger.info(f"Progress file '{file_path}' not found. Initializing new progress tracking.")
        # Return default structure if it is a new user tracking session
        return {"completed_weeks": []}
        
    try:
        # Load progress from the JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure the completed_weeks key is always present
            if "completed_weeks" not in data:
                data["completed_weeks"] = []
            return data
    except Exception as e:
        logger.warning(f"Error reading progress file '{file_path}': {e}. Starting with empty progress.")
        return {"completed_weeks": []}

def save_progress(progress_data: dict, file_path: str = "progress.json") -> None:
    """
    Saves the user's updated progress tracking database back to progress.json.

    Args:
        progress_data (dict): The current progress dictionary to save.
        file_path (str): File path where progress should be written. Defaults to "progress.json".
    """
    try:
        # Save the updated data with pretty print indentation of 4 spaces
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(progress_data, f, indent=4, ensure_ascii=False)
        logger.info(f"Successfully saved user progress to {file_path}")
    except Exception as e:
        logger.error(f"Failed to write progress to '{file_path}': {e}")
        raise

def find_matching_week(user_input: str, roadmap: dict, progress: dict) -> dict:
    """
    Matches the user's description of what they planned to learn to a week in the roadmap.

    It performs a case-insensitive keyword search on the 'goal' and 'description' keys.
    If no matches are found, it falls back to returning the first uncompleted week.

    Args:
        user_input (str): The learning activity string entered by the user.
        roadmap (dict): The parsed career roadmap containing weekly details.
        progress (dict): The user's progress tracking data.

    Returns:
        dict: The dictionary of the matched week from the career roadmap.
    """
    weeks = roadmap.get("weeks", [])
    if not weeks:
        return {}

    user_input_lower = user_input.strip().lower()
    
    # 1. Look for a direct substring match in the goal or description of each week
    for week_data in weeks:
        goal = week_data.get("goal", "").lower()
        description = week_data.get("description", "").lower()
        if user_input_lower in goal or user_input_lower in description:
            logger.info(f"Matched input '{user_input}' to Week {week_data.get('week')} via substring matching.")
            return week_data

    # 2. Look for common keywords in case of multi-word inputs
    words = [w for w in user_input_lower.split() if len(w) > 2]
    for week_data in weeks:
        goal = week_data.get("goal", "").lower()
        if any(word in goal for word in words):
            logger.info(f"Matched input '{user_input}' to Week {week_data.get('week')} via keyword matching.")
            return week_data

    # 3. Fallback: Identify and return the first uncompleted week in the sequence
    completed = set(progress.get("completed_weeks", []))
    for week_data in weeks:
        if week_data.get("week") not in completed:
            logger.info(f"No match found for '{user_input}'. Defaulting to next uncompleted Week {week_data.get('week')}.")
            return week_data

    # 4. If all weeks are completed, default to the last week
    logger.info("All weeks completed. Defaulting to the last roadmap milestone.")
    return weeks[-1]

def calculate_progress_percentage(progress: dict, roadmap: dict) -> int:
    """
    Computes the user's overall career roadmap progress as an integer percentage.

    Args:
        progress (dict): The user's progress tracking data.
        roadmap (dict): The parsed career roadmap data.

    Returns:
        int: The completion percentage out of 100.
    """
    total_weeks = len(roadmap.get("weeks", []))
    if total_weeks == 0:
        return 0
        
    completed_weeks = len(set(progress.get("completed_weeks", [])))
    # Calculate percentage and clamp it at 100% maximum
    percentage = int(round((completed_weeks / total_weeks) * 100))
    return min(percentage, 100)

def track_and_update_progress(planned_input: str, completed_bool: bool) -> dict:
    """
    Coordinates reading files, matching goals, updating progress, and calculating scores.

    This function acts as the core logical executor that ties the file states and 
    user interaction state changes together.

    Args:
        planned_input (str): What the user planned to learn.
        completed_bool (bool): Whether the goal was completed.

    Returns:
        dict: A structure containing matching, status updates, and progress stats.
    """
    # 1. Load roadmap and progress files
    roadmap = load_career_roadmap("career_roadmap.json")
    progress = load_progress("progress.json")
    
    # 2. Find which week in the roadmap matches what the user planned to learn
    matched_week = find_matching_week(planned_input, roadmap, progress)
    week_num = matched_week.get("week")
    
    # 3. If completed, add the week number to progress tracking
    if completed_bool:
        if week_num not in progress["completed_weeks"]:
            progress["completed_weeks"].append(week_num)
            progress["completed_weeks"].sort()
            save_progress(progress, "progress.json")
            
    # 4. Find the next week in sequence to display to the user
    weeks = roadmap.get("weeks", [])
    next_week = None
    for w in weeks:
        if w.get("week") == week_num + 1:
            next_week = w
            break
            
    # 5. Compute the final overall completion rate
    overall_percentage = calculate_progress_percentage(progress, roadmap)
    
    return {
        "matched_week": matched_week,
        "completed": completed_bool,
        "next_week": next_week,
        "progress_percentage": overall_percentage,
        "total_weeks": len(weeks),
        "completed_count": len(progress["completed_weeks"])
    }

async def main():
    """
    Main asynchronous orchestrator for running the Nudge Agent CLI.

    It loads configurations, guides the user through progress checks, and optionally
    boots up the Google Antigravity Agent to generate personalized support/nudges
    or falls back to deterministic local processing.
    """
    # Load dotenv credentials configuration
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    print("\n==================================================")
    print("         CareerReady - Nudge Agent CLI            ")
    print("==================================================")
    
    # Verify career roadmap exists before executing
    if not os.path.exists("career_roadmap.json"):
        print("[ERROR] 'career_roadmap.json' is missing. Please create it or place it in the root.")
        return

    # 1. Load data to display current pending goals to guide the user
    roadmap = load_career_roadmap("career_roadmap.json")
    progress = load_progress("progress.json")
    completed_set = set(progress.get("completed_weeks", []))
    
    print("\nYour Weekly Roadmap Milestones:")
    for w in roadmap.get("weeks", []):
        status = "[x] Completed" if w.get("week") in completed_set else "[ ] Pending"
        print(f"  Week {w.get('week')}: {w.get('goal')} {status}")
        
    print("\n--------------------------------------------------")
    
    # 2. Ask user what they planned to learn this week
    planned_input = input("\nWhat did you plan to learn this week? ").strip()
    if not planned_input:
        print("[ERROR] Planned learning goal cannot be empty.")
        return
        
    # 3. Ask if they completed it
    completed_input = input("Did you complete it? (yes/no): ").strip().lower()
    if completed_input not in ["yes", "y", "no", "n"]:
        print("[ERROR] Invalid response. Please enter 'yes' or 'no'.")
        return
        
    completed_bool = completed_input in ["yes", "y"]
    
    # Determine whether to use Agent mode or local mode
    use_agent = HAS_ANTIGRAVITY and gemini_key and "your_gemini_api_key_here" not in gemini_key
    
    if use_agent:
        logger.info("Initializing Google Antigravity Agent for custom motivation and next steps...")
        
        # Tool wrapped for the Agent context to execute the update
        def process_progress(planned_goal: str, completed: bool) -> str:
            """
            Updates progress files and returns matching info for the agent to report.
            """
            try:
                results = track_and_update_progress(planned_goal, completed)
                return json.dumps(results, indent=2)
            except Exception as e:
                return f"Error executing progress update: {str(e)}"
                
        config = LocalAgentConfig(
            system_instructions=(
                "You are the Nudge Agent, part of the CareerReady agent team.\n"
                "Your goal is to check in on the user's weekly learning progress and nudge them to stay on track.\n"
                "1. Call the `process_progress` tool with user inputs.\n"
                "2. Parse the JSON results returned by the tool.\n"
                "3. Present the outcome to the user beautifully: \n"
                "   - If completed is True:\n"
                "     - Congratulate them warmly.\n"
                "     - Show the next week's goal and description.\n"
                "   - If completed is False:\n"
                "     - Motivate them to keep going.\n"
                "     - Retrieve the matched week's 'importance' value and remind them why it is important.\n"
                "   - State the overall progress percentage (e.g. 'Your overall roadmap progress is now X%').\n"
                "   - Mention that progress has been saved to `progress.json`."
            ),
            tools=[process_progress],
            api_key=gemini_key
        )
        
        try:
            async with Agent(config) as agent:
                print("\n[Agent] Logging progress and generating response...")
                response = await agent.chat(f"Planned to learn: '{planned_input}'. Completed: {completed_bool}")
                agent_response = await response.text()
                
                print("\n==================================================")
                print("                Agent Feedback                    ")
                print("==================================================")
                print(agent_response)
                print("==================================================\n")
        except Exception as e:
            logger.error(f"Error running agent: {e}. Falling back to local offline mode.")
            use_agent = False
            
    if not use_agent:
        # Local analysis mode (runs offline without Gemini key)
        print("\n[Local Mode] Logging progress...")
        try:
            results = track_and_update_progress(planned_input, completed_bool)
            matched_week = results["matched_week"]
            
            print("\n==================================================")
            print("                 PROGRESS UPDATE                  ")
            print("==================================================")
            print(f"Goal Analyzed: {matched_week.get('goal')} (Week {matched_week.get('week')})")
            
            if results["completed"]:
                print("\n🎉 Congratulations! You completed this week's milestone!")
                next_week = results["next_week"]
                if next_week:
                    print(f"\nNext Week's Goal (Week {next_week.get('week')}):")
                    print(f"  Goal: {next_week.get('goal')}")
                    print(f"  Description: {next_week.get('description')}")
                else:
                    print("\n🏆 Amazing! You have completed all weeks in your career roadmap!")
            else:
                print("\n💪 Don't worry! Keep pushing forward.")
                print(f"Why this milestone matters: {matched_week.get('importance')}")
                
            print(f"\nOverall Progress: {results['progress_percentage']}% completed ({results['completed_count']}/{results['total_weeks']} weeks)")
            print("--------------------------------------------------")
            print("Progress saved to `progress.json` successfully.")
            print("==================================================\n")
            
        except Exception as e:
            print(f"\n[ERROR] Failed to execute progress tracking: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
