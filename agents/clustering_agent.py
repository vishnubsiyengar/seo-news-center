import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_clustering_agent(new_summary, existing_events):
    """
    Compares a new article summary against a list of recent event titles.
    Returns the cluster_id if a match is found, or 'NEW' if it's unique.
    """
    if not existing_events:
        return "NEW"

    prompt = f"""
    You are a Data Architect. Review this new SEO update and compare it to the list of recent 'Event Titles'.
    
    NEW UPDATE SUMMARY: 
    {new_summary[:500]}

    RECENT EVENTS:
    {json.dumps(existing_events)}

    TASK:
    - Does this new update belong to one of the RECENT EVENTS?
    - If YES, return the 'id' of that event.
    - If NO (it's a different topic), return 'NEW'.
    
    FORMAT: Return ONLY the raw ID or the word 'NEW'. No prose.
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant", # Fast, binary-style task
    )
    
    return response.choices[0].message.content.strip()