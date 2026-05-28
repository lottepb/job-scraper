# criteria.py
# This file defines Lotte's job search criteria.
# It is imported by score_job_listings.py and discover_new_companies.py
# Edit this file to update your preferences — no other files need to change.

# ---------------------------------------------------------------------------
# Titles to scrape — broad net, Claude reads the JD to confirm it's AE work
# ---------------------------------------------------------------------------
TARGET_TITLE_KEYWORDS = [
    "analytics engineer",
    "analytics engineering",
    "business intelligence engineer",
    "BI engineer",
    "data engineer, analytics",
    "analytics infrastructure",
    "data analyst",         # included — some AE roles use this title
    "data engineer",        # included at low priority
]

# ---------------------------------------------------------------------------
# Scoring criteria — passed to Claude as part of the matching prompt
# ---------------------------------------------------------------------------
SCORING_CRITERIA = """
You are evaluating a job listing for Lotte Petersen-Buckley, a Senior Analytics Engineer
based in San Francisco with 8 years of data experience. She is looking for her next role.

## Her background
- Expert in SQL, dbt, BigQuery, Looker, data modelling, semantic layer
- Experience building data foundations from scratch at scale-ups
- Strong stakeholder communication and cross-functional collaboration
- Comfortable with Python (learning), Fivetran, Hightouch, Segment
- Oxford PPE graduate, former management consultant, sharp business instincts
- US Green Card holder, based in San Francisco

## Target roles (in priority order)
1. Senior Analytics Engineer
2. Staff Analytics Engineer
3. Analytics Engineer
4. Business Intelligence Engineer
5. Data Engineer with analytics focus (low priority)

Note: title matters less than the job description. A "Data Analyst" or "BI Engineer"
role that describes analytics engineering work (dbt, data modelling, self-serve analytics)
should be scored as an AE role. Use the JD, not the title, to determine fit.

## Location preferences (in priority order)
1. San Francisco, hybrid 2-3 days in office — ideal
2. San Francisco, hybrid 4 days — acceptable, slight ding
3. South Bay (e.g. Palo Alto, Menlo Park), hybrid 1-2 days — open for exceptional roles
4. Remote with SF office — only for genuinely outstanding roles
5. Fully remote, no SF office — low priority
6. Outside US — exclude

## Salary
- Target: $180k-$220k+ base
- Floor: $175k (below this is a meaningful negative signal)
- Current salary: $190k base — going lower needs to be justified by role quality
- If salary is not listed, do not penalise — many startups don't list it

## Technical skills
- Must have (score down if absent): SQL, data modelling
- Strong positive signal: dbt, BigQuery, Snowflake, Looker, semantic layer
- Positive signal: Python, Airflow, Dagster, Fivetran, Airbyte, Hex, Omni
- Emerging skills worth rewarding: AI/LLM integration, text-to-SQL, RAG awareness
- Do not exclude roles that require Spark, Databricks, or heavy Python — Lotte
  is open to roles that will develop her technical skills over the next 2 years

## Company preferences
- Stage: Seed through pre-IPO (Series A-E preferred)
- Sector: any — ethics filter applies (see exclusions)
- Positive signal: first data hire, building from scratch, high growth, scale-up
- Positive signal: role mentions potential to build or lead a team in future
- GTM/Growth domain is a strong fit but not required — all domains welcome

## Hard exclusions — always score 0
- Company operates in: oil/fossil fuels, tobacco/vaping, weapons/defence,
  predatory lending or finance (e.g. payday loans)
- Salary confirmed below $175k
- Role is pure people management with no IC work
- Role is outside the US

## Scoring guide
Score the role from 1-10 based on overall fit. Be honest — a 10 is rare.

10 — Near-perfect: Senior/Staff AE, SQL+dbt required, SF hybrid 2-3 days,
     growth-stage startup, salary in range, strong background match
9  — Excellent: most criteria met, one minor imperfection
8  — Strong: good title and skills match, location or salary slightly off
7  — Good: solid AE role, a couple of criteria not perfectly met
6  — Decent: worth reviewing manually, meaningful gaps in 1-2 areas
5  — Marginal: AE-adjacent role, or significant location/salary mismatch
4  — Long shot: Data Engineer role, heavy Python/Spark, or South Bay commute
3  — Weak: poor skills match or remote-only with no SF office
2  — Very weak: title mismatch, wrong location, low salary signal
1  — Near miss: almost nothing matches but not a hard exclusion
0  — Exclude: hard exclusion criteria met (harmful company, outside US, etc.)

## Output format
Return a JSON object with exactly these fields:
{
  "score": <integer 0-10>,
  "title_confirmed": <true if JD describes AE work regardless of title, else false>,
  "summary": <one sentence: what the role is and why it scored this way>,
  "green_flags": [<list of specific positive signals from the JD>],
  "yellow_flags": [<list of concerns or uncertainties>],
  "apply": <true if score >= 6, else false>
}
"""

# ---------------------------------------------------------------------------
# Company expander prompt — used by discover_new_companies.py
# ---------------------------------------------------------------------------
EXPANDER_PROMPT = """
You are helping Lotte Petersen-Buckley, a Senior Analytics Engineer in San Francisco,
find companies to target in her job search.

Here is her current list of target companies:
{company_list}

Your task: suggest up to 20 additional companies that are NOT on this list but share
similar characteristics. Focus on:
- US-based tech companies or startups (Seed through pre-IPO preferred)
- Companies likely to have an analytics engineering function
- Companies in similar sectors to those already on the list
- Avoid companies in harmful industries (fossil fuels, tobacco, weapons, predatory finance)
- Avoid very large enterprises where AE roles are rare or bureaucratic

For each suggested company return:
- company_name: the company name
- reason: one sentence on why it's a good fit for this list
- stage: estimated stage (Seed, Series A, B, C, D, E, Pre-IPO, Public)
- sector: primary sector

Return a JSON array only. No preamble or explanation outside the JSON.
"""
