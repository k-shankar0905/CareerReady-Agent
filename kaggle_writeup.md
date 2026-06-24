# CareerReady Agent — Know Your Gap. Close It. Get Hired.

## Subtitle: A multi-agent AI system that tells you exactly what is stopping you from getting hired

---

## 1. Executive Summary & Abstract
In the modern, hyper-competitive job market, job seekers face a dual challenge: the landscape of technical competencies changes faster than formal academic curricula can adapt, and applicant tracking systems (ATS) filter out candidates who fail to match specific keyword criteria. As a result, candidates often spend months sending generic resumes to black-box application portals, wasting time on generic online courses that do not target their specific skill deficiencies, and losing motivation due to a lack of structured progression.

Our submission, the **CareerReady Agent**, is a modular, cooperative multi-agent AI platform designed to completely automate and personalize the career preparation lifecycle. Utilizing the **Google Antigravity SDK (ADK)** for advanced agentic orchestration, standard **Model Context Protocol (MCP)** for cross-application utility, and **Streamlit** for interactive visualizations, CareerReady Agent replaces generic advice with data-driven, hyper-personalized career intelligence. The system consists of six specialized, autonomous agents that collaborate through structured data files (`.json`) to scrape job listings, extract skill weights, analyze individual gaps, produce step-by-step roadmaps, provide accountability nudges, and compile tailored ATS-friendly resumes. This write-up details the architecture, design decisions, technical implementation details, and our experience "vibe coding" this solution to completion with the **Antigravity** AI assistant.

---

## 2. Problem Statement
The transition from being a student or career switcher to securing a professional position is plagued by structural inefficiencies:

1. **The Skill-Market Mismatch (Moving Target)**:
   Job descriptions are written by a combination of hiring managers, HR specialists, and recruiting teams. The resulting requirements are often unstructured, localized, and dynamic. A "Data Analyst" position at a financial institution may heavily prioritize SQL and Excel, whereas a similar title at a tech firm may demand Python, Tableau, and AWS. Static guides or general curriculums fail to capture this real-time variance.

2. **The Paradox of Information Overload**:
   When candidates identify a skill gap, they are met with thousands of tutorials, bootcamps, and degree programs. Determining which resources are high-quality, free, and correctly prioritized is a time-consuming chore. Many candidates attempt to learn advanced topics (e.g., Machine Learning) before mastering the foundational prerequisites (e.g., SQL and basic programming), leading to frustration and burnout.

3. **The ATS (Applicant Tracking System) Black Box**:
   Over 90% of medium-to-large enterprises utilize ATS software to screen resumes before a human recruiter ever views them. These systems rely on keyword parsing. If a candidate possesses the requisite capabilities but fails to phrase them in the exact terminology expected by the ATS, their application is rejected. Conversely, blindly stuffing keywords leads to human rejection in later rounds.

4. **The Accountability Deficit**:
   Self-paced online learning suffers from extremely low completion rates (often under 10%). Without regular progress checks, milestones, and contextual motivation (understanding *why* a specific skill is being learned in terms of market value), learners lose momentum.

---

## 3. Why Agents?
A traditional software approach or a single-prompt LLM execution is insufficient to solve this problem:

* **Limits of Single-Prompt Engineering**:
  A single LLM prompt trying to ingest thousands of job descriptions, evaluate a user's skills, formulate a roadmap, and write a resume would inevitably run into context length limits, hallucinations, and formatting breakdowns. The task requires reasoning over separate phases.
* **Separation of Concerns**:
  By breaking down the pipeline into six distinct agents, each with a narrow set of tools, system instructions, and target output models, we achieve far higher reliability. For example, the `Job Scraper Agent` focuses strictly on retrieval; the `Skills Extractor Agent` focuses on naming-normalization and frequency counting; the `Gap Analyzer Agent` handles math-based weighted scores and direct comparisons.
