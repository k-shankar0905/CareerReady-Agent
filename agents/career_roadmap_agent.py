import os
import json
import logging
from typing import Union, Dict, Any
from dotenv import load_dotenv

# Try to import Google Antigravity SDK components.
# If they are not available, the script will fall back to local execution.
try:
    from google.antigravity import Agent, LocalAgentConfig
    HAS_ANTIGRAVITY = True
except ImportError:
    HAS_ANTIGRAVITY = False

# Configure logging for the agent to output informative messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_gap_analysis(file_path: str = "gap_analysis.json") -> Dict[str, Any]:
    """
    Reads and parses the gap analysis data from a JSON file.

    Args:
        file_path (str): The file path of the gap analysis JSON. Defaults to "gap_analysis.json".

    Returns:
        Dict[str, Any]: The parsed JSON data as a dictionary.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file content is not valid JSON.
    """
    logger.info(f"Reading gap analysis file from path: '{file_path}'")
    
    # Verify that the gap analysis file exists before opening it
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Gap analysis file '{file_path}' not found. Please ensure the file exists in the workspace.")

    # Open the file with UTF-8 encoding to support international characters
    with open(file_path, "r", encoding="utf-8") as f:
        # Load and parse the JSON content into a Python dictionary
        return json.load(f)

def save_career_roadmap(roadmap_data: Union[str, Dict[str, Any]], file_path: str = "career_roadmap.json") -> str:
    """
    Saves the generated career roadmap data to a JSON file. Handles both parsed dictionaries
    and raw JSON strings, ensuring formatting is clean.

    Args:
        roadmap_data (Union[str, Dict[str, Any]]): The roadmap content to save.
        file_path (str): The destination file path. Defaults to "career_roadmap.json".

    Returns:
        str: A status message indicating success or failure.
    """
    logger.info(f"Attempting to save career roadmap to path: '{file_path}'")
    try:
        # If the input data is a string, check if it's JSON and parse it for pretty printing
        if isinstance(roadmap_data, str):
            try:
                data_to_save = json.loads(roadmap_data)
            except json.JSONDecodeError:
                # If it's not valid JSON, log a warning and save it as raw string content
                logger.warning("Provided roadmap_data string is not valid JSON. Saving as raw string content.")
                data_to_save = roadmap_data
        else:
            # If it is already a dictionary or list, save it directly
            data_to_save = roadmap_data

        # Open the output file in write mode with UTF-8 encoding
        with open(file_path, "w", encoding="utf-8") as f:
            if isinstance(data_to_save, (dict, list)):
                # Write the JSON data with a neat 4-space indentation
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
            else:
                # Write raw string content directly to the file
                f.write(str(data_to_save))

        logger.info(f"Successfully saved career roadmap to '{file_path}'")
        return f"Successfully saved career roadmap to {file_path}"
    except Exception as e:
        # Log any system exception that occurred during writing and return an error message
        error_msg = f"Failed to save career roadmap to {file_path}: {str(e)}"
        logger.error(error_msg)
        return error_msg

def generate_local_roadmap(gap_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a fallback career roadmap locally without calling the Gemini API,
    by using a static library of free resources for common skills and a dynamic template.

    Args:
        gap_data (Dict[str, Any]): The gap analysis results parsed from the input JSON.

    Returns:
        Dict[str, Any]: A structured roadmap containing estimated learning times, prioritized
                       free learning resources, and a week-by-week plan matching the required schema.
    """
    logger.info("Generating learning roadmap locally (offline mode fallback)...")
    
    # Extract the target role name, defaulting to "Target Role" if not found
    target_role = gap_data.get("target_role", "Target Role")
    
    # Retrieve missing skills from the gap data (supporting multiple potential schema keys)
    missing_skills_raw = gap_data.get("missing_skills", [])
    if not missing_skills_raw:
        missing_skills_raw = gap_data.get("skill_gap", [])
        
    missing_skills = []
    # Normalize the extracted skills into simple strings
    for s in missing_skills_raw:
        if isinstance(s, dict):
            missing_skills.append(s.get("name", ""))
        else:
            missing_skills.append(str(s))
            
    # Filter out empty or whitespace-only skill names
    missing_skills = [s for s in missing_skills if s.strip()]

    # Library containing predefined free resources and study duration mappings for common skills
    resource_library = {
        "power bi": {
            "time": "2 weeks (15 hours)",
            "resources": [
                {"name": "Power BI Documentation", "url": "https://learn.microsoft.com/en-us/power-bi/", "type": "Documentation"},
                {"name": "Power BI for Beginners - YouTube", "url": "https://www.youtube.com/playlist?list=PLmB0edc1zS68tL1C7k833wL83R7Hk33iJ", "type": "YouTube"},
                {"name": "Coursera Free: Getting Started with Power BI Desktop", "url": "https://www.coursera.org/learn/getting-started-with-power-bi-desktop", "type": "Coursera"}
            ]
        },
        "tableau": {
            "time": "2 weeks (12 hours)",
            "resources": [
                {"name": "Tableau Training Videos", "url": "https://www.tableau.com/learn/training", "type": "Documentation"},
                {"name": "Tableau for Beginners - YouTube", "url": "https://www.youtube.com/watch?v=aHaOIvR00Hg", "type": "YouTube"},
                {"name": "Coursera Free: Data Visualization with Tableau Specialization", "url": "https://www.coursera.org/specializations/data-visualization", "type": "Coursera"}
            ]
        },
        "python": {
            "time": "3 weeks (25 hours)",
            "resources": [
                {"name": "Python 3 Official Documentation", "url": "https://docs.python.org/3/", "type": "Documentation"},
                {"name": "Python for Beginners - YouTube Course", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw", "type": "YouTube"},
                {"name": "Coursera Free: Programming for Everybody (Python)", "url": "https://www.coursera.org/learn/python", "type": "Coursera"}
            ]
        },
        "sql": {
            "time": "2 weeks (15 hours)",
            "resources": [
                {"name": "W3Schools SQL Tutorial", "url": "https://www.w3schools.com/sql/", "type": "Documentation"},
                {"name": "SQL Tutorial for Beginners - YouTube", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY", "type": "YouTube"},
                {"name": "Coursera Free: SQL for Data Science", "url": "https://www.coursera.org/learn/sql-for-data-science", "type": "Coursera"}
            ]
        },
        "excel": {
            "time": "1 week (10 hours)",
            "resources": [
                {"name": "Microsoft Excel Support & Training", "url": "https://support.microsoft.com/excel", "type": "Documentation"},
                {"name": "Excel crash course - YouTube", "url": "https://www.youtube.com/watch?v=rwbho0CgEAE", "type": "YouTube"},
                {"name": "Coursera Free: Everyday Excel", "url": "https://www.coursera.org/learn/everyday-excel-part-1", "type": "Coursera"}
            ]
        },
        "fastapi": {
            "time": "2 weeks (15 hours)",
            "resources": [
                {"name": "FastAPI Official Documentation", "url": "https://fastapi.tiangolo.com/", "type": "Documentation"},
                {"name": "FastAPI Course - YouTube", "url": "https://www.youtube.com/watch?v=tLKKmCOKiNM", "type": "YouTube"}
            ]
        },
        "docker": {
            "time": "1 week (8 hours)",
            "resources": [
                {"name": "Docker Get Started Docs", "url": "https://docs.docker.com/get-started/", "type": "Documentation"},
                {"name": "Docker Tutorial for Beginners - YouTube", "url": "https://www.youtube.com/watch?v=3c-iBn73dDE", "type": "YouTube"}
            ]
        },
        "postgresql": {
            "time": "2 weeks (12 hours)",
            "resources": [
                {"name": "PostgreSQL Tutorial website", "url": "https://www.postgresqltutorial.com/", "type": "Documentation"},
                {"name": "PostgreSQL Course - YouTube", "url": "https://www.youtube.com/watch?v=qw--VYLpxG4", "type": "YouTube"}
            ]
        }
    }

    missing_skills_analysis = []
    week_by_week_plan = []
    current_week = 1

    # Map each missing skill to structured suggestions and populate lists
    for idx, skill in enumerate(missing_skills):
        skill_lower = skill.lower().strip()
        
        # Search for matched skills in the local resource library
        matched_info = None
        for key, info in resource_library.items():
            if key in skill_lower or skill_lower in key:
                matched_info = info
                break
                
        # Assign matched information or fallback values if not recognized
        if matched_info:
            time_est = matched_info["time"]
            resources = matched_info["resources"]
        else:
            time_est = "2 weeks (10 hours)"
            resources = [
                {"name": f"{skill} Official Documentation", "url": f"https://www.google.com/search?q={skill}+documentation", "type": "Documentation"},
                {"name": f"{skill} Tutorial for Beginners - YouTube", "url": f"https://www.youtube.com/results?search_query={skill}+tutorial", "type": "YouTube"}
            ]
            
        # Append analysis details to the list of missing skills
        missing_skills_analysis.append({
            "skill": skill,
            "priority": idx + 1,
            "estimated_time_to_learn": time_est,
            "free_resources": resources
        })
        
        # Distribute topics across sequential weeks (e.g. 2 weeks per skill)
        week_by_week_plan.append({
            "week": current_week,
            "topics": [f"Introduction to {skill}", f"Core concepts and basic setup of {skill}"],
            "resources": [resources[0]["name"]]
        })
        week_by_week_plan.append({
            "week": current_week + 1,
            "topics": [f"Intermediate {skill} tools", f"Practical portfolio project using {skill}"],
            "resources": [r["name"] for r in resources[1:]]
        })
        current_week += 2
        
    # Return structured roadmap matching the expected JSON outline
    return {
        "target_role": target_role,
        "missing_skills_analysis": missing_skills_analysis,
        "week_by_week_plan": week_by_week_plan
    }

async def main():
    """
    Main entry point for the Career Roadmap Agent.
    Loads environment variables, configures the Google ADK agent with system instructions
    and tools, triggers the agent loop to analyze gaps, creates a learning roadmap,
    saves the results to career_roadmap.json, and prints a final agent response.
    If the agent components are missing or configuration is incomplete, executes locally.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve the Gemini API key from environment variables
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    # Determine whether we should invoke the Gemini SDK or run deterministically locally
    use_agent = HAS_ANTIGRAVITY and gemini_key and "your_gemini_api_key_here" not in gemini_key

    # Define tool functions wrapping the read/write logic for the agent to call
    def agent_read_gap_analysis() -> str:
        """
        Tool that reads the gap analysis from gap_analysis.json and returns it as a JSON string.

        Returns:
            str: JSON string of the gap analysis or an error message.
        """
        try:
            data = read_gap_analysis("gap_analysis.json")
            return json.dumps(data)
        except Exception as e:
            return f"Error reading gap analysis: {str(e)}"

    def agent_save_roadmap(roadmap_json_str: str) -> str:
        """
        Tool that saves the generated roadmap JSON string to career_roadmap.json.

        Args:
            roadmap_json_str (str): The structured roadmap JSON string generated by the agent.

        Returns:
            str: Status message from the save operation.
        """
        return save_career_roadmap(roadmap_json_str, "career_roadmap.json")

    if use_agent:
        logger.info("Initializing Google Antigravity Agent configuration...")
        
        # System instruction guide for the agent's behavior and formatting rules
        system_instructions = (
            "You are the Career Roadmap Agent, a helpful agent designed to guide users in learning new skills.\n"
            "Your main responsibility is to read the gap analysis, analyze the missing skills, suggest learning resources, "
            "and structure a comprehensive learning plan.\n\n"
            "Perform the following steps:\n"
            "1. Read the gap analysis by invoking the `agent_read_gap_analysis` tool.\n"
            "2. For each missing skill, suggest:\n"
            "   - Free learning resources (YouTube videos/playlists, Coursera free courses, official documentation, tutorials)\n"
            "   - Estimated time to learn (e.g., '10 hours', '2 weeks')\n"
            "   - Priority order / learning order (e.g., skill A must be learned before skill B)\n"
            "3. Create a week-by-week learning plan dividing the topic coverage over a sequence of weeks.\n"
            "4. Call the `agent_save_roadmap` tool, passing a clean, valid JSON string containing the generated roadmap details. "
            "   The JSON must follow this exact structure:\n"
            "   {\n"
            "     \"target_role\": \"<Role Name>\",\n"
            "     \"missing_skills_analysis\": [\n"
            "       {\n"
            "         \"skill\": \"<Skill Name>\",\n"
            "         \"priority\": <Integer, e.g. 1, 2, 3>,\n"
            "         \"estimated_time_to_learn\": \"<Time estimation>\",\n"
            "         \"free_resources\": [\n"
            "           {\n"
            "             \"name\": \"<Resource Title>\",\n"
            "             \"url\": \"<URL to resource>\",\n"
            "             \"type\": \"<YouTube | Coursera | Documentation | Other>\"\n"
            "           }\n"
            "         ]\n"
            "       }\n"
            "     ],\n"
            "     \"week_by_week_plan\": [\n"
            "       {\n"
            "         \"week\": <Integer>,\n"
            "         \"topics\": [\"<Topic 1>\", \"<Topic 2>\"],\n"
            "         \"resources\": [\"<Resource Name or Link>\"]\n"
            "       }\n"
            "     ]\n"
            "   }\n"
            "5. Once the roadmap is saved, output a polite, human-readable summary of the plan, including the priority list and "
            "   a confirmation that the detailed roadmap has been saved to `career_roadmap.json`."
        )

        # Build local agent config passing tools and API key
        config = LocalAgentConfig(
            system_instructions=system_instructions,
            tools=[agent_read_gap_analysis, agent_save_roadmap],
            api_key=gemini_key
        )

        try:
            # Instantiate the Antigravity Agent and start chat conversation
            async with Agent(config) as agent:
                logger.info("Starting roadmap generation process with Gemini Agent...")
                
                # Command the agent to read, prioritize, build the plan and save results
                response = await agent.chat(
                    "Please read the gap analysis from gap_analysis.json, analyze the missing skills, "
                    "suggest free resources, prioritize them, create a week-by-week plan, and save the final "
                    "roadmap to career_roadmap.json."
                )
                
                # Fetch text response from agent asynchronously
                agent_response = await response.text()
                
                print("\n==================================================")
                print("         Career Roadmap Agent Response            ")
                print("==================================================")
                print(agent_response)
                print("==================================================\n")

        except Exception as e:
            # Catch exceptions during the API call and fallback to local mode
            logger.error(f"Error during agent execution: {e}. Falling back to offline mode.")
            use_agent = False

    if not use_agent:
        logger.info("Running Career Roadmap Agent in local mode...")
        try:
            # Load input gap data from local file
            gap_data = read_gap_analysis("gap_analysis.json")
            
            # Generate the learning roadmap using offline template logic
            roadmap = generate_local_roadmap(gap_data)
            
            # Save the computed roadmap data to file
            save_result = save_career_roadmap(roadmap, "career_roadmap.json")
            
            # Output the outcome summary in a reader-friendly format
            print("\n==================================================")
            print("      Career Roadmap Analysis (Local Mode)        ")
            print("==================================================")
            print(f"Target Role: {roadmap['target_role']}")
            print("\nMissing Skills Learning Priority & Resources:")
            for item in roadmap["missing_skills_analysis"]:
                print(f"\n  Priority {item['priority']}: {item['skill']}")
                print(f"    Estimated Time: {item['estimated_time_to_learn']}")
                print("    Recommended Free Resources:")
                for r in item["free_resources"]:
                    print(f"      - {r['name']} ({r['type']})")
                    print(f"        URL: {r['url']}")
            
            print("\nWeek-by-Week Learning Plan Preview:")
            for w in roadmap["week_by_week_plan"][:4]:
                print(f"  Week {w['week']}: Topics: {', '.join(w['topics'])}")
                print(f"    Resources: {', '.join(w['resources'])}")
            if len(roadmap["week_by_week_plan"]) > 4:
                print("  ... [See career_roadmap.json for complete roadmap weeks]")
                
            print("\n--------------------------------------------------")
            print(save_result)
            print("==================================================\n")
        except Exception as e:
            logger.error(f"Failed to execute local roadmap analysis: {e}")
            print(f"\n[ERROR] Career Roadmap Agent failed to execute: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
