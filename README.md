# job-scraper

Automated job scraper that monitors company career pages, discovers similar companies dynamically, scores listings against my criteria, and delivers a daily digest of the best matches via a Streamlit dashboard.

## How it works

1. **Scrape** — `scrapers/scrape_career_pages.py` visits career pages for all companies in `data/companies.csv` and pulls job listings into `data/raw_job_listings.csv`
2. **Score** — `matching/score_job_listings.py` sends each listing to Claude, which scores it 1–10 against my criteria and writes results to `data/job_matches.csv`
3. **Expand** — `expander/discover_new_companies.py` asks Claude to suggest similar companies and appends them to `data/companies.csv`
4. **Review** — `ui/dashboard.py` is a Streamlit app for browsing matches, viewing the company list, and managing the search

Steps 1–3 run automatically every day via GitHub Actions (`.github/workflows/run_daily.yml`).

## Project structure

```
job-scraper/
├── data/
│   ├── companies.csv            # master company list (seed + AI-discovered)
│   └── job_matches.csv          # scored job matches, read by the UI
├── scrapers/
│   └── scrape_career_pages.py   # visits career pages, pulls job listings
├── matching/
│   ├── criteria.py              # all job search criteria and scoring prompts
│   └── score_job_listings.py    # sends jobs to Claude, returns scores
├── expander/
│   └── discover_new_companies.py # asks Claude to find similar companies
├── ui/
│   └── dashboard.py             # Streamlit dashboard
├── .github/
│   └── workflows/
│       └── run_daily.yml        # GitHub Actions schedule
├── .env                         # API key — never committed to GitHub
├── requirements.txt             # Python dependencies
└── README.md
```

## Setup

See setup instructions (coming soon).

## Criteria

Job matching criteria are defined in `matching/criteria.py`. Edit that file to update preferences — no other files need to change.
