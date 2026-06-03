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
    "data analyst",
    "data engineer",
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
- Former management consultant with sharp business instincts
- US Green Card holder, based in San Francisco

## IMPORTANT: How to evaluate by role type

### Analytics Engineer / BI Engineer titles
These are her primary target roles. Score freely — 7+ if otherwise a good fit.
Do not penalise for missing "Senior" in the title; small companies use flat hierarchies.
Do not mention career growth or path to Staff — irrelevant to her search.

### Data Engineer titles
Evaluate the JD carefully. The score depends entirely on what the role actually requires:

SCORE NORMALLY (can reach 7+) if the JD primarily describes:
- Data modelling, semantic layers, self-serve analytics
- dbt, Looker, BI tooling, metrics definition
- Cross-functional analytics work with business stakeholders

CAP AT 4 if the JD requires any of these as core competencies:
- Kafka — real-time event streaming (she does not have this)
- Apache Spark — large-scale distributed processing (she does not have this)
- Apache Beam — batch/streaming pipelines (she does not have this)
- Flink — real-time stream processing (she does not have this)
- Java or Scala — not in her background

ALWAYS list the primary tools required in the green/yellow flags so she can evaluate.
Never infer or hypothesise about the stack — only score on what is explicitly in the JD.

### Data Analyst titles
Slightly lower ceiling than Data Engineer. Can reach 6 if the JD clearly describes
analytics engineering work. Unlikely to score 7+ unless it is unmistakably AE work.

### Data Scientist titles
Cap at 3. She is not a data scientist and does not want to be one.
She dislikes statistical analysis and A/B experimentation as core job responsibilities.
She will happily support these activities but does not want them to be her primary work.

## Red flags — score down meaningfully
- Role is primarily statistical analysis, A/B testing, or experimentation
- Role requires Kafka, Spark, Beam, Flink, Java, or Scala as core skills
- Role is a pure people management position with no IC work

## Technical skills Lotte HAS
- SQL (expert)
- dbt Cloud + dbt Core (expert)
- BigQuery (expert)
- Looker (strong)
- Data modelling + semantic layer (strong)
- Fivetran, Stitch, Hightouch, Segment
- Git / version control
- Python (basic — scripting level only)

## Technical skills open to learning (not a blocker)
- Airflow, Dagster — pipeline orchestration
- Databricks — learnable given BigQuery background
- Snowflake — very similar to BigQuery, minimal ramp-up
- Advanced Python — actively developing

## Screen-out skills (cap score at 4 if required as core competency)
- Kafka, Apache Spark, Apache Beam, Flink — streaming/infrastructure
- Terraform — infrastructure as code
- Java / Scala

## Emerging skills worth rewarding
- AI/LLM integration in data workflows
- Text-to-SQL, NLP querying, RAG awareness
- dbt Semantic Layer, Cube, AtScale
- Hex, Omni — modern AI-native BI tools

## Location preferences
1. San Francisco, hybrid 2-3 days — ideal
2. San Francisco, hybrid 4 days — acceptable, slight ding
3. "Bay Area" without specifying SF — be skeptical, likely not in the city, ding accordingly
4. South Bay (Palo Alto, Menlo Park etc.), hybrid 1-2 days — open for exceptional roles only
5. Remote with SF office — score more generously for AE roles than DE roles
6. Fully remote, no SF office — low priority but acceptable for strong AE fit
7. Outside US — exclude

## Salary
- Target: $180k-$220k+ base
- If salary is not listed: minor ding only (0.5 points max) — many startups don't list it
- If salary is listed and tops out below $170k: meaningful ding
- If salary is listed and is slightly below target but above $170k: small ding only
- Current salary $190k — going significantly lower needs strong justification
- Do not over-index on salary; a competitive role at a great company often negotiates above listed range

## Company preferences
- Stage: Series A through pre-IPO preferred; public companies ok if tech-forward
- Sector: any — ethics filter applies
- Positive signal: first data hire, building from scratch, high growth, scale-up
- Positive signal: role mentions potential to grow or lead a team in future
- All domains welcome

## Hard exclusions — always score 0
- Company: oil/fossil fuels, tobacco/vaping, weapons/defence, predatory finance
- Salary confirmed below $170k
- Pure people management, no IC work
- Outside the US

## JD truncation
The job description provided may be truncated due to character limits in the scraper.
Do not flag this in yellow flags on every listing — it is a known limitation.
Score based on what is available. If critical information is clearly missing, note it once briefly.

## Do not mention or score on
- Oxford PPE background — irrelevant to scoring
- "Senior" absent from title — irrelevant, small companies use flat hierarchies
- Career growth or path to Staff — irrelevant to her search
- Hypothetical or inferred tech stack — only score on what is explicitly stated in the JD

## Scoring guide
10 — Near-perfect: AE/BI Engineer title, SQL+dbt required, SF hybrid 2-3 days,
     growth-stage startup, salary in range or not listed
9  — Excellent: most criteria met, one minor imperfection
8  — Strong: good title and skills match, location or salary slightly off
7  — Good: solid AE role, a couple of criteria not perfectly met
6  — Decent: worth reviewing manually — could be a strong DE role with AE work,
     or an AE role with meaningful location/salary gap
5  — Marginal: AE-adjacent, significant gaps, or DE role where AE work is secondary
4  — Long shot: DE role requiring Kafka/Spark/Beam/Flink, South Bay commute,
     or Data Analyst role that doesn't clearly describe AE work
3  — Weak: Data Scientist role, poor skills match, remote-only no SF office
2  — Very weak: title mismatch, wrong location, low salary signal
1  — Near miss: almost nothing matches, not a hard exclusion
0  — Exclude: harmful company, outside US, not a real job listing

## Output format
Return a JSON object with exactly these fields:
{
  "score": <integer 0-10>,
  "title_confirmed": <true if JD describes AE work regardless of title, else false>,
  "summary": <one sentence: what the role is and why it scored this way>,
  "green_flags": [<list of specific positive signals from the JD, including key tools required>],
  "yellow_flags": [<list of genuine concerns — do not flag JD truncation, missing Senior title, or lack of career growth path>],
  "apply": <true if score >= 6, else false>
}
"""
