# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Federal Skill Risk Explorer", layout="wide")

# === Load Data ===
@st.cache_data

def load_data():
    df_ai = pd.read_csv("data/dashboard_ai_tagged_slim.csv.gz", compression="gzip")
    df_dept_map = pd.read_csv("data/agency_department_map.csv")
    df_summary = pd.read_csv("data/dashboard_agency_state_summary.csv")
    df_signal = pd.read_csv("data/federal_layoff_signal.csv")
    df_sim = pd.read_csv("data/occupation_similarity_matrix.csv", index_col=0)
    return df_ai, df_dept_map, df_summary, df_signal, df_sim

required_files = [
    "data/dashboard_ai_tagged_slim.csv.gz",
    "data/agency_department_map.csv",
    "data/dashboard_agency_state_summary.csv",
    "data/federal_layoff_signal.csv",
    "data/occupation_similarity_matrix.csv"
]

missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    st.error(f"Missing file(s): {', '.join(missing)}")
    st.stop()

# === Load & Clean ===
df_ai, df_dept_map, df_summary, df_signal, df_sim = load_data()
for df in [df_ai, df_dept_map, df_summary, df_signal]:
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
df_sim.columns = df_sim.columns.str.strip().str.lower()
df_sim.index = df_sim.index.str.strip().str.lower()

# === Join Department Mapping ===
df_ai = df_ai.merge(
    df_dept_map.rename(columns={"agency_department": "department"}),
    on="agency_name", how="left"
)

# === Sidebar Filters ===
st.sidebar.header("🔍 Filters")
states = sorted(df_ai['state'].dropna().unique())
state = st.sidebar.selectbox("Select State", states)
agencies = sorted(df_ai[df_ai['state'] == state]['agency_name'].unique())
agency = st.sidebar.selectbox("Select Agency", ["All"] + agencies)

filtered = df_ai[df_ai['state'] == state]
if agency != "All":
    filtered = filtered[filtered['agency_name'] == agency]

# === Main Title ===
st.markdown("""
    <h1 style='text-align: center; background-color: #003366; color: white; padding: 1rem; border-radius: 8px;'>
        Federal Workforce Intelligence Dashboard
    </h1>
""", unsafe_allow_html=True)

# === KPI Cards ===
k1, k2, k3, k4 = st.columns(4)
k1.metric("👥 Workforce", f"{filtered['employee_count_2024'].sum():,}")
k2.metric("⚠️ Layoff Estimate", f"{filtered['estimate_layoff'].sum():,}")
k3.metric("🔧 Skills", f"{filtered['skill'].nunique():,}")
k4.metric("🤖 AI Impact", f"{filtered['ai_impact_flag'].sum():,}")

# === Tabs ===
t1, t2, t3, t4 = st.tabs(["📊 Skills", "💼 Occupations", "📰 Layoff News", "🔄 Similar Jobs"])

with t1:
    st.subheader("Top At-Risk Skills")
    top_skills = filtered.groupby("skill")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(10)
    fig = px.bar(top_skills, x="skill", y="estimate_layoff", title="Top Skills by Layoff Impact")
    st.plotly_chart(fig, use_container_width=True)

with t2:
    st.subheader("Occupation Breakdown")
    top_jobs = filtered.groupby("occupation")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(10)
    for _, row in top_jobs.iterrows():
        with st.expander(f"{row['occupation']} — {int(row['estimate_layoff']):,} Layoffs"):
            df_occ = filtered[filtered['occupation'] == row['occupation']]
            st.dataframe(df_occ[['skill', 'estimate_layoff', 'ai_impact_flag']], use_container_width=True)

with t3:
    st.subheader("Layoff-Related News")
    signal_filtered = df_signal[df_signal['state'] == state]
    st.dataframe(signal_filtered[['date', 'agency_name', 'estimated_layoff', 'source_link', 'article_title']], use_container_width=True)

with t4:
    st.subheader("Explore Similar Roles")
    selected_job = st.selectbox("Choose an Occupation", sorted(df_ai['occupation'].dropna().unique()))
    if selected_job:
        job_key = selected_job.lower().strip()
        if job_key in df_sim.index:
            sim_jobs = df_sim.loc[job_key].sort_values(ascending=False).head(10).reset_index()
            sim_jobs.columns = ['occupation', 'similarity']
            fig = px.bar(sim_jobs, x='occupation', y='similarity', title=f"Most Similar to {selected_job}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Occupation not found in similarity index.")

# === Footer ===
st.markdown("""---
Built with care — Empowering human-centered workforce intelligence
""")