* **State Persistence via Files**:
  Rather than maintaining a massive, fragile in-memory conversation history, the agents communicate by reading and writing structured JSON files (`job_results.json`, `skills_analysis.json`, `gap_analysis.json`, `career_roadmap.json`, `progress.json`). This design provides multiple benefits:
  1. **Auditability**: Developers and users can inspect the intermediate states of the system.
  2. **Modularity**: Any single agent can be rerun, replaced, or updated without breaking the rest of the pipeline.
  3. **Robustness**: If a network request fails or an API limit is reached in one stage, the system does not lose data from previous stages.
  4. **Hybrid Execution (Deterministic Fallbacks)**: When an API key is missing or an agent call fails, the system can gracefully fall back to local, deterministic Python code that parses files locally, ensuring 100% uptime.

---

## 4. Solution Overview
The CareerReady Agent platform is structured as an integrated, multi-stage pipeline:

```
[User Job Role Input]
       │
       ▼
 ┌───────────┐      job_results.json      ┌───────────────┐
 │1. Scraper │ ─────────────────────────> │ 2. Extractor  │
 └───────────┘                            └───────────────┘
                                                  │
                                                  │ skills_analysis.json
                                                  ▼
 ┌───────────┐      gap_analysis.json     ┌───────────────┐
 │4. Roadmap │ <───────────────────────── │3.Gap Analyzer │ <── [User Skill Input]
 └───────────┘                            └───────────────┘
       │                                          │
       │ career_roadmap.json                      │ gap_analysis.json
       ▼                                          ▼
 ┌───────────┐      progress.json         ┌───────────────┐
 │ 5. Nudge  │ ─────────────────────────> │  6. Resume    │ ──> [resume_output.txt]
 └───────────┘                            └───────────────┘
```

The system takes a target job role from the user, queries live job market databases, normalizes the requirements, calculates where the candidate stands, builds a week-by-week learning pathway with free links, holds the candidate accountable through interactive nudges, and automatically drafts an ATS-optimized resume emphasizing their market-ready skills.

---

## 5. Architecture: Deep Dive into the 6-Agent Ecosystem

### 5.1. Job Scraper Agent (`agents/job_scraper_agent.py`)
* **Objective**: Ingest real-time market data for the user's targeted role.
* **Core Logic**: Prompts the user via CLI for a job role (e.g., "Data Analyst"). It contains a custom tool, `search_jobs`, which checks the environment for a `RAPIDAPI_KEY`. If present, it executes an HTTP GET request to the JSearch API to retrieve active listings (job title, employer name, job city/state/country, and full descriptions). If the key is missing, it triggers `get_mock_jobs()`, generating 10 realistic, detailed mock job postings matching the requested role.
* **Output**: Writes structured listings directly to `job_results.json`.

### 5.2. Skills Extractor Agent (`agents/skills_extractor_agent.py`)
* **Objective**: Parse unstructured text descriptions into a clean, normalized skills dictionary.
* **Core Logic**: Reads the job descriptions from `job_results.json`. In Agent Mode (Gemini-powered), it loops through all listings and extracts technical and soft skills, normalizing synonyms (e.g., mapping "python scripting", "python language", and "py" to a single standardized key: `"Python"`). It then counts frequencies across all listings to calculate what percentage of job postings demand each skill. In local fallback mode, it uses a predefined dictionary of core industry skills and regular expressions to count occurrences.
* **Output**: Writes the results sorted by frequency (descending) to `skills_analysis.json`.

### 5.3. Gap Analyzer Agent (`agents/gap_analyzer_agent.py`)
* **Objective**: Perform a direct audit of the candidate's skills against current market needs.
* **Core Logic**: Prompts the user for a list of their current skills (comma-separated). It loads `skills_analysis.json` and performs a case-insensitive comparison. Crucially, it calculates a weighted readiness score out of 100 based on the importance levels of the market skills:
  - **High Importance** (represented in >60% of postings or explicitly marked): Weight = 3.
  - **Medium Importance** (30% - 60% of postings): Weight = 2.
  - **Low Importance** (<30% of postings): Weight = 1.
  $$\text{Readiness Score} = \left( \frac{\sum \text{Weights of Matched Skills}}{\sum \text{Weights of All Required Skills}} \right) \times 100$$
  It also identifies missing skills and ranks them by importance.
