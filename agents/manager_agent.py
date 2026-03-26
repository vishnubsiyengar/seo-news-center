import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load Environment Variables (The 'Keys' to the Brain)
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_manager_agent(raw_text, source_domain):
    """
    The Strategic Lead: Transforms raw data into MECE Intelligence & Scores Confidence.
    """
    
    # --- TASK 1: THE SUMMARIZER & SCORER ---
    # This prompt uses the Itamar Gilad framework and your MECE requirements.
    summarizer_prompt = f"""
    You are a Senior SEO Strategy Consultant. Analyze data from: {source_domain}
    
    RAW DATA: 
    {raw_text[:8000]} 

    TASK:
    1. CLASSIFICATION: Choose the MOST relevant category from this list: 
       [Technical SEO, Algorithm Update, Content Strategy, E-commerce, AI & Search]
    2. IMPACT SCORE: Assign a score (0.0 to 10.0) based on this Severity Index:
       - 9.0 - 10.0: CRITICAL (Core Algorithm Updates, Major API Deprecations, Global Indexing changes).
       - 6.0 - 8.0: SIGNIFICANT (Search Console tool updates, schema changes, new ranking factors).
       - 3.0 - 5.0: MODERATE (Best practice refinements, industry case studies, documentation tweaks).
       - 0.1 - 2.0: LOW (Event announcements, guest interviews, general industry news).
    3. SUMMARY: Provide a MECE (Mutually Exclusive, Collectively Exhaustive) Summary in bullet points:
       - Technical Delta: The exact changes to code/documentation.
       - Strategic Implications: The broader search impact (use 'could' or 'may').
       - Execution Constraints: Resource or technical requirements.
    4. TONE: Simple, Direct, and Clinical.
    5. TWEET EXCEPTION: If the input is a short tweet, provide it verbatim first.
    6. QUESTIONS: Generate 3 persona-agnostic 'Food for Thought' questions for builders.
    7. CONFIDENCE SCORE: Assign a score (0.01 to 10.0) based on the Itamar Gilad Framework:
       - 0.01 - 0.1: Near-Zero (Opinions, Pitch Decks, Thematic support)
       - 0.2 - 0.5: Very Low/Low (Estimates, Anecdotal evidence)
       - 1.0 - 3.0: Med-Low (Market data, User evidence)
       - 7.0: Medium (Test results, A/B experiments)
       - 10.0: High (Official Launch Data / Google Docs)

    FORMAT: You MUST return a valid JSON object with these keys: 
    "category","verbatim", "summary", "confidence_score", "questions"
    """

    # Call the High-Capacity Model (Llama 3.3 70B)
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": summarizer_prompt}],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"}
    )
    
    # Parse the output into a Python Dictionary
    analysis = json.loads(response.choices[0].message.content)

    # --- TASK 2: THE JUDGE (HALLUCINATION CHECK) ---
    # This smaller model vets the work of the larger model.
    judge_prompt = f"""
    You are the Quality Control Judge. Review this Summary against the Raw Data.
    RAW DATA: {raw_text[:2000]}
    PROPOSED SUMMARY: {analysis['summary']}

    CRITERIA:
    - Does the summary contain claims NOT found in the raw data? (Hallucination check)
    - Is the tone clinical (e.g., using 'could') rather than prescriptive?

    RESPONSE: Return only 'APPROVED' or 'REJECTED: [Reason]'.
    """

    judge_response = client.chat.completions.create(
        messages=[{"role": "user", "content": judge_prompt}],
        model="llama-3.1-8b-instant",
    )
    
    # Add the Judge's Verdict to our final results
    analysis["judge_verdict"] = judge_response.choices[0].message.content
    
    return analysis