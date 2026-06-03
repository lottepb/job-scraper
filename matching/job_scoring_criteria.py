# job_scoring_criteria.py
# This file defines Lotte's job search criteria.
# Imported by score_job_listings.py
# Edit this file to update preferences — no other files need to change.

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
- Expert in SQL, dbt (Cloud + Core), BigQuery, Looker, data modelling, semantic layer
- Experience building data foundations from scratch at scale-ups
- Strong stakeholder communication and cross-functional collaboration
- Also has: Fivetran, Hightouch, Segment, Stitch, Git, basic Python
- Oxford PPE graduate, former management consultant, sharp business instincts
- US Green Card holder, based in San Francisco

## Target roles (in priority order)
1. Senior Analytics Engineer
2. Staff Analytics Engineer
3. Analytics Engineer
4. Business Intelligence Engineer
5. Data Engineer — ONLY if the JD describes analytics engineering work (see below)

## Critical: how to evaluate "Data Engineer" roles
A Data Engineer role should only score above 5 if the JD primarily describes:
- Data modelling, semantic layers, self-serve analytics
- dbt, Looker, BI tooling, metrics definition
- Cross-functional analytics work with business stakeholders

A Data Engineer role should be capped at 4 if the JD primarily requires:
- Kafka, Spark, Beam, Flink — real-time streaming and infrastructure tools
- Heavy Java, Scala, or advanced Python (beyond scripting)
- Building and maintaining data infrastructure at a systems level
- Distributed systems, data platform architecture

These are genuine screen-out signals — Lotte does not have these skills and
is very unlikely to pass interviews for roles that require them as core competencies.

## Technical skills Lotte HAS
- SQL ✅ (expert)
- dbt Cloud + dbt Core ✅ (expert)
- BigQuery ✅ (expert)
- Looker ✅ (strong)
- Data modelling + semantic layer ✅ (strong)
- Fivetran, Stitch, Hightouch, Segment ✅
- Git / version control ✅
- Python ✅ (basic — scripting level, not engineering level)

## Technical skills Lotte is LEARNING (open to, not a blocker)
- Airflow, Dagster — pipeline orchestration, increasingly common in AE roles
- Databricks — Spark-based platform, learnable given BigQuery background
- Snowflake — very similar to BigQuery, minimal ramp-up needed
- Advanced Python — actively developing this skill

## Technical skills that are SCREEN-OUT risks (cap score at 4 if required)
- Kafka — real-time event streaming infrastructure
- Apache Spark — large-scale distributed data processing
- Apache Beam — batch/streaming pipeline framework
- Flink — real-time stream processing
- Terraform — infrastructure as code (very rare in AE roles)
- Java / Scala — not in her background at all

## Emerging skills worth rewarding (score up if present)
- AI/LLM integration in data workflows
- Text-to-SQL, NLP querying, RAG awareness
- dbt Semantic Layer, Cube, AtScale
- Hex, Omni — modern AI-native BI tools

## Location preferences (in priority order)
1. San Francisco, hybrid 2-3 days in office — ideal
2. San Francisco, hybrid 4 days — acceptable, slight ding
3. South Bay (e.g. Palo Alto, Menlo Park), hybrid 1-2 days — open for exceptional roles only
4. Remote with SF office — only for genuinely outstanding roles
5. Fully remote, no SF office — low priority
6. Outside US — exclude

## Salary
- Target: $180k-$220k+ base
- Floor: $175k (below this is a meaningful negative signal)
- Current salary: $190k base — going lower needs to be justified by role quality
- If salary is not listed, do not penalise — many startups don't list it

## Company preferences
- Stage: Series A through pre-IPO preferred; public companies ok if tech-forward
- Sector: any — ethics filter applies (see exclusions)
- Positive signal: first data hire, building from scratch, high growth, scale-up
- Positive signal: role mentions potential to build or lead a team in future
- All domains welcome — GTM/Growth is a strong fit but not required

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
5  — Marginal: AE-adjacent role, significant location/salary mismatch,
     or Data Engineer role where AE work is present but secondary
4  — Long shot: Data Engineer role requiring Kafka/Spark/Beam/Flink,
     or South Bay commute, or heavy infrastructure focus
3  — Weak: poor skills match, remote-only with no SF office
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