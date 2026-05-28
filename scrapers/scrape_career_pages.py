# scrape_career_pages.py
# Reads companies from data/companies.csv, finds their career pages,
# scrapes job listings, and writes raw results to data/raw_job_listings.csv

import csv
import os
import re
import requests
import time
from bs4 import BeautifulSoup
from datetime import date

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COMPANIES_FILE = "data/companies.csv"
OUTPUT_FILE = "data/raw_job_listings.csv"

# Keywords that suggest a link leads to a careers page
CAREER_LINK_KEYWORDS = [
    "career", "careers", "jobs", "job", "work-with-us",
    "work_with_us", "join-us", "join_us", "hiring", "opportunities"
]

# Keywords to filter job titles — broad net, Claude will confirm AE fit later
TITLE_KEYWORDS = [
    "analytics engineer",
    "analytics engineering",
    "business intelligence",
    "bi engineer",
    "data engineer",
    "data analyst",
    "data platform",
    "analytics infrastructure",
    "analytics",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 10  # seconds
SLEEP_BETWEEN_REQUESTS = 1  # seconds — be polite to servers

# ---------------------------------------------------------------------------
# Load companies
# ---------------------------------------------------------------------------
def load_companies() -> list[dict]:
    if not os.path.exists(COMPANIES_FILE):
        print(f"Companies file not found: {COMPANIES_FILE}")
        return []
    with open(COMPANIES_FILE, newline="", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row.get("excluded", "false") == "false"]


# ---------------------------------------------------------------------------
# Find the career page URL for a company
# ---------------------------------------------------------------------------
def find_career_url(company_name: str) -> str | None:
    """Try common career page URL patterns before scraping."""
    slug = company_name.lower().replace(" ", "").replace(".", "").replace(",", "")
    candidates = [
        f"https://{slug}.com/careers",
        f"https://{slug}.com/jobs",
        f"https://www.{slug}.com/careers",
        f"https://www.{slug}.com/jobs",
        f"https://{slug}.ai/careers",
        f"https://{slug}.io/careers",
    ]
    for url in candidates:
        try:
            r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            if r.status_code == 200:
                return url
        except Exception:
            continue
    return None


# ---------------------------------------------------------------------------
# Scrape job listings from a career page URL
# ---------------------------------------------------------------------------
def scrape_jobs(company_name: str, career_url: str) -> list[dict]:
    """Scrape job titles and links from a career page."""
    try:
        r = requests.get(career_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
    except Exception as e:
        print(f"    Could not fetch {career_url}: {e}")
        return []

    soup = BeautifulSoup(r.text, "lxml")
    jobs = []

    # Find all links on the page
    for tag in soup.find_all("a", href=True):
        title = tag.get_text(strip=True)
        href = tag["href"]

        if not title or len(title) < 5:
            continue

        # Check if title contains any of our keywords
        title_lower = title.lower()
        if not any(kw in title_lower for kw in TITLE_KEYWORDS):
            continue

        # Build absolute URL
        if href.startswith("http"):
            job_url = href
        elif href.startswith("/"):
            base = re.match(r"https?://[^/]+", career_url)
            job_url = base.group(0) + href if base else career_url
        else:
            job_url = career_url + "/" + href

        # Try to extract location from nearby text
        parent = tag.find_parent()
        location = ""
        if parent:
            siblings = parent.get_text(separator=" ", strip=True)
            # Look for common location patterns
            loc_match = re.search(
                r"(San Francisco|Remote|New York|NYC|Austin|Seattle|Chicago|Los Angeles|Hybrid|London)",
                siblings, re.IGNORECASE
            )
            if loc_match:
                location = loc_match.group(0)

        jobs.append({
            "date_scraped": str(date.today()),
            "company_name": company_name,
            "title": title,
            "location": location,
            "salary": "",  # rarely available on listing pages
            "url": job_url,
            "career_page": career_url,
            "description": "",  # fetched separately if needed
        })

    # Deduplicate by title + url
    seen = set()
    unique_jobs = []
    for job in jobs:
        key = (job["title"], job["url"])
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    return unique_jobs


# ---------------------------------------------------------------------------
# Fetch full job description from individual job page
# ---------------------------------------------------------------------------
def fetch_job_description(job_url: str) -> str:
    """Fetch the full text of a job listing page."""
    try:
        r = requests.get(job_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        # Remove nav, header, footer noise
        for tag in soup(["nav", "header", "footer", "script", "style"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Trim to first 3000 chars — enough for Claude to score
        return text[:3000]
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Write results to CSV
# ---------------------------------------------------------------------------
def write_results(jobs: list[dict]):
    if not jobs:
        return
    fieldnames = jobs[0].keys()
    file_exists = os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(jobs)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    companies = load_companies()
    print(f"Loaded {len(companies)} companies to scrape.")

    # Clear previous results
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print(f"Cleared previous results from {OUTPUT_FILE}")

    total_jobs = 0

    for i, company in enumerate(companies):
        name = company["company_name"]
        print(f"[{i+1}/{len(companies)}] {name}")

        career_url = find_career_url(name)
        if not career_url:
            print(f"    Could not find career page — skipping")
            continue

        print(f"    Found career page: {career_url}")
        jobs = scrape_jobs(name, career_url)

        if not jobs:
            print(f"    No matching job titles found")
            time.sleep(SLEEP_BETWEEN_REQUESTS)
            continue

        # Fetch descriptions for each job
        for job in jobs:
            job["description"] = fetch_job_description(job["url"])
            time.sleep(SLEEP_BETWEEN_REQUESTS)

        write_results(jobs)
        total_jobs += len(jobs)
        print(f"    Found {len(jobs)} relevant listings")

    print(f"\nDone. {total_jobs} total job listings saved to {OUTPUT_FILE}.")


if __name__ == "__main__":
    main()
