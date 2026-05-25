\# Autonomous Research Agent



An AI agent that researches any topic and produces a cited markdown report using iterative refinement.



\## How it works

1\. \*\*Planner\*\* breaks the topic into sub-questions and search queries

2\. \*\*Gather loop\*\* searches the web via Tavily and scrapes source pages

3\. \*\*Synthesizer\*\* compiles evidence into a structured report with citations

4\. \*\*Gap checker\*\* identifies missing coverage and triggers follow-up research

5\. Repeats up to 3 iterations until the report is comprehensive



\## Tech stack

\- \*\*LLM:\*\* Groq (LLaMA 3.3 70B)

\- \*\*Web search:\*\* Tavily API

\- \*\*Scraping:\*\* BeautifulSoup4

\- \*\*Vector memory:\*\* ChromaDB

\- \*\*Language:\*\* Python 3.12



\## Setup

```bash

git clone https://github.com/yourusername/research-agent

cd research-agent

python -m venv venv

venv\\Scripts\\Activate.ps1

pip install -r requirements.txt

```



\## Usage

```bash

python main.py "Your research topic here"

```



\## Sample output

Reports are saved as markdown files with inline citations. Example topics:

\- "The current state of AI in 2026"

\- "The impact of quantum computing on cybersecurity"



