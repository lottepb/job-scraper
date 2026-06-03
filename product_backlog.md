# Product Backlog

Sorted by priority. Move items to "Done" when shipped.

---

## In progress / next up
_(nothing yet)_

---

## Backlog

- [ ] **Remove dodgy line terminator characters** - when the scraper runs, it should clean the text as it's written rather than leaving in unusual line terminator and other characters. 

- [ ] **Only English language roles** - don't find a match for roles listed in a language other than English.

- [ ] **Include hyperlink to role in dashboard**

- [ ] **Diff-based daily runs (high priority)** — instead of re-scraping and re-scoring everything each day, compare new listings against the previous run and only score what's new. Mark disappeared listings as closed. This makes daily runs faster, cheaper, and enables the "new today" feature. Required before setting up GitHub Actions schedule.

- [ ] **Define company expansion criteria (high priority)** — document the requirements for how `discover_new_companies.py` should find similar companies. What makes a company eligible? How many to add per run? How to avoid duplicates or bad suggestions? Required before running the expander in production.

- [ ] **GitHub Actions daily schedule (high priority)** — write `run_daily.yml` to run scraper → scorer → expander automatically each day. Blocked by diff-based runs being in place first.

- [ ] **Company scoring** — automatically evaluate each company against Lotte's preferences (SF office, hybrid policy, size, stage, tech-forward culture) and generate a company-level score and summary. Displayed in the Companies tab of the dashboard. Would feed into the interest indicator and give context before even looking at job listings. Could use Claude + web search to research each company. Adjust product to not search for companies I'm not interested in at all, and to reduce frequency of search for low-interest companies.

- [ ] **Company interest level** — add an `interest` field to `companies.csv` with values: `high`, `medium`, `low`, or empty. Settable from the dashboard company tab. Could give a small score boost to high-interest companies in the job matches view.

- [ ] **Exclude companies** — add an exclude button in the dashboard company tab. Writes `excluded=true` to `companies.csv` so it's skipped in future scrapes.

- [ ] **"New today" badge** — highlight roles that appeared in today's scrape run. Enabled by diff-based runs.

- [ ] **Applied tracker** — mark a role as applied, add application date, track status (applied / interviewing / offer / rejected).

- [ ] **Date first seen** — track when a role first appeared vs just when it was last seen, so roles that persist across runs show their original discovery date.

- [ ] **Company enrichment** — add metadata per company: funding stage, sector, headcount, SF office yes/no, remote policy. Could use Claude + web search to populate this automatically.

- [ ] **Manual company add** — add a company directly from the dashboard without editing the CSV.

- [ ] **Salary scraping** — salary is rarely listed on job pages. Explore scraping from Levels.fyi or asking Claude to estimate based on company stage and title.

- [ ] **Job status tracking** — detect when a role disappears from a career page and mark it as closed in the dashboard.

- [ ] **Password protection** — add simple Streamlit authentication so the app isn't fully public.

- [ ] **Daily email digest** — optional email summarising top new roles each day, for days when you don't open the dashboard.

- [ ] **Template version** — generalise the project into a reusable template anyone can adapt, with personal config (company list, role criteria, scoring prompt) separated from core logic.

---

## Done
_(nothing yet)_