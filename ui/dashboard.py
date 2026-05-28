# dashboard.py
# Streamlit app for browsing job matches and the company list
# Run locally with: streamlit run ui/dashboard.py
# Or deploy for free at streamlit.io

import os
import pandas as pd
import streamlit as st
from datetime import date

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
JOB_MATCHES_FILE = "data/job_matches.csv"
COMPANIES_FILE = "data/companies.csv"

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Job Search Dashboard",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Job Search Dashboard")
st.caption(f"Last refreshed: {date.today()}")

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)  # refresh every 5 minutes
def load_matches() -> pd.DataFrame:
    if not os.path.exists(JOB_MATCHES_FILE):
        return pd.DataFrame()
    df = pd.read_csv(JOB_MATCHES_FILE)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["date_scored"] = pd.to_datetime(df["date_scored"], errors="coerce")
    return df

@st.cache_data(ttl=300)
def load_companies() -> pd.DataFrame:
    if not os.path.exists(COMPANIES_FILE):
        return pd.DataFrame()
    return pd.read_csv(COMPANIES_FILE)


matches = load_matches()
companies = load_companies()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2 = st.tabs(["🎯 Job Matches", "🏢 Companies"])


# ---------------------------------------------------------------------------
# Tab 1 — Job Matches
# ---------------------------------------------------------------------------
with tab1:
    if matches.empty:
        st.info("No job matches yet. Run the scraper and scorer first.")
    else:
        # --- Filters ---
        col1, col2, col3 = st.columns(3)
        with col1:
            min_score = st.slider("Minimum score", 0, 10, 6)
        with col2:
            show_applied = st.checkbox("Show all scores", value=False)
        with col3:
            date_filter = st.selectbox(
                "Date range",
                ["Today", "Last 7 days", "Last 30 days", "All time"]
            )

        # --- Filter logic ---
        filtered = matches.copy()

        if not show_applied:
            filtered = filtered[filtered["score"] >= min_score]

        if date_filter == "Today":
            filtered = filtered[filtered["date_scored"].dt.date == date.today()]
        elif date_filter == "Last 7 days":
            filtered = filtered[filtered["date_scored"] >= pd.Timestamp.now() - pd.Timedelta(days=7)]
        elif date_filter == "Last 30 days":
            filtered = filtered[filtered["date_scored"] >= pd.Timestamp.now() - pd.Timedelta(days=30)]

        filtered = filtered.sort_values("score", ascending=False)

        # --- Summary metrics ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total matches", len(filtered))
        col2.metric("Score ≥ 8", len(filtered[filtered["score"] >= 8]))
        col3.metric("Score ≥ 6", len(filtered[filtered["score"] >= 6]))
        col4.metric("Avg score", f"{filtered['score'].mean():.1f}" if not filtered.empty else "—")

        st.divider()

        # --- Job cards ---
        for _, job in filtered.iterrows():
            score = int(job.get("score", 0))

            # Colour code by score
            if score >= 8:
                badge = "🟢"
            elif score >= 6:
                badge = "🟡"
            else:
                badge = "🔴"

            with st.expander(f"{badge} **{score}/10** — {job.get('company_name')} · {job.get('title')} · {job.get('location', 'Location unknown')}"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Summary:** {job.get('summary', '—')}")

                    green = job.get("green_flags", "")
                    if green:
                        st.write("**✅ Green flags:**")
                        for flag in str(green).split(" | "):
                            st.write(f"- {flag}")

                    yellow = job.get("yellow_flags", "")
                    if yellow:
                        st.write("**⚠️ Yellow flags:**")
                        for flag in str(yellow).split(" | "):
                            st.write(f"- {flag}")

                with col2:
                    st.metric("Score", f"{score}/10")
                    if job.get("salary"):
                        st.write(f"💰 {job.get('salary')}")
                    if job.get("url"):
                        st.link_button("View listing →", job.get("url"))
                    st.write(f"📅 {job.get('date_scored', '').strftime('%d %b %Y') if pd.notna(job.get('date_scored')) else '—'}")


# ---------------------------------------------------------------------------
# Tab 2 — Companies
# ---------------------------------------------------------------------------
with tab2:
    if companies.empty:
        st.info("No companies loaded yet.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            source_filter = st.multiselect(
                "Source",
                options=companies["source"].unique().tolist(),
                default=companies["source"].unique().tolist()
            )
        with col2:
            search = st.text_input("Search companies", placeholder="Type to filter...")

        filtered_cos = companies[companies["source"].isin(source_filter)]
        if search:
            filtered_cos = filtered_cos[
                filtered_cos["company_name"].str.contains(search, case=False, na=False)
            ]

        # Summary
        col1, col2, col3 = st.columns(3)
        col1.metric("Total companies", len(filtered_cos))
        col2.metric("Seed list", len(filtered_cos[filtered_cos["source"] == "seed"]))
        col3.metric("AI discovered", len(filtered_cos[filtered_cos["source"] == "ai_discovered"]))

        st.divider()

        # Table
        st.dataframe(
            filtered_cos[["company_name", "source", "status", "excluded"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "company_name": "Company",
                "source": "Source",
                "status": "Status",
                "excluded": "Excluded"
            }
        )
