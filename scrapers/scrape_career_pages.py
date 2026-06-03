# scrape_career_pages.py
# Reads companies from data/companies.csv, finds their career pages,
# detects if they use Greenhouse / Lever / Ashby, and scrapes job listings
# using those platforms' public APIs where possible.
# Falls back to HTML scraping for companies not on a known job board.
# Writes raw results to data/raw_job_listings.csv

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

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 10
SLEEP_BETWEEN_REQUESTS = 1

# Keywords to filter job titles — broad net, Claude confirms AE fit later
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
# Helper: is a title relevant?
# ---------------------------------------------------------------------------
def is_relevant_title(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in TITLE_KEYWORDS)


# ---------------------------------------------------------------------------
# Helper: make a GET request safely
# ---------------------------------------------------------------------------
def safe_get(url: str, as_json: bool = False):
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json() if as_json else r
    except Exception as e:
        print(f"    Request failed for {url}: {e}")
        return None


# ---------------------------------------------------------------------------
# Detect job board from a career page
# Returns (platform, slug) or (None, None)
# ---------------------------------------------------------------------------
def detect_job_board(career_url: str) -> tuple[str | None, str | None]:
    r = safe_get(career_url)
    if not r:
        return None, None

    html = r.text

    # Greenhouse
    gh = re.search(r'boards\.greenhouse\.io/([a-zA-Z0-9_\-]+)', html)
    if gh:
        return "greenhouse", gh.group(1)

    # Lever
    lv = re.search(r'jobs\.lever\.co/([a-zA-Z0-9_\-]+)', html)
    if lv:
        return "lever", lv.group(1)

    # Ashby
    ab = re.search(r'jobs\.ashbyhq\.com/([a-zA-Z0-9_\-]+)', html)
    if ab:
        return "ashby", ab.group(1)

    return None, None


