# federal_layoffs_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Federal Skill Risk & Layoff Explorer", layout="wide")

# === Safe CSV Reader with Encoding Fallback ===
def safe_read_csv(path):
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin1")

# === Load from Local Directory ===
@st.cache_data
def load_data():
    df_ai = pd.read_csv("data/dashboard_ai_tagged_renamed.csv.gz", compression="gzip")
    df_agency = safe_read_csv("data/agency_department_map.csv")
    df_summary = safe_read_csv("data/dashboard_agency_state_summary.csv")
    df_signal = safe_read_csv("data/federal_layoff_signal.csv")
    df_sim = safe_read_csv("data/occupation_similarity_matrix.csv")
    df_sim.set_index(df_sim.columns[0], inplace=True)
    return df_ai, df_agency, df_summary, df_signal, df_sim

# Validate files exist
required_files = [
    "data/dashboard_ai_tagged_renamed.csv.gz",
    "data/agency_department_map.csv",
    "data/dashboard_agency_state_summary.csv",
    "data/federal_layoff_signal.csv",
    "data/occupation_similarity_matrix.csv"
]

missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    st.error(f"Missing required file(s): {', '.join(missing)}. Please ensure all five datasets are in the 'data/' folder.")
    st.stop()

# Load datasets
try:
    df_ai, df_dept_map, df_summary, df_signal, df_sim = load_data()
except Exception as e:
    st.error(f"Failed to load datasets: {e}")
    st.stop()

# === Clean Column Names ===
for df in [df_ai, df_dept_map, df_summary, df_signal]:
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

df_sim.columns = df_sim.columns.str.lower().str.strip()
df_sim.index = df_sim.index.str.lower().str.strip()

# === Merge Department Mapping ===
df_ai = df_ai.merge(df_dept_map.rename(columns={"agency_department": "department"}), on="agency_name", how="left")

# === Sidebar Filters ===
st.sidebar.header("🔍 Filters")
all_states = sorted(df_ai['state'].dropna().unique())
state = st.sidebar.selectbox("Select a State", all_states)
agencies = sorted(df_ai[df_ai['state'] == state]['agency_name'].dropna().unique())
agency = st.sidebar.selectbox("Agency", ["All"] + agencies)

# === Filtered AI-tagged Data ===
data_filtered = df_ai[df_ai['state'] == state]
if agency != "All":
    data_filtered = data_filtered[data_filtered['agency_name'] == agency]

# === KPI Summary ===
st.markdown("""
    <h1 style='text-align: center; background-color: #003366; color: white; padding: 1rem; border-radius: 8px;'>
        Federal Layoffs & Skills Intelligence Dashboard
    </h1>
""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
k1.metric("👥 Total Workforce", f"{data_filtered['employee_count_2024'].sum():,}")
k2.metric("⚠️ Estimated Layoffs", f"{data_filtered['estimate_layoff'].sum():,}")
k3.metric("🔧 Unique Skills", f"{data_filtered['skill'].nunique():,}")
k4.metric("🤖 AI Impact Count", f"{data_filtered['ai_impact_flag'].sum():,}")

# === Tabs ===
t1, t2, t3, t4 = st.tabs(["📊 Skills", "💼 Occupations", "📰 Layoff Signals", "🔄 Similar Occupations"])

with t1:
    st.markdown("""
        <div style='padding: 1rem; background-color: #003366; border-radius: 6px;'>
            <h2 style='color: white;'>🔍 Federal Layoff Intelligence Overview — <span style='font-weight:400;'>State: {}</span></h2>
        </div>
    """.format(state), unsafe_allow_html=True)

    k1, k2 = st.columns([2, 1])
    with k1:
        st.subheader("🎯 Top 5 Occupations by Estimated Layoffs")
        top_occ = (
            data_filtered.groupby("occupation")["estimate_layoff"]
            .sum().sort_values(ascending=False).head(5).reset_index()
        )
        fig_occ = px.bar(top_occ, x="occupation", y="estimate_layoff",
                         labels={"estimate_layoff": "Layoffs"},
                         title="Top Occupations", color="estimate_layoff")
        st.plotly_chart(fig_occ, use_container_width=True)

    with k2:
        st.subheader("⚙️ Quick Summary")
        st.metric("Occupations Tracked", f"{data_filtered['occupation'].nunique():,}")
        st.metric("Unique Skills", f"{data_filtered['skill'].nunique():,}")
        st.metric("Total Layoffs", f"{int(data_filtered['estimate_layoff'].sum()):,}")

    # 🔍 DRILL-DOWN: Skills Per Occupation
    st.markdown("### 🧠 Skill Insights per Occupation")
    for job in top_occ["occupation"]:
        job_data = data_filtered[data_filtered["occupation"] == job]
        top_skills = job_data.groupby("skill")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(5)

        with st.expander(f"💼 {job} — Top Skills at Risk"):
            chart = px.bar(top_skills, x="skill", y="estimate_layoff", color="estimate_layoff",
                           labels={"estimate_layoff": "Estimated Layoff"}, title=f"{job}: Top Skills at Risk")
            st.plotly_chart(chart, use_container_width=True)
            st.dataframe(job_data[["skill", "estimate_layoff", "ai_impact_flag"]], use_container_width=True)

with t3:
    st.subheader("Federal Layoff News")
    signal_filtered = df_signal[df_signal['state'] == state]
    st.dataframe(signal_filtered[['date', 'agency_name', 'estimated_layoff', 'source_link', 'article_title']], use_container_width=True)

with t4:
    st.subheader("Explore Similar Occupations")
    selected_job = st.selectbox("Select Occupation", sorted(df_ai['occupation'].dropna().unique()))
    if selected_job:
        selected_key = selected_job.lower().strip()
        if selected_key in df_sim.index:
            similar_jobs = df_sim.loc[selected_key].sort_values(ascending=False).head(10).reset_index()
            similar_jobs.columns = ['occupation', 'similarity_score']
            fig = px.bar(similar_jobs, x='occupation', y='similarity_score', title=f"Most Similar Occupations to {selected_job}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Similarity data not available for this occupation.")

# === Footer ===
st.markdown("---")
st.caption("Built by Data Scientist & UX Strategist — Unified workforce insights from five datasets")
