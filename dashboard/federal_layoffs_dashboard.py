# federal_layoffs_dashboard.py

import pandas as pd
import streamlit as st
import plotly.express as px
import os

st.set_page_config(page_title="Federal Layoffs & Skills Intelligence Dashboard", layout="wide")

# === Safe CSV Reader ===
def safe_read_csv(path):
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin1")

# === Load Datasets ===
@st.cache_data
def load_data():
    df = safe_read_csv("data/dashboard_ai_tagged_cleaned.csv")
    df_summary = safe_read_csv("data/dashboard_agency_state_summary.csv")
    df_signal = safe_read_csv("data/federal_layoff_signal.csv")
    df_sim = pd.read_csv("data/occupation_similarity_matrix.csv", index_col=0)
    return df, df_summary, df_signal, df_sim

# Validate all required files exist
required_files = [
    "data/dashboard_ai_tagged_cleaned.csv",
    "data/dashboard_agency_state_summary.csv",
    "data/federal_layoff_signal.csv",
    "data/occupation_similarity_matrix.csv"
]

missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    st.error(f"Missing required file(s): {', '.join(missing)}")
    st.stop()

# Load data
try:
    df, df_summary, df_signal, df_sim = load_data()
except Exception as e:
    st.error(f"Failed to load datasets: {e}")
    st.stop()

# Clean column names
for d in [df, df_summary, df_signal]:
    d.columns = d.columns.str.lower().str.strip().str.replace(" ", "_")

df_sim.columns = df_sim.columns.str.lower().str.strip()
df_sim.index = df_sim.index.str.lower().str.strip()

# === Sidebar Filters ===
st.sidebar.header("📍 Filter by State")
state_list = sorted(df['state'].unique())
selected_state = st.sidebar.selectbox("State", state_list)

# === Apply Filter ===
df_filtered = df[df['state'] == selected_state]

# === Header ===
st.markdown("""
    <h1 style='text-align: center; background-color: #003366; color: white; padding: 1rem; border-radius: 8px;'>
        Federal Layoffs & Skills Intelligence Dashboard
    </h1>
""", unsafe_allow_html=True)

# === KPI Section ===
k1, k2, k3 = st.columns(3)
k1.metric("👥 Total Workforce", f"{df_filtered['talent_size'].sum():,}")
k2.metric("⚠️ Estimated Layoffs", f"{df_filtered['estimate_layoff'].sum():,}")
k3.metric("🔧 Unique Skills", f"{df_filtered['skill'].nunique():,}")

# === Tabs ===
t1, t2, t3 = st.tabs(["🧠 Federal Layoff Intelligence", "📰 Layoff News", "🔁 Similar Occupations (Optional)"])

with t1:
    st.subheader(f"Top 10 Skills at Risk in {selected_state}")
    top_skills = df_filtered.groupby("skill")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(5)
    fig_skills = px.bar(top_skills, x="skill", y="estimate_layoff",
                        title="Top Skills by Estimated Layoffs",
                        color_discrete_sequence=["#ddeeff", "#a9d0f5", "#7ec0ee", "#3b9dd1", "#007acc"])
    st.plotly_chart(fig_skills, use_container_width=True)

    st.subheader("Top 10 Occupations by Estimated Layoffs")
    top_jobs = df_filtered.groupby("occupation")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(5)
    fig_jobs = px.bar(top_jobs, x="occupation", y="estimate_layoff",
                     title="Top Occupations by Estimated Layoffs",
                     color_discrete_sequence=["#fde0dc", "#fbb4ae", "#f768a1", "#c51b8a", "#7a0177"])
    st.plotly_chart(fig_jobs, use_container_width=True)

with t2:
    st.subheader(f"Layoff News in {selected_state}")
    df_signal_filtered = df_signal[df_signal['state'] == selected_state]
    st.dataframe(df_signal_filtered[["date", "agency_name", "estimated_layoff", "article_title", "source_link"]], use_container_width=True)

with t3:
    st.subheader("Explore Similar Occupations (Optional)")
    selected_occ = st.selectbox("Choose an occupation", sorted(df['occupation'].unique()))
    selected_key = selected_occ.lower().strip()
    if selected_key in df_sim.index:
        similar_df = df_sim.loc[selected_key].sort_values(ascending=False).head(10).reset_index()
        similar_df.columns = ['occupation', 'similarity']
        fig_sim = px.bar(similar_df, x='occupation', y='similarity',
                         title=f"Most Similar to {selected_occ}",
                         color='similarity',
                         color_continuous_scale=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_sim, use_container_width=True)
    else:
        st.info("Similarity data not available for this occupation.")

# === Footer ===
st.markdown("---")
st.caption("Built with ❤️ by your data + design team. Data source: Draup")
