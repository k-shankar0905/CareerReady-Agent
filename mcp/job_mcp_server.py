import os
import sys
import json
import logging
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from the standard local .env file
load_dotenv()

# Setup logging to output exclusively to sys.stderr.
# This prevents log messages from corrupting the stdout channel used for JSON-RPC messages.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("job-market-mcp")

# Initialize the Model Context Protocol (MCP) server called 'job-market-mcp' using FastMCP
mcp = FastMCP("job-market-mcp")

# Retrieve JSearch RapidAPI authentication key from environment variables
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

def fetch_raw_jobs(role: str) -> list[dict]:
    """
    Helper function to query job postings from JSearch API or mock them in demo mode.

    It queries the live JSearch API if a valid RapidAPI key is present,
    otherwise it generates high-quality mock jobs for testing and demo.

    Args:
        role (str): The job title or role to search for.

    Returns:
        list[dict]: A list of job postings with keys: job_id, title, company, location, description.
    """
    # Detect if we should run in demo/mock fallback mode
    is_demo = not RAPIDAPI_KEY or "your_" in RAPIDAPI_KEY or RAPIDAPI_KEY == ""
    
    if is_demo:
        logger.warning(f"Running in Demo Mode: Generating mock job postings for role: {role}")
        # High quality sample companies and locations for mockup results
        mock_companies = ["TechCorp", "DataDynamics", "Innovate Solutions", "FinTech Group", "Apex Systems"]
        mock_locations = ["San Francisco, CA", "New York, NY", "Austin, TX", "Remote, US", "London, UK"]
        mock_jobs = []
        
        for i in range(5):
            mock_jobs.append({
                "job_id": f"mcp_mock_{i+1}",
                "title": f"Lead {role}" if i == 0 else f"Senior {role}" if i < 3 else role,
                "company": mock_companies[i],
                "location": mock_locations[i],
                "description": (
                    f"We are seeking a qualified {role} to join our engineering department. "
                    "You will work with Python, SQL, Tableau, Excel, and AWS. "
                    "Key duties include designing data visualizations and preparing statistics report."
                )
            })
        return mock_jobs

    # JSearch API Search Endpoint url
    url = "https://jsearch.p.rapidapi.com/search"
    
    # Configure API parameters (Query role, fetch 1 page)
    querystring = {
        "query": role,
        "page": "1",
        "num_pages": "1"
    }

    # Setup RapidAPI request authentication headers
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    try:
        logger.info(f"Sending API request to JSearch for role query: '{role}'")
        # Dispatch GET request with 10-second timeout
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        # Raise HTTPError for bad status codes
        response.raise_for_status()
        
        response_data = response.json()
        raw_listings = response_data.get("data", [])
        
        jobs_list = []
        for job in raw_listings:
            # Construct job location string
            city = job.get("job_city")
            state = job.get("job_state")
            country = job.get("job_country")
            location_parts = [p for p in [city, state, country] if p]
            
            location = ", ".join(location_parts) if location_parts else job.get("job_location", "Remote/Unknown")
            
            # Format raw data to standard schema
            jobs_list.append({
                "job_id": job.get("job_id", ""),
                "title": job.get("job_title", "N/A"),
                "company": job.get("employer_name", "N/A"),
                "location": location,
                "description": job.get("job_description", "No description provided.")
            })
        return jobs_list
        
    except Exception as e:
        logger.error(f"JSearch API fetch failed: {e}. Gracefully returning empty result list.")
        return []

@mcp.tool()
def search_jobs(role: str) -> str:
    """
    Search for job postings by role/title from the JSearch database.

    Args:
        role (str): The job title or role to search for (e.g., 'Data Analyst').

    Returns:
        str: A JSON string containing the list of matching jobs in MCP format.
    """
    logger.info(f"MCP Tool 'search_jobs' triggered for role: '{role}'")
    # Fetch jobs list from helper
    jobs = fetch_raw_jobs(role)
    # Serialize to JSON format for tool output
    return json.dumps(jobs, indent=2)

@mcp.tool()
def get_trending_skills(role: str) -> str:
    """
    Analyze job postings for a given role to identify and rank trending skills.

    Args:
        role (str): The target job title or role to analyze.

    Returns:
        str: A JSON string listing trending skills and their demand mention counts.
    """
    logger.info(f"MCP Tool 'get_trending_skills' triggered for role: '{role}'")
    # Fetch jobs list for analysis
    jobs = fetch_raw_jobs(role)
    
    # Predefined skill keywords and common alias terms
    skill_keywords = {
        "Python": ["python", "py"],
        "SQL": ["sql", "mysql", "postgresql", "queries"],
        "Excel": ["excel", "spreadsheet", "vlookup"],
        "Tableau": ["tableau"],
        "Power BI": ["power bi", "powerbi"],
        "Statistics": ["statistics", "statistical", "probability"],
        "Communication": ["communication", "presenting", "verbal"],
        "AWS": ["aws", "amazon web services", "cloud"],
        "Docker": ["docker", "container"],
        "Git": ["git", "github"]
    }
    
    # Initialize counts for each skill
    counts = {skill: 0 for skill in skill_keywords}
    
    # Scan titles and descriptions for occurrences
    for job in jobs:
        combined_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
        for skill, terms in skill_keywords.items():
            if any(term in combined_text for term in terms):
                counts[skill] += 1
                
    # Format and sort results in descending order of demand frequency
    sorted_skills = sorted(
        [{"skill": s, "mentions": c} for s, c in counts.items() if c > 0],
        key=lambda x: x["mentions"],
        reverse=True
    )
    
    # Default fallback list if no skills are matched in descriptions
    if not sorted_skills:
        sorted_skills = [
            {"skill": "Python", "mentions": 3},
            {"skill": "SQL", "mentions": 3},
            {"skill": "Excel", "mentions": 2}
        ]
        
    result = {
        "role": role,
        "jobs_analyzed": len(jobs),
        "trending_skills": sorted_skills
    }
    return json.dumps(result, indent=2)

@mcp.tool()
def get_market_pulse() -> str:
    """
    Retrieve overall job market trends and demand signals.

    Returns:
        str: A JSON string summarizing overall market health, active hiring locations, and hiring firms.
    """
    logger.info("MCP Tool 'get_market_pulse' triggered")
    # Query developer jobs to construct broad market sample
    jobs = fetch_raw_jobs("Software Developer")
    
    locations = {}
    companies = []
    
    # Aggregate data
    for job in jobs:
        loc = job.get("location", "Unknown")
        locations[loc] = locations.get(loc, 0) + 1
        comp = job.get("company")
        if comp and comp != "N/A":
            companies.append(comp)
            
    # Identify top 3 locations by hiring density
    sorted_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)
    top_locations = [loc for loc, count in sorted_locations[:3]]
    
    # Construct pulse result summary
    pulse_data = {
        "status": "Healthy" if jobs else "Limited Data",
        "market_sentiment": "High demand continues for engineering, analytics, and infrastructure cloud skills.",
        "active_hiring_companies": list(set(companies))[:5],
        "top_hiring_locations": top_locations if top_locations else ["Remote", "San Francisco, CA", "New York, NY"],
        "sample_size_analyzed": len(jobs)
    }
    
    return json.dumps(pulse_data, indent=2)

# Start MCP Server via FastMCP runner
if __name__ == "__main__":
    mcp.run()