* **Output**: Writes the detailed metric breakdown to `gap_analysis.json`.

### 5.4. Career Roadmap Agent (`agents/career_roadmap_agent.py`)
* **Objective**: Plan an optimized learning curriculum to bridge the identified gap.
* **Core Logic**: Reads `gap_analysis.json` to identify missing skills. In Agent Mode, the Gemini model uses its internal knowledge base to suggest specific, high-quality, free resources (official documentation, top-rated free YouTube tutorials, free Coursera/edX programs) with URLs and estimated hours to learn. It structures these into a week-by-week learning syllabus, sorting skills so that fundamental requirements are tackled first. If offline, it uses a localized resource library mapping common technical skills (Power BI, Python, SQL, Tableau, FastAPI, Docker, PostgreSQL) to static resources.
* **Output**: Saves the structured path to `career_roadmap.json`.

### 5.5. Nudge Agent (`agents/nudge_agent.py`)
* **Objective**: Provide motivational reinforcement and check off weekly learning goals.
* **Core Logic**: An interactive tracker. It loads `career_roadmap.json` and `progress.json` (creating a new one if it doesn't exist). It displays the weekly milestones to the user and asks what they planned to learn and whether they completed it. The agent matches the user's input to the correct week in the roadmap using substring and keyword matching. If the goal was completed, it adds the week number to `progress.json`, congratulates the user, and presents the next week's goal. If not completed, it leverages Gemini (or a fallback local template) to provide motivational advice, referencing the specific "importance" field from the roadmap to remind the user of the skill's direct monetary/career value.
* **Output**: Updates the progress tracking state in `progress.json`.

### 5.6. Resume Generator Agent (`agents/resume_generator_agent.py`)
* **Objective**: Assemble a professionally tailored, ATS-friendly plain-text resume.
* **Core Logic**: Prompts the user for personal info (Full name, email, phone, education, experience summary). It reads `gap_analysis.json` to extract matched skills and missing skills. It then generates a structured text resume, dynamically inserting matched skills into the Core Proficiencies section and placing remaining gaps in a "Professional Development Areas" section (showing employers a proactive learning path). The AI-driven mode formats a cohesive Professional Summary that highlights alignment with the target role.
* **Output**: Writes the final plain-text resume to `resume_output.txt`.

---

## 6. Technical Implementation details

### 6.1. Google Antigravity SDK Integration
The multi-agent system is built on top of the Google Antigravity SDK (`google-antigravity`). This SDK provides a clean, native interface to Gemini models, supporting features like system instructions, active tool registration, chat management, and local configuration.

An example of our implementation of the `LocalAgentConfig` setup for the **Gap Analyzer Agent**:

```python
from google.antigravity import Agent, LocalAgentConfig

# Tools are native Python functions with detailed docstrings
def analyze_skills(user_input: str) -> str:
    """
    Analyzes the skill gap between user input and market requirements,
    saves the results, and returns a raw representation for the agent.
    """
    results = perform_local_analysis(user_input)
    return json.dumps(results, indent=2)

config = LocalAgentConfig(
    system_instructions=(
        "You are the Gap Analyzer Agent, part of the CareerReady agent team.\n"
        "Your goal is to guide the user on their readiness for the target role.\n"
        "1. Run the `analyze_skills` tool with the user's input skills.\n"
        "2. Parse the JSON results returned by the tool.\n"
        "3. Present the analysis beautifully..."
    ),
    tools=[analyze_skills],
    api_key=gemini_key
)
```

The async context manager (`async with Agent(config) as agent:`) ensures clean initialization and teardown of connections. The model has direct access to Python functions, calling them dynamically when it needs to inspect the local filesystem or update state.

### 6.2. Model Context Protocol (MCP) Server
To extend the utility of the CareerReady ecosystem beyond local CLI execution, we implemented an MCP-compliant server using the Python `FastMCP` framework (`mcp/job_mcp_server.py`). The Model Context Protocol is an open standard that allows host applications (such as Claude Desktop, Cursor, or custom corporate platforms) to securely interact with external tools and data sources.

The MCP server exposes three tools:
1. **`search_jobs(role: str) -> str`**: Fetches active job listings from the database or API.
2. **`get_trending_skills(role: str) -> str`**: Analyzes listings to identify and count skill occurrences.
3. **`get_market_pulse() -> str`**: Returns general hiring health statistics (top companies, active hubs, market sentiment).

Here is a snippet from our MCP server code:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("job-market-mcp")

@mcp.tool()
def search_jobs(role: str) -> str:
    """
    Search for job postings by role/title from the JSearch database.
    """
    jobs = fetch_raw_jobs(role)
    return json.dumps(jobs, indent=2)
```

### 6.3. Agent Skills & Local Tool Design
In the Google Antigravity SDK, agent tools act as "skills." The LLM reads the function signatures and docstrings to understand what arguments to pass and what data will be returned. We carefully structured our tools to return clean JSON strings. This keeps the token usage highly optimized and allows the agent to parse tool outputs programmatically before framing its chat responses.

### 6.4. Security Features & Design Constraints
Deploying agentic systems requires strict security measures, especially when exposing local filesystems and running external code. The CareerReady Agent system incorporates several security best practices:

1. **Stdout/Stderr Separation in MCP**:
   In `mcp/job_mcp_server.py`, the Model Context Protocol uses the standard output (`stdout`) stream for JSON-RPC message passing. If python loggers or print statements write to `stdout`, the host application will fail to parse the messages, resulting in crashes. To resolve this, we redirected all python logging explicitly to `sys.stderr`:
   ```python
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       stream=sys.stderr
   )
   ```
2. **Credential Isolation**:
   API keys are never hardcoded. They are loaded at runtime using `dotenv` from an isolated, git-ignored `.env` file. A `.env.example` file is provided to guide users without exposing sensitive developer tokens.
3. **Graceful Local Fallback Bounds**:
   If an agent execution encounters an invalid or missing API key, it does not throw unhandled exceptions or expose stack traces. Instead, it catches the error and drops back to local Python logic. This ensures that the application remains functional even in offline environments.

---

## 7. How We Built It: Vibe Coding with Antigravity
The term "vibe coding" refers to the highly collaborative paradigm where human developers act as directors, setting the architecture, high-level objectives, and UX requirements, while an advanced AI pair programmer (in our case, the **Antigravity** coding assistant) handles the heavy lifting of code generation, testing, refactoring, and integration.

### Our Vibe Coding Workflow
1. **Defining the Architecture**:
   We started by sketching out the data schemas for the JSON exchange files. We aligned on a pipeline design where each agent’s output forms the input for the next. We explained this architecture to our Antigravity assistant.
2. **Incremental Scaffolding**:
   We prompted Antigravity to write the scaffolding for each agent file. Instead of writing monolithic scripts, we asked it to modularize the logic. Antigravity generated the skeleton, including clean imports, dotenv integration, logging configurations, helper methods, and main asynchronous execution loops.
3. **Refining the Fallback Logic**:
   A key goal was offline utility. We worked with Antigravity to design robust local fallbacks. For instance, when we asked Antigravity to build the `Career Roadmap Agent`, it suggested and implemented a static local dictionary of common tech skills and structured resource lists, ensuring that the tool could generate high-quality outputs even if the Gemini API key was missing.
4. **Testing and Commit Cycles**:
   Throughout development, we ran validation tests. After verified successes, we ran git command sequences directly through our workspace to commit and push changes:
   ```bash
   git add README.md
   git commit -m "Added README.md"
   git push
   ```
   This workflow let us focus on high-level orchestration while Antigravity ensured syntactical correctness and clean logging behavior.

---

## 8. Demo and Results
To evaluate the platform, we ran a full testing scenario targeting a **Data Analyst** role. Below are the key steps, inputs, and generated files showing how the multi-agent system performed.

### Step 1: Scrape Jobs
We ran the `job_scraper_agent.py` and requested the role `"Data Analyst"`. 
Since we did not specify a live RapidAPI key, the agent executed in demo mode, generating `job_results.json`. The output file contained 10 high-quality mock listings containing detailed descriptions:

```json
[
    {
        "job_id": "mock_job_1",
        "title": "Senior Data Analyst",
        "company": "TechCorp",
        "location": "San Francisco, CA, US",
        "description": "We are looking for a talented Data Analyst to join our growing team. In this role, you will analyze datasets, build models, collaborate with stakeholders, and drive data-driven decision making across the organization.\n\nRequirements:\n- 2+ years of experience in similar roles\n- Strong familiarity with SQL, Python, and BI tools\n- Outstanding communication and problem-solving skills"
    }
]
```

### Step 2: Extract Skills
We executed `skills_extractor_agent.py`. The agent read the listings, standardized the skills, and wrote the following ranked summary to `skills_analysis.json`:

```json
{
  "role": "Data Analyst",
  "skills": [
    { "name": "Python", "importance": "high" },
    { "name": "SQL", "importance": "high" },
    { "name": "Excel", "importance": "medium" },
    { "name": "Tableau", "importance": "medium" },
    { "name": "Power BI", "importance": "medium" },
    { "name": "Statistics", "importance": "medium" },
    { "name": "Communication", "importance": "low" }
  ]
}
```

### Step 3: Analyze the Skills Gap
We ran `gap_analyzer_agent.py`. We input our current skills as: `"Python, Excel, Tableau"`. The agent parsed our input, compared it with the required skills, and calculated a weighted readiness score:
* **Required Weights**: 
  - High (Python, SQL) = $2 \times 3 = 6$
  - Medium (Excel, Tableau, Power BI, Statistics) = $4 \times 2 = 8$
  - Low (Communication) = $1 \times 1 = 1$
  - **Total Weights** = 15
* **Matched Weights**:
  - Python (High) = 3
  - Excel (Medium) = 2
  - Tableau (Medium) = 2
  - **Total Matched** = 7
* **Readiness Score**: $\frac{7}{15} \times 100 \approx 47\%$

The agent generated `gap_analysis.json`:

```json
{
    "target_role": "Data Analyst",
    "user_skills": [
        "Python",
        "Excel",
        "Tableau"
    ],
    "readiness_score": "47%",
    "readiness_percentage": 47,
    "matched_skills": [
        { "name": "Python", "importance": "high" },
        { "name": "Excel", "importance": "medium" },
        { "name": "Tableau", "importance": "medium" }
    ],
    "skill_gap": [
        { "name": "SQL", "importance": "high" },
        { "name": "Power BI", "importance": "medium" },
        { "name": "Statistics", "importance": "medium" },
        { "name": "Communication", "importance": "low" }
    ]
}
```

### Step 4: Build Career Roadmap
We ran `career_roadmap_agent.py`. It ingested the gap analysis file and generated a targeted week-by-week curriculum saved to `career_roadmap.json`:

```json
{
    "target_role": "Data Analyst",
    "missing_skills_analysis": [
        {
            "skill": "SQL",
            "priority": 1,
            "estimated_time_to_learn": "2 weeks (15 hours)",
            "free_resources": [
                {
                    "name": "W3Schools SQL Tutorial",
                    "url": "https://www.w3schools.com/sql/",
                    "type": "Documentation"
                },
                {
                    "name": "SQL Tutorial for Beginners - YouTube",
                    "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
                    "type": "YouTube"
                }
            ]
        }
    ],
    "week_by_week_plan": [
        {
            "week": 1,
            "topics": [
                "Introduction to SQL",
                "Core concepts and basic setup of SQL"
            ],
            "resources": [
                "W3Schools SQL Tutorial"
            ]
        }
    ]
}
```

### Step 5: Accountability Tracking
We executed `nudge_agent.py` to check in on our progress.
* **CLI Prompt**: *What did you plan to learn this week?* -> `SQL`
* **CLI Prompt**: *Did you complete it? (yes/no):* -> `yes`

The nudge agent logged the completion, updated `progress.json` to show Week 1 as completed, calculated the overall progress percentage, and announced the next week's goal.

### Step 6: Generate Tailwind-Ready Resumes
We ran `resume_generator_agent.py`, entering our contact info and career summary. The agent read `gap_analysis.json` and compiled a tailored text file `resume_output.txt` structured as follows:

```
================================================================================
                                  YAMUNA SHARMA
