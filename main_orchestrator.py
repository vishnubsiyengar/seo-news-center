import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# --- IMPORTS ---
from skills.web_scraper import run_scraper
from agents.manager_agent import run_manager_agent

load_dotenv()

# Initialize Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def process_new_article(article_url):
    print(f"\n[ORCHESTRATOR] Processing: {article_url}")

    # 1. DUPLICATION GUARD: Check if we already have this article
    existing = supabase.table("articles").select("id").eq("source_url", article_url).execute()
    if existing.data:
        print(">>> SKIPPING: Article already exists in the 12-month database.")
        return

    # 2. INGESTION (The Skill)
    scrape_result = await run_scraper(article_url)
    if scrape_result["status"] == "error":
        print(f"!!! SCRAPE FAILED: {scrape_result['message']}")
        return

    raw_text = scrape_result["data"]
    source_domain = article_url.split("//")[-1].split("/")[0]

    # 3. SYNTHESIS & JUDGE (The Multi-Agent Brain)
    # The 'analysis' variable is now a DICTIONARY, not just text.
    analysis = run_manager_agent(raw_text, source_domain)
    
    print(f"--- JUDGE VERDICT: {analysis['judge_verdict']} ---")
    if "REJECTED" in analysis["judge_verdict"]:
        print("!!! QUALITY GATE FAILED: Summary rejected by Judge.")
        return

    # 4. DATA PERSISTENCE (Saving to Supabase)
    # Mapping the JSON keys to our Database Columns
    data_to_save = {
        "title": f"SEO Update: {source_domain}", 
        "source_url": article_url,
        "source_name": source_domain,
        "raw_content": raw_text[:5000],
        "summary_technical": analysis["summary"], # The MECE bullets
        "confidence_score": analysis["confidence_score"], # The Itamar Gilad score
        "food_for_thought": analysis["questions"], # The persona-agnostic questions
        "verbatim_text": analysis.get("verbatim", ""), # Verbatim tweet if applicable
        "impact_score": 5.0 # We will automate this metric in v1.1
    }

    try:
        supabase.table("articles").insert(data_to_save).execute()
        print(f"✅ SUCCESS: Intelligence captured with Confidence Score: {analysis['confidence_score']}")
    except Exception as e:
        print(f"!!! DATABASE ERROR: {e}")

if __name__ == "__main__":
    test_link = "https://developers.google.com/search/blog"
    asyncio.run(process_new_article(test_link))