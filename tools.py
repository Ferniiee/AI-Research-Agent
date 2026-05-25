import os, requests, chromadb
from dotenv import load_dotenv
from tavily import TavilyClient
from bs4 import BeautifulSoup

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
chroma = chromadb.Client()
collection = chroma.get_or_create_collection("research")

# --- Web search ---
def search_web(query: str, max_results: int = 5) -> list[dict]:
    results = tavily.search(query=query, max_results=max_results)
    return [{"url": r["url"], "title": r["title"], "snippet": r["content"]} 
            for r in results["results"]]

# --- Page scraper ---
def scrape_page(url: str) -> str:
    try:
        html = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return text[:8000]
    except Exception as e:
        return f"[scrape failed: {e}]"

# --- Vector memory ---
def store_chunk(doc_id: str, text: str, metadata: dict):
    collection.upsert(documents=[text], ids=[doc_id], metadatas=[metadata])

def retrieve_chunks(query: str, n: int = 5) -> list[str]:
    results = collection.query(query_texts=[query], n_results=n)
    return results["documents"][0] if results["documents"] else []