# ---------------------------------------------------------------------------
# Greenhouse scraper
# ---------------------------------------------------------------------------
def scrape_greenhouse(company_name: str, slug: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    data = safe_get(url, as_json=True)
    if not data:
        return []

    jobs = []
    for job in data.get("jobs", []):
        title = job.get("title", "")
        if not is_relevant_title(title):
            continue

        location = job.get("location", {}).get("name", "")
        raw_desc = job.get("content", "") or ""
        description = BeautifulSoup(raw_desc, "lxml").get_text(separator="\n", strip=True)[:6000]

        jobs.append({
            "date_scraped": str(date.today()),
            "company_name": company_name,
            "title": title,
            "location": location,
            "salary": "",
            "url": job.get("absolute_url", ""),
            "career_page": f"https://boards.greenhouse.io/{slug}",
            "description": description,
            "source_platform": "greenhouse",
        })

    return jobs


# ---------------------------------------------------------------------------
# Lever scraper
# ---------------------------------------------------------------------------
def scrape_lever(company_name: str, slug: str) -> list[dict]:
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    data = safe_get(url, as_json=True)
    if not data:
        return []

    jobs = []
    for job in data:
        title = job.get("text", "")
        if not is_relevant_title(title):
            continue

        location = job.get("categories", {}).get("location", "")

        desc_parts = []
        for section in job.get("lists", []):
            desc_parts.append(section.get("text", ""))
            for item in section.get("content", "").split("<li>"):
                clean = BeautifulSoup(item, "lxml").get_text(strip=True)
                if clean:
                    desc_parts.append(f"- {clean}")

        description = "\n".join(desc_parts)[:6000]

        jobs.append({
            "date_scraped": str(date.today()),
            "company_name": company_name,
            "title": title,
            "location": location,
            "salary": "",
            "url": job.get("hostedUrl", ""),
            "career_page": f"https://jobs.lever.co/{slug}",
            "description": description,
            "source_platform": "lever",
        })

    return jobs


# ---------------------------------------------------------------------------
# Ashby scraper
# ---------------------------------------------------------------------------
def scrape_ashby(company_name: str, slug: str) -> list[dict]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true"
    data = safe_get(url, as_json=True)
    if not data:
        return []

    jobs = []
    for job in data.get("jobs", []):
        title = job.get("title", "")
        if not is_relevant_title(title):
            continue

        location = job.get("location", "")

        comp = job.get("compensation", {})
        salary = ""
        if comp:
            min_val = comp.get("minValue")
            max_val = comp.get("maxValue")
            currency = comp.get("currency", "USD")
            if min_val and max_val:
                salary = f"{currency} {min_val:,}–{max_val:,}"

        description = BeautifulSoup(
            job.get("descriptionHtml", "") or "", "lxml"
        ).get_text(separator="\n", strip=True)[:6000]

        jobs.append({
            "date_scraped": str(date.today()),
            "company_name": company_name,
            "title": title,
            "location": location,
            "salary": salary,
            "url": job.get("jobUrl", ""),
            "career_page": f"https://jobs.ashbyhq.com/{slug}",
            "description": description,
            "source_platform": "ashby",
        })

    return jobs


# ---------------------------------------------------------------------------
# Fallback: HTML scraper
# ---------------------------------------------------------------------------
def scrape_html_fallback(company_name: str, career_url: str) -> list[dict]:
    r = safe_get(career_url)
    if not r:
        return []

    soup = BeautifulSoup(r.text, "lxml")
    jobs = []

    for tag in soup.find_all("a", href=True):
        title = tag.get_text(strip=True)
        href = tag["href"]

        if not title or len(title) < 5:
            continue
        if not is_relevant_title(title):
            continue

        if href.startswith("http"):
            job_url = href
        elif href.startswith("/"):
            base = re.match(r"https?://[^/]+", career_url)
            job_url = base.group(0) + href if base else career_url
        else:
            job_url = career_url + "/" + href

        parent = tag.find_parent()
        location = ""
        if parent:
            text = parent.get_text(separator=" ", strip=True)
            loc_match = re.search(
                r"(San Francisco|Remote|New York|NYC|Austin|Seattle|Chicago|Hybrid|London)",
                text, re.IGNORECASE
            )
            if loc_match:
                location = loc_match.group(0)

        description = ""
        try:
            jr = requests.get(job_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            jr.raise_for_status()
            jsoup = BeautifulSoup(jr.text, "lxml")
            for t in jsoup(["nav", "header", "footer", "script", "style"]):
                t.decompose()
            description = jsoup.get_text(separator="\n", strip=True)[:6000]
            time.sleep(SLEEP_BETWEEN_REQUESTS)
        except Exception:
            pass

        jobs.append({
            "date_scraped": str(date.today()),
            "company_name": company_name,
            "title": title,
            "location": location,
            "salary": "",
            "url": job_url,
            "career_page": career_url,
            "description": description,
            "source_platform": "html_fallback",
        })

    seen = set()
    unique = []
    for job in jobs:
        key = (job["title"], job["url"])
        if key not in seen:
            seen.add(key)
            unique.append(job)

    return unique


# ---------------------------------------------------------------------------
# Find career page URL for a company
# ---------------------------------------------------------------------------
def find_career_url(company_name: str) -> str | None:
    slug = company_name.lower().replace(" ", "").replace(".", "").replace(",", "").replace("/", "")
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
# Write results to CSV
# ---------------------------------------------------------------------------
def write_results(jobs: list[dict]):
    if not jobs:
        return
    fieldnames = list(jobs[0].keys())
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
    print(f"Loaded {len(companies)} companies to scrape.\n")

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print(f"Cleared previous results from {OUTPUT_FILE}\n")

    total_jobs = 0
    platform_counts = {"greenhouse": 0, "lever": 0, "ashby": 0, "html_fallback": 0, "not_found": 0}

    for i, company in enumerate(companies):
        name = company["company_name"]
        print(f"[{i+1}/{len(companies)}] {name}")

        career_url = find_career_url(name)
        if not career_url:
            print(f"    Could not find career page — skipping")
            platform_counts["not_found"] += 1
            time.sleep(SLEEP_BETWEEN_REQUESTS)
            continue

        print(f"    Career page: {career_url}")

        platform, slug = detect_job_board(career_url)
        print(f"    Platform: {platform or 'none — using HTML fallback'}")

        if platform == "greenhouse":
            jobs = scrape_greenhouse(name, slug)
        elif platform == "lever":
            jobs = scrape_lever(name, slug)
        elif platform == "ashby":
            jobs = scrape_ashby(name, slug)
        else:
            jobs = scrape_html_fallback(name, career_url)

        platform_counts[platform or "html_fallback"] += len(jobs)

        if jobs:
            write_results(jobs)
            total_jobs += len(jobs)
            print(f"    Found {len(jobs)} relevant listings")
        else:
            print(f"    No matching listings found")

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    print(f"\n{'='*50}")
    print(f"Done. {total_jobs} total listings saved to {OUTPUT_FILE}")
    print(f"Greenhouse: {platform_counts['greenhouse']} | Lever: {platform_counts['lever']} | Ashby: {platform_counts['ashby']} | HTML fallback: {platform_counts['html_fallback']} | Not found: {platform_counts['not_found']}")


if __name__ == "__main__":
    main()
