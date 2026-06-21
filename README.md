# CareerReady Agent Project

CareerReady is a suite of intelligent command-line agents designed to streamline job search, skill gap analysis, and career readiness assessment. It combines the power of the Google Antigravity SDK (Gemini API) and external APIs to provide personalized career insights.

---

## Implemented Agents

### 1. Job Scraper Agent (`agents/job_scraper_agent.py`)

#### Description
The **Job Scraper Agent** searches for active job listings matching a user-specified job role (e.g., "Data Analyst"). It fetches real-time postings using the JSearch API via RapidAPI. If no RapidAPI key is provided, it automatically falls back to generating high-quality mock listings for testing and demo purposes.

#### Input
* **CLI Input**: Job role or title (e.g., `"Data Analyst"`).
* **Environment Variables**:
  * `GEMINI_API_KEY`: Required to execute the Google Antigravity Agent.
  * `RAPIDAPI_KEY`: Optional. Required to fetch live data; if missing, runs in demo/mock mode.

#### Output
* **Console**: A high-level response from the Gemini-powered agent summarizing the search result, including total jobs found and examples of hiring companies.
* **File Output**: Saves structured job listings details to `job_results.json`.

---

### 2. Gap Analyzer Agent (`agents/gap_analyzer_agent.py`)

#### Description
The **Gap Analyzer Agent** assesses user readiness for a target job role. It reads requirements from `skills_analysis.json`, prompts the user for their current skills, compares them, calculates a weighted readiness score out of 100, identifies missing skills (ranked by importance), and saves the results. It has a Gemini-powered Agent mode for recommending custom learning plans, and an offline local mode fallback.

#### Input
* **CLI Input**: Comma-separated list of skills (e.g., `"Python, Excel, Tableau"`).
* **File Input**: [skills_analysis.json](file:///c:/Users/yamuna/.antigravity-ide/CareerReady-Agent/skills_analysis.json) defining required skills and their importance ("high", "medium", "low").
* **Environment Variables**:
  * `GEMINI_API_KEY`: Optional. Used for generating personalized learning recommendations via Gemini; falls back to offline local CLI analysis if not set.

#### Output
* **Console**: A formatted summary displaying the target role, readiness score status (e.g., `"You are 65% ready for Data Analyst role"`), matched skills, and missing skills ranked by importance.
* **File Output**: Saves the full breakdown structure to `gap_analysis.json`.

---

### 3. Nudge Agent (`agents/nudge_agent.py`)

#### Description
The **Nudge Agent** tracks the user's weekly learning progress against a structured career roadmap defined in `career_roadmap.json`. It prompts the user for what they planned to learn, checks if it was completed, updates progress in `progress.json`, gives motivational messages (including why the skill is important if they failed to complete it), and displays the overall roadmap progress percentage.

#### Input
* **CLI Input**:
  * Planned learning goal (e.g., `"Python Basics"`).
  * Completion status (`"yes"`/`"no"`).
* **File Input**: [career_roadmap.json](file:///c:/Users/yamuna/.antigravity-ide/CareerReady-Agent/career_roadmap.json) defining weekly goals, descriptions, and importance.
* **Environment Variables**:
  * `GEMINI_API_KEY`: Optional. Used for generating personalized learning nudges and advice; falls back to offline local CLI analysis if not set.

#### Output
* **Console**:
  * Congratulates the user and displays next week's goal on completion.
  * Motivates the user and displays the skill importance if not completed.
  * Shows the overall roadmap completion percentage.
* **File Output**: Updates and saves progress status to `progress.json`.

---

## Model Context Protocol (MCP) Servers

### Job Market MCP Server (`mcp/job_mcp_server.py`)

#### Description
An MCP-compliant server called **`job-market-mcp`** implemented using the standard Python `FastMCP` framework. It exposes three tools to any host application (such as Claude Desktop or other Model Context Protocol clients) for querying the job market in real time.

#### Exposed Tools
1. **`search_jobs(role: str)`**
   * **Purpose**: Searches for active job postings by job role from the JSearch database.
   * **Returns**: JSON string list of job details in MCP tool response format.
2. **`get_trending_skills(role: str)`**
   * **Purpose**: Analyzes job listings text to identify and rank trending technical and soft skills for a given role.
   * **Returns**: JSON string listing trending skills and count statistics.
3. **`get_market_pulse()`**
   * **Purpose**: Fetches general postings sample to extract broad hiring hubs, top hiring companies, and market demand sentiments.
   * **Returns**: JSON summary of market health parameters.

---

## Dependencies Required

The project requires **Python 3.8+** and the following dependencies:

* **`requests`**: For contacting the external JSearch API.
* **`python-dotenv`**: For loading credentials from a local `.env` configuration file.
* **`mcp`** (FastMCP SDK): Enables Model Context Protocol server capabilities.
* **`google-antigravity`** (Optional/Standard SDK): Enables agent-based orchestration and LLM chat execution.

Install the python dependencies using `pip`:
```bash
pip install requests python-dotenv "mcp[cli]"
```

---

## Project Setup

1. **Clone/Open the Workspace** inside the IDE.
2. **Configure Environment Variables**:
   * Copy the `.env.example` file to create a `.env` file in the project root:
     ```bash
     cp .env.example .env
     ```
   * Open the `.env` file and insert your API keys:
     ```env
     GEMINI_API_KEY=your_actual_gemini_api_key
     RAPIDAPI_KEY=your_actual_rapidapi_key
     ```

---

## How to Run the Project

### 1. Run the Job Scraper Agent
To scrape job postings for a role (e.g., "Data Analyst") and save them to `job_results.json`:
```bash
python agents/job_scraper_agent.py
```
*Follow the interactive prompt to type your target role.*

### 2. Run the Gap Analyzer Agent
To analyze your skills gap against the market requirements loaded from `skills_analysis.json`:
```bash
python agents/gap_analyzer_agent.py
```
*Follow the prompt to input your current skills (e.g., `Python, Excel, Tableau`).*

### 3. Run the Nudge Agent
To track your learning progress against your roadmap:
```bash
python agents/nudge_agent.py
```
*Follow the prompt to enter what you planned to learn and if you completed it.*

### 4. Run the Job Market MCP Server
To boot up the Model Context Protocol stdio transport server:
```bash
python mcp/job_mcp_server.py
```
*Note: This server communicates over standard input/output (stdio) and should be registered in your client configuration (e.g., `claude_desktop_config.json`).*
