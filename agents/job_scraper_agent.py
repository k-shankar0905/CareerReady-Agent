import os
import json
import logging
import requests
from dotenv import load_dotenv
from google.antigravity import Agent, LocalAgentConfig

# Configure logging for the agent
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_jobs_from_jsearch(role: str, rapidapi_key: str) -> list[dict]:
    """
    Connects to the JSearch API on RapidAPI to search for real job postings
    and extracts job title, company, location, and full job description.

    Args:
        role (str): The job role or title to search for (e.g. "Data Analyst").
        rapidapi_key (str): The RapidAPI API key for authentication.

    Returns:
        list[dict]: A list of job posting dictionaries.
    
    Raises:
        requests.exceptions.RequestException: If the API call fails.
        ValueError: If the API returns an invalid response.
    """
    # JSearch search endpoint
    url = "https://jsearch.p.rapidapi.com/search"
    
    # Search parameters:
    # - query: Search term (e.g., "Data Analyst")
    # - page: Page number of search results (1)
    # - num_pages: Number of pages to retrieve (1)
    querystring = {
        "query": role,
        "page": "1",
        "num_pages": "1"
    }

    # Setup headers required by RapidAPI
    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    logger.info(f"Sending request to JSearch API for role: '{role}'")
    
    try:
        # Send HTTP GET request to JSearch endpoint with a 15-second timeout
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        
        # Raise HTTP error if status code is not 200 OK
        response.raise_for_status()
        
        response_data = response.json()
        
        # Validate structure of JSearch response
        if response_data.get("status") != "OK" or "data" not in response_data:
            raise ValueError("JSearch API returned an unsuccessful status or missing data field.")
        
        raw_jobs = response_data["data"]
        extracted_jobs = []
        
        for job in raw_jobs:
            # Build location string dynamically using available fields
            city = job.get("job_city")
            state = job.get("job_state")
            country = job.get("job_country")
            location_parts = [p for p in [city, state, country] if p]
            
            location = ", ".join(location_parts) if location_parts else job.get("job_location", "Remote/Unknown")
            
            # Format and clean the job data
            job_info = {
                "job_id": job.get("job_id", ""),
                "title": job.get("job_title", "N/A"),
                "company": job.get("employer_name", "N/A"),
                "location": location,
                "description": job.get("job_description", "No description provided.")
            }
            extracted_jobs.append(job_info)
            
        logger.info(f"Successfully fetched and extracted {len(extracted_jobs)} job postings.")
        return extracted_jobs

    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP request to JSearch API failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error parsing JSearch API response: {e}")
        raise

def get_mock_jobs(role: str) -> list[dict]:
    """
    Generates high-quality mock job listings to allow the agent to run and
    demonstrate functionality in demo mode when no RapidAPI key is provided.

    Args:
        role (str): The requested job role.

    Returns:
        list[dict]: A list of 10 mocked job postings.
    """
    logger.warning("Running in Demo Mode: Generating mock job postings.")
    
    mock_companies = ["TechCorp", "DataDynamics", "Innovate Solutions", "FinTech Group", "Global AI Solutions", "Apex Systems", "CloudScale", "QuantLab", "FutureVision", "CyberSec Inc"]
    mock_locations = ["San Francisco, CA, US", "New York, NY, US", "Austin, TX, US", "Chicago, IL, US", "Seattle, WA, US", "Remote, US", "London, UK", "Toronto, ON, CA", "Boston, MA, US", "Denver, CO, US"]
    
    mock_jobs = []
    for i in range(10):
        mock_jobs.append({
            "job_id": f"mock_job_{i+1}",
            "title": f"Senior {role}" if i % 2 == 0 else f"Junior {role}",
            "company": mock_companies[i],
            "location": mock_locations[i],
            "description": (
                f"We are looking for a talented {role} to join our growing team. "
                "In this role, you will analyze datasets, build models, collaborate with "
                "stakeholders, and drive data-driven decision making across the organization.\n\n"
                "Requirements:\n"
                "- 2+ years of experience in similar roles\n"
                "- Strong familiarity with SQL, Python, and BI tools\n"
                "- Outstanding communication and problem-solving skills"
            )
        })
    return mock_jobs