================================================================================
Email: yamuna@example.com | Phone: +1-555-0199
Target Role: Data Analyst

--------------------------------------------------------------------------------
PROFESSIONAL SUMMARY
--------------------------------------------------------------------------------
Results-driven professional seeking to transition into a Data Analyst role. 
Possesses core strengths in Python, Excel, Tableau. Highly motivated and aligned with 
current target market requirements, demonstrating matching technical capabilities in 
essential industry skills.

--------------------------------------------------------------------------------
TECHNICAL & PROFESSIONAL SKILLS
--------------------------------------------------------------------------------
- Core Proficiencies: Python, Excel, Tableau
- Key Alignments for Data Analyst: Python, Excel, Tableau
- Professional Development Areas: SQL, Power BI, Statistics, Communication
================================================================================
```

---

## 9. Future Improvements
While the current version of CareerReady Agent is fully functional and modular, we have identified several promising directions for future development:

1. **Tailwind-Styled PDF Exports**:
   Instead of generating plain-text files (`resume_output.txt`), we plan to integrate a PDF generation library (such as ReportLab or a Headless Chrome HTML-to-PDF renderer) to compile highly stylized, modern resumes matching custom design templates.
2. **Direct Course Catalog Integrations**:
   By connecting the `Career Roadmap Agent` to live learning platforms like Coursera, Udemy, or edX APIs, we can retrieve up-to-date courses, check pricing, and recommend active modules containing certifications.
3. **AI Mock Interview Simulator**:
   Adding a seventh agent—the `Mock Interview Agent`—which reads the user's `gap_analysis.json` and conducts an interactive text-to-speech mock interview focusing on the candidate's target skills. It will evaluate responses and provide actionable tips for improvement.
4. **Vector Database Integration (RAG)**:
   For power users, integrating a local vector store (e.g., ChromaDB or FAISS) to store historical resume versions, cover letters, and comprehensive job descriptions. This will allow the agents to perform retrieval-augmented generation (RAG) to tailor job descriptions based on a much larger context.

---

## 10. Conclusion & Team Credits
Developing the CareerReady Agent has shown us how multi-agent architectures, structured file interfaces, and AI-assisted development tools can accelerate software creation. By breaking a complex career planning workflow into specialized agents, we built a tool that provides real-time market insights and personalized feedback. Vibe coding with the Antigravity assistant allowed us to implement code patterns and fallbacks rapidly, keeping us focused on system architecture and user flows.

This project was built by a collaborative team of four developers:

* **Jashmitha**: Lead Agent Architect, focused on the configuration of Google Antigravity Agents and prompt engineering.
* **Yamuna**: Lead UI/UX Engineer, responsible for designing the CLI workflows and developing the Streamlit visualization interface.
* **Shankar**: MCP & Protocol Specialist, responsible for designing the FastMCP server structure, tool endpoints, and JSearch API integrations.
* **Aashritha**: QA & Data Engineer, responsible for data schemas, validation routines, local fallback libraries, and weighted score calculations.

We have released CareerReady Agent under the **MIT License**, making it fully open for developers to modify, customize, and deploy.

---
*Thank you for reading our Kaggle competition write-up. We hope CareerReady Agent helps job seekers know their gaps, close them, and get hired!*
