# Product Backlog

Ideas and improvements for the job scraper app. Move items to "Done" when shipped.

---

## In progress / next up
_(nothing yet)_

---

## Backlog

### Data & scraping
- [ ] **Date first seen** — `date_scraped` is already captured per run. Future improvement: track when a role *first* appeared vs just when it was last seen, so roles that persist across multiple runs show their original discovery date rather than the most recent scrape date
- [ ] **Salary scraping** — currently empty for most roles since salary is rarely on listing pages. Explore scraping from Levels.fyi, Glassdoor, or asking Claude to estimate based on company stage + title
- [ ] **Job status tracking** — detect when a role disappears from a career page (i.e. was filled or taken down) and mark it as closed in the dashboard

### Company management
- [ ] **Exclude companies** — add an exclude button in the dashboard (company list tab). Writes `excluded=true` to `companies.csv` so it's skipped in future scrapes
- [ ] **Company enrichment** — add metadata per company: funding stage, sector, headcount, SF office yes/no, remote policy. Could use Claude + web search to populate this
- [ ] **Manual company add** — add a company directly from the dashboard without editing the CSV

### Dashboard & UI
- [ ] **"New today" badge** — highlight roles that appeared in today's scrape run
- [ ] **Applied tracker** — mark a role as applied, add application date, track status (applied / interviewing / offer / rejected)
- [ ] **Password protection** — add simple Streamlit authentication so the app isn't fully public

### Delivery
- [ ] **Daily email digest** — optional email summarising top new roles each day, for days when you don't open the dashboard

---

## Done
_(nothing yet)_