async def main(role_input: str = None):
    """
    Main asynchronous CLI driver for the Job Scraper Agent.
    Prompts the user for a job role (if not supplied programmatically), configures the Google ADK Agent,
    executes the job search, and saves results to job_results.json.
    """
    # Security: Verify that .env file exists before running
    if not os.path.exists(".env"):
        print("[ERROR] Security check failed: .env file does not exist in the root directory.")
        raise FileNotFoundError("Missing required .env configuration file in the project root.")

    # Load env variables from .env file
    load_dotenv()
    
    # Security: Ensure all API keys are loaded ONLY from .env file (no hardcoding)
    gemini_key = os.getenv("GEMINI_API_KEY")
    rapidapi_key = os.getenv("RAPIDAPI_KEY")
    
    # Check if Gemini key exists (required to run the ADK Agent)
    if not gemini_key:
        print("\n[ERROR] GEMINI_API_KEY is not set in your .env file.")
        print("Please copy .env.example to .env and add your Google Gemini API key.")
        raise ValueError("Missing GEMINI_API_KEY in environment variables.")

    # Prompt user for the job role to scrape if not passed programmatically
    if role_input is None:
        print("\n==================================================")
        print("      CareerReady - Job Scraper Agent CLI         ")
        print("==================================================")
        role_input = input("Enter the job role to search for (e.g., 'Data Analyst'): ").strip()
    else:
        role_input = role_input.strip()
    
    # Security: Input validation (check not empty and not too long)
    if not role_input:
        print("[ERROR] Input validation failed: Job role cannot be empty.")
        raise ValueError("Invalid Input: Job role cannot be empty.")
        
    if len(role_input) > 100:
        print("[ERROR] Input validation failed: Job role exceeds maximum length of 100 characters.")
        raise ValueError("Invalid Input: Job role exceeds maximum length of 100 characters.")

    import re
    # Security: Input validation (check for safe characters to prevent code injection/API abuse)
    if not re.match(r"^[a-zA-Z0-9\s\-\.\,\(\)\&]+$", role_input):
        print("[ERROR] Input validation failed: Job role contains invalid or unsafe characters.")
        raise ValueError("Invalid Input: Job role contains invalid characters.")

    # Check if JSearch API Key is provided or placeholder
    is_demo = not rapidapi_key or "your_" in rapidapi_key or rapidapi_key == ""

    # Security: Rate limiting check (throttling active scraping to avoid RapidAPI abuse)
    if not is_demo:
        rate_limit_file = ".job_scraper_rate_limit"
        import time
        if os.path.exists(rate_limit_file):
            try:
                with open(rate_limit_file, "r") as rlf:
                    last_run = float(rlf.read().strip())
                time_passed = time.time() - last_run
                if time_passed < 10:
                    wait_time = 10 - time_passed
                    logger.warning(f"Security/Rate Limit: API calls are throttled. Please wait {wait_time:.1f} seconds. Sleeping...")
                    time.sleep(wait_time)
            except Exception as e:
                logger.warning(f"Rate limiting check warning: {e}")

        # Update the timestamp file
        try:
            with open(rate_limit_file, "w") as rlf:
                rlf.write(str(time.time()))
        except Exception as e:
            logger.warning(f"Rate limiting timestamp update failed: {e}")

    # Define the local tool that the agent can execute
    def search_jobs(query: str) -> str:
        """
        Agent tool to search for job postings and save them to a file.
        
        Args:
            query (str): The search query or job role.
            
        Returns:
            str: Status message of the search results.
        """
        try:
            if is_demo:
                jobs = get_mock_jobs(query)
            else:
                jobs = fetch_jobs_from_jsearch(query, rapidapi_key)
                
            # If no results found and not in demo mode
            if not jobs:
                return f"No jobs found for role: '{query}'."

            # Save extracted job listings to job_results.json
            with open("job_results.json", "w", encoding="utf-8") as f:
                json.dump(jobs, f, indent=4, ensure_ascii=False)
                
            return f"Successfully retrieved {len(jobs)} jobs for '{query}' and saved to job_results.json."
            
        except Exception as e:
            logger.error(f"Error executing search_jobs tool: {e}")
            return f"Failed to complete job search due to error: {str(e)}"

    # Configure the local Agent using the Google ADK configurations
    logger.info("Initializing Google Antigravity Agent...")
    config = LocalAgentConfig(
        system_instructions=(
            "You are the Job Scraper Agent, part of the CareerReady agent team.\n"
            "Your main role is to coordinate job scraping requests.\n"
            "Use the `search_jobs` tool to look up real-time postings for the user's requested role.\n"
            "After the tool returns, summarize the outcome for the user. Mention how many jobs "
            "were found, some company names, and let them know the details are saved in `job_results.json`."
        ),
        tools=[search_jobs],
        api_key=gemini_key
    )

    try:
        # Run the agent in an async context
        async with Agent(config) as agent:
            print(f"\n[Agent] Starting job search for '{role_input}'...")
            
            # Start conversation chat session with the agent
            response = await agent.chat(f"Search for job postings for the role: {role_input}")
            
            # Get and display the agent response text
            agent_response = await response.text()
            print("\n==================================================")
            print("                Agent Response                    ")
            print("==================================================")
            print(agent_response)
            print("==================================================\n")
            
    except Exception as e:
        logger.error(f"An unexpected error occurred during agent execution: {e}")
        print(f"\n[ERROR] Agent failed to execute: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
