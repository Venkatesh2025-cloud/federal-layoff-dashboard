# federal_layoffs_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Federal Layoffs & Skills Explorer", layout="wide")

# === Load Datasets ===
@st.cache_data
def load_data():
    df_ai = pd.read_csv("data/dashboard_ai_tagged_slim.csv.gz", compression="gzip")
    df_dept = pd.read_csv("data/agency_department_map.csv", encoding='utf-8')
    df_summary = pd.read_csv("data/dashboard_agency_state_summary.csv")
    df_signal = pd.read_csv("data/federal_layoff_signal.csv")
    df_sim = pd.read_csv("data/occupation_similarity_matrix.csv", index_col=0)
    return df_ai, df_dept, df_summary, df_signal, df_sim

required = [
    "data/dashboard_ai_tagged_slim.csv.gz",
    "data/agency_department_map.csv",
    "data/dashboard_agency_state_summary.csv",
    "data/federal_layoff_signal.csv",
    "data/occupation_similarity_matrix.csv"
]

missing = [f for f in required if not os.path.exists(f)]
if missing:
    st.error(f"Missing required files: {', '.join(missing)}")
    st.stop()

# === Load
try:
    df_ai, df_dept, df_summary, df_signal, df_sim = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# === Column Cleanup ===
for df in [df_ai, df_dept, df_summary, df_signal]:
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

df_sim.columns = df_sim.columns.str.strip().str.lower()
df_sim.index = df_sim.index.str.strip().str.lower()
df_sim.index.name = "occupation"

# === Merge department
df_ai = df_ai.merge(df_dept.rename(columns={"agency_department": "department"}), on="agency_name", how="left")

# === Sidebar Filters ===
st.sidebar.title("🔍 Filters")
state = st.sidebar.selectbox("Select a State", sorted(df_ai['state'].dropna().unique()))
agency_list = df_ai[df_ai['state'] == state]['agency_name'].unique().tolist()
agency = st.sidebar.selectbox("Select Agency", ["All"] + agency_list)

# === Filtered Data ===
data_filtered = df_ai[df_ai['state'] == state]
if agency != "All":
    data_filtered = data_filtered[data_filtered['agency_name'] == agency]

# === Header ===
st.markdown("""
    <h1 style='text-align: center; background-color: #003366; color: white; padding: 0.75rem; border-radius: 6px;'>
        📊 Federal Layoffs & Skills Intelligence Dashboard
    </h1>
""", unsafe_allow_html=True)

# === KPI ===
k1, k2, k3, k4 = st.columns(4)
k1.metric("👥 Workforce", f"{data_filtered['employee_count_2024'].sum():,}")
k2.metric("⚠️ Layoffs Est.", f"{data_filtered['estimate_layoff'].sum():,}")
k3.metric("🔧 Skills", f"{data_filtered['skill'].nunique():,}")
k4.metric("🤖 AI Risk Count", f"{data_filtered['ai_impact_flag'].sum():,}")

# === Tabs ===
t1, t2, t3, t4 = st.tabs(["💡 Skills", "💼 Occupations", "📰 Layoff Signals", "🔄 Similar Occupations"])

with t1:
    st.subheader("Top Skills At Risk")
    top_skills = data_filtered.groupby("skill")["estimate_layoff"].sum().reset_index()
    top_skills = top_skills.sort_values("estimate_layoff", ascending=False).head(10)
    fig = px.bar(top_skills, x="skill", y="estimate_layoff", title="Top 10 At-Risk Skills", height=400)
    st.plotly_chart(fig, use_container_width=True)

with t2:
    st.subheader("Occupation Drilldown")
    top_jobs = data_filtered.groupby("occupation")["estimate_layoff"].sum().reset_index()
    top_jobs = top_jobs.sort_values("estimate_layoff", ascending=False).head(10)
    for _, row in top_jobs.iterrows():
        job = row['occupation']
        subset = data_filtered[data_filtered['occupation'] == job]
        with st.expander(f"{job} (Est. Layoffs: {row['estimate_layoff']})"):
            st.dataframe(subset[['skill', 'estimate_layoff', 'ai_impact_flag']], use_container_width=True)

with t3:
    st.subheader("Layoff News")
    signals = df_signal[df_signal['state'] == state][['date', 'agency_name', 'estimated_layoff', 'source_link', 'article_title']]
    st.dataframe(signals, use_container_width=True)

with t4:
    st.subheader("Similar Occupations")
    occ = st.selectbox("Choose Occupation", sorted(df_ai['occupation'].unique()))
    occ_key = occ.strip().lower()
    if occ_key in df_sim.index:
        sim = df_sim.loc[occ_key].sort_values(ascending=False).head(10).reset_index()
        sim.columns = ['occupation', 'similarity']
        fig = px.bar(sim, x='occupation', y='similarity', title=f"Jobs Similar to '{occ}'")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No similarity data available for this job title.")

st.markdown("---")
st.caption("Crafted with 💙 using Streamlit — Federal Workforce Insights, Skills & Layoffs")
