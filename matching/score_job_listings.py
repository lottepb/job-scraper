# score_job_listings.py
# Reads raw job listings, sends each one to Claude for scoring,
# and writes scored results to data/job_matches.csv

import anthropic
import csv
import json
import os
from datetime import date
from criteria import SCORING_CRITERIA

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
INPUT_FILE = "data/raw_job_listings.csv"
OUTPUT_FILE = "data/job_matches.csv"
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1000

# ---------------------------------------------------------------------------
# Score a single job listing
# ---------------------------------------------------------------------------
def score_job(client, job: dict) -> dict:
    """Send a job listing to Claude and return a structured score."""

    prompt = f"""
{SCORING_CRITERIA}

---

Here is the job listing to evaluate:

Company: {job.get('company_name', 'Unknown')}
Title: {job.get('title', 'Unknown')}
Location: {job.get('location', 'Not specified')}
Salary: {job.get('salary', 'Not listed')}
Job description:
{job.get('description', 'No description available')}

Evaluate this role and return your assessment as JSON.
"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)
    return result


# ---------------------------------------------------------------------------
# Main — read listings, score each, write results
# ---------------------------------------------------------------------------
def main():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    if not os.path.exists(INPUT_FILE):
        print(f"No input file found at {INPUT_FILE} — run scrape_career_pages.py first.")
        return

    with open(INPUT_FILE, newline="", encoding="utf-8") as f:
        listings = list(csv.DictReader(f))

    print(f"Scoring {len(listings)} job listings...")

    results = []
    for i, job in enumerate(listings):
        print(f"  [{i+1}/{len(listings)}] {job.get('company_name')} — {job.get('title')}")
        try:
            scored = score_job(client, job)
            results.append({
                "date_scored": str(date.today()),
                "company_name": job.get("company_name"),
                "title": job.get("title"),
                "location": job.get("location"),
                "salary": job.get("salary"),
                "url": job.get("url"),
                "score": scored.get("score"),
                "title_confirmed": scored.get("title_confirmed"),
                "summary": scored.get("summary"),
                "green_flags": " | ".join(scored.get("green_flags", [])),
                "yellow_flags": " | ".join(scored.get("yellow_flags", [])),
                "apply": scored.get("apply"),
            })
        except Exception as e:
            print(f"    Error scoring {job.get('company_name')}: {e}")
            continue

    # Sort by score descending
    results.sort(key=lambda x: int(x.get("score", 0)), reverse=True)

    # Write to output CSV
    if results:
        fieldnames = results[0].keys()
        write_header = not os.path.exists(OUTPUT_FILE)
        with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerows(results)

    print(f"\nDone. {len(results)} jobs scored and saved to {OUTPUT_FILE}.")
    top = [r for r in results if int(r.get("score", 0)) >= 7]
    print(f"{len(top)} roles scored 7 or above.")


if __name__ == "__main__":
    main()
