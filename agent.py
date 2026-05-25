import os, json
from groq import Groq
from tools import search_web, scrape_page, store_chunk, retrieve_chunks
from prompts import PLANNER_PROMPT, SYNTHESIZER_PROMPT, GAP_CHECKER_PROMPT
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MAX_ITERATIONS = 3

def plan(topic: str) -> dict:
    prompt = PLANNER_PROMPT + f"\n\nResearch topic: {topic}"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

def gather(queries: list[str], iteration: int = 0) -> list[dict]:
    evidence = []
    for i, query in enumerate(queries):
        print(f"  Searching: {query}")
        results = search_web(query)
        for j, r in enumerate(results[:3]):
            print(f"     Scraping: {r['url'][:60]}...")
            content = scrape_page(r["url"])
            chunk_id = f"iter{iteration}_q{i}_r{j}"
            store_chunk(chunk_id, content, {"url": r["url"], "query": query})
            evidence.append({"url": r["url"], "query": query, "content": content[:800]})
    return evidence

def synthesize(topic: str, all_evidence: list[dict], plan: dict) -> str:
    capped_evidence = all_evidence[:-20:] 
    evidence_text = "\n\n---\n\n".join(
        f"[Source: {e['url']}]\n{e['content']}" for e in capped_evidence
    )
    prompt = f"""{SYNTHESIZER_PROMPT}

Topic: {topic}

Report sections needed: {', '.join(plan['report_sections'])}

Evidence gathered:
{evidence_text}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def check_gaps(topic: str, report: str) -> dict:
    prompt = GAP_CHECKER_PROMPT + f"\n\nOriginal topic: {topic}\n\nCurrent report:\n{report}"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

def run(topic: str) -> str:
    print(f"\nPlanning research on: {topic}")
    research_plan = plan(topic)
    print(f"   Sub-questions: {len(research_plan['sub_questions'])}")
    print(f"   Sections planned: {research_plan['report_sections']}")

    # First gather pass
    print(f"\n[Iteration 1] Gathering evidence...")
    all_evidence = gather(research_plan["search_queries"], iteration=0)
    print(f"   Collected {len(all_evidence)} sources")

    print(f"\n[Iteration 1] Synthesizing report...")
    report = synthesize(topic, all_evidence, research_plan)

    # Refinement loop
    for iteration in range(2, MAX_ITERATIONS + 1):
        print(f"\nChecking for gaps...")
        gap_result = check_gaps(topic, report)

        if not gap_result.get("has_gaps") or not gap_result.get("follow_up_queries"):
            print(f"   No gaps found — report is complete!")
            break

        print(f"   Gaps found: {gap_result['gaps']}")
        print(f"\n[Iteration {iteration}] Gathering more evidence...")
        new_evidence = gather(gap_result["follow_up_queries"], iteration=iteration)
        all_evidence.extend(new_evidence)
        print(f"   Total sources now: {len(all_evidence)}")

        print(f"\n[Iteration {iteration}] Re-synthesizing report...")
        report = synthesize(topic, all_evidence, research_plan)

    return report