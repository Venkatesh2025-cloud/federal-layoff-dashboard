# federal_layoffs_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
import os

st.set_page_config(page_title="Federal Skill Risk & Layoff Explorer", layout="wide")

# === Load from Local Directory for Shared View ===
@st.cache_data
def load_data():
    df_ai = pd.read_csv("data/dashboard_ai_tagged.csv.gz", compression='gzip')
    df_dept_map = pd.read_csv("data/agency_department_map.csv")
    df_summary = pd.read_csv("data/dashboard_agency_state_summary.csv")
    df_signal = pd.read_csv("data/federal_layoff_signal.csv")
    df_sim = pd.read_csv("data/occupation_similarity_matrix.csv", index_col=0)
    return df_ai, df_dept_map, df_summary, df_signal, df_sim

# Load datasets
try:
    df_ai, df_dept_map, df_summary, df_signal, df_sim = load_data()
except FileNotFoundError:
    st.error("One or more required files are missing in the 'data/' folder. Please ensure all five datasets are available.")
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
k4.metric("🤖 AI Exposure Count", f"{data_filtered['ai_exposure'].sum():,}")

# === Tabs ===
t1, t2, t3, t4 = st.tabs(["📊 Skills", "💼 Occupations", "📰 Layoff Signals", "🔄 Similar Occupations"])

with t1:
    st.subheader("Top Skills at Risk")
    top_skills = data_filtered.groupby("skill")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(10)
    fig = px.bar(top_skills, x="skill", y="estimate_layoff", title="Top At-Risk Skills")
    st.plotly_chart(fig, use_container_width=True)

with t2:
    st.subheader("Occupational Breakdown")
    top_jobs = data_filtered.groupby("occupation")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(10)
    for _, row in top_jobs.iterrows():
        job = row['occupation']
        job_subset = data_filtered[data_filtered['occupation'] == job]
        with st.expander(f"{job} - Est. Layoffs: {int(row['estimate_layoff'])}"):
            st.dataframe(job_subset[['skill', 'estimate_layoff', 'ai_exposure']], use_container_width=True)

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
