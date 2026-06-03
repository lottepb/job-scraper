# company_expander_criteria.py
# Company expansion criteria and prompt.
# Imported by discover_new_companies.py
# Edit this file to update how new companies are discovered.

# ---------------------------------------------------------------------------
# Company expansion prompt — used by discover_new_companies.py
# ---------------------------------------------------------------------------
EXPANDER_PROMPT = """
You are helping Lotte Petersen-Buckley, a Senior Analytics Engineer in San Francisco,
find companies to target in her job search.

Here is her current list of target companies:
{company_list}

Your task: suggest up to 20 additional companies that are NOT on this list.

## Company criteria

### Location
- Must have a San Francisco office
- South Bay (Menlo Park, Palo Alto, Redwood City) is acceptable but lower priority
- Remote-first is acceptable only if they have an SF office

### Size & stage
- Ideal size: 100-300 employees
- Acceptable: smaller or larger, with slightly lower preference
- Over 1,000 employees is less desirable; avoid 10,000+
- Stage: Series A through Pre-IPO preferred; public companies acceptable if tech-forward
- Exclude seed stage — too early for analytics engineering roles

### Culture & environment
- Must be tech-forward — data and engineering are taken seriously
- Fast-paced, startup or scale-up environment strongly preferred
- Avoid companies where roles require deep domain passion (e.g. must be a gamer)
- Avoid old-school, slow-moving, or non-tech-native companies
- All sectors welcome — domain fit is handled separately

### Hard excludes
- No SF office
- Seed stage
- 5-days-in-office culture
- Fossil fuels, tobacco/vaping, weapons/defence, predatory finance
- Headcount over 10,000

### Must be likely to have analytics engineering roles
- Data-driven, product-led companies
- Companies that have raised Series B+ and are scaling their data function
- Companies using modern data stacks (dbt, Snowflake, BigQuery, Looker etc.)

For each suggested company return:
- company_name: the company name
- reason: one sentence on why it's a good fit
- stage: estimated stage (Series A, B, C, D, Pre-IPO, Public)
- sector: primary sector
- estimated_headcount: approximate number of employees

Return a JSON array only. No preamble or explanation outside the JSON.
"""