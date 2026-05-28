# discover_new_companies.py
# Reads the current company list, asks Claude to suggest similar companies,
# and appends new discoveries to data/companies.csv

import anthropic
import csv
import json
import os
from criteria import EXPANDER_PROMPT

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COMPANIES_FILE = "data/companies.csv"
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2000

# ---------------------------------------------------------------------------
# Load existing companies
# ---------------------------------------------------------------------------
def load_companies() -> list[str]:
    if not os.path.exists(COMPANIES_FILE):
        return []
    with open(COMPANIES_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row["company_name"] for row in reader]


# ---------------------------------------------------------------------------
# Ask Claude for new company suggestions
# ---------------------------------------------------------------------------
def discover_companies(client, existing: list[str]) -> list[dict]:
    company_list = "\n".join(f"- {c}" for c in existing)
    prompt = EXPANDER_PROMPT.format(company_list=company_list)

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

    return json.loads(raw)


# ---------------------------------------------------------------------------
# Append new companies to companies.csv
# ---------------------------------------------------------------------------
def append_companies(new_companies: list[dict], existing_names: list[str]):
    existing_lower = {name.lower() for name in existing_names}
    added = 0

    with open(COMPANIES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["company_name", "source", "status", "excluded"])
        for company in new_companies:
            name = company.get("company_name", "").strip()
            if name.lower() not in existing_lower:
                writer.writerow({
                    "company_name": name,
                    "source": "ai_discovered",
                    "status": "active",
                    "excluded": "false"
                })
                print(f"  + Added: {name} ({company.get('reason', '')})")
                added += 1
            else:
                print(f"  ~ Skipped (already exists): {name}")

    return added


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    existing = load_companies()
    print(f"Current company list: {len(existing)} companies")
    print("Asking Claude to suggest new companies...")

    suggestions = discover_companies(client, existing)
    print(f"Claude suggested {len(suggestions)} companies. Adding new ones...")

    added = append_companies(suggestions, existing)
    print(f"\nDone. {added} new companies added to {COMPANIES_FILE}.")


if __name__ == "__main__":
    main()
