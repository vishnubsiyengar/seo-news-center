import asyncio
import os
import time
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

# --- THE SOURCE REGISTRY ---
# You can add or remove URLs here as your strategy evolves.
SEO_SOURCES = [
    "https://developers.google.com/search/blog",
    "https://www.searchenginejournal.com/category/seo/",
    "https://searchengineland.com/library/platforms/google/google-search-console/",
    "https://backlinko.com/blog",
    "https://ahrefs.com/blog/"
]

async def process_article(article_url):
    """Processes a single URL through the Ingest -> Synthesize -> Save pipeline."""
    source_domain = article_url.split("//")[-1].split("/")[0]
    print(f"\n[ORCHESTRATOR] Checking: {source_domain}...")

    # 1. DUPLICATION GUARD
    existing = supabase.table("articles").select("id").eq("source_url", article_url).execute()
    if existing.data:
        print(f"   - SKIPPING: Already indexed.")
        return

    # 2. INGESTION
    scrape_result = await run_scraper(article_url)
    if scrape_result["status"] == "error":
        print(f"   - FAILED: Scrape error.")
        return

    # 3. SYNTHESIS (The Brain)
    # Note: We pass the raw data to the Manager Agent
    analysis = run_manager_agent(scrape_result["data"], source_domain)
    
    if "REJECTED" in analysis["judge_verdict"]:
        print(f"   - REJECTED: Failed quality gate.")
        return

# 3.5 CLUSTERING LOGIC (The Triage Check)
    # Fetch titles/IDs of articles from the last 48 hours
    recent_data = supabase.table("articles").select("id, event_title").limit(10).execute()
    existing_events = recent_data.data if recent_data.data else []

    cluster_verdict = run_clustering_agent(analysis["summary"], existing_events)
    
    # If it's a new event, we use its own ID as the Cluster ID
    # If it's related, we inherit the existing Cluster ID
    event_title = analysis.get("category") if cluster_verdict == "NEW" else None

    # 4. PERSISTENCE
    data_to_save = {
        "title": f"Update from {source_domain}", 
        "source_url": article_url,
        "source_name": source_domain,
        "category": analysis.get("category", "General SEO"), # New mapping
        "raw_content": scrape_result["data"][:5000],
        "summary_technical": analysis["summary"],
        "confidence_score": analysis["confidence_score"],
        "food_for_thought": analysis["questions"],
        "impact_score": analysis.get("impact_score", 5.0)
        "cluster_id": cluster_verdict if cluster_verdict != "NEW" else None,
        "event_title": event_title
    }

    try:
        supabase.table("articles").insert(data_to_save).execute()
        print(f"   ✅ SUCCESS: Captured with Confidence {analysis['confidence_score']}")
    except Exception as e:
        print(f"   - DB ERROR: {e}")

async def run_news_cycle():
    """Iterates through the manifest of SEO sources."""
    print("🚀 STARTING SEO INTELLIGENCE CYCLE")
    for source in SEO_SOURCES:
        await process_article(source)
        # Clinical Grace Period: We wait 2 seconds between sources to be a 'Good Crawler'
        time.sleep(2)
    print("\n🏁 CYCLE COMPLETE: All sources processed.")

if __name__ == "__main__":
    asyncio.run(run_news_cycle())