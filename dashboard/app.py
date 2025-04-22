import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Federal Workforce Skill Risk Dashboard", layout="wide")

# === Load Data ===
data_path = "data"
df = pd.read_csv(os.path.join(data_path, "clean_dashboard_ai_tagged.csv"))
df.columns = df.columns.str.strip().str.lower()

# === Sidebar Filters ===
st.sidebar.header("📍 Filter Options")
selected_state = st.sidebar.selectbox("Select a State", sorted(df['location_name'].dropna().unique()))

filtered_df = df[df['location_name'] == selected_state]

# === KPI Row ===
st.markdown("""
    <h1 style='text-align: center; color: white; background-color: #003366; padding: 25px; border-radius: 8px'>
    🧠 Federal Workforce Skill Risk Dashboard
    </h1>
""", unsafe_allow_html=True)

k1, k2, k3 = st.columns(3)
k1.metric("👥 Total Employees", f"{filtered_df['employee_count_2024'].sum():,}")
k2.metric("⚠️ Estimated Layoffs", f"{filtered_df['layoff_estimate'].sum():,}")
k3.metric("🔧 Unique Skills", f"{filtered_df['skill'].nunique():,}")

# === Tabs ===
tab1, tab2, tab3 = st.tabs(["📊 Skill Risk Explorer", "🧑‍💼 Job Role Intelligence", "🗺️ Geo Skill Map"])

with tab1:
    st.subheader(f"Top At-Risk Skills in {selected_state}")
    top_skills = (
        filtered_df.groupby("skill")["layoff_estimate"]
        .sum()
        .reset_index()
        .sort_values(by="layoff_estimate", ascending=False)
        .head(10)
    )
    fig = px.bar(top_skills, x="skill", y="layoff_estimate", color="layoff_estimate",
                 height=400, title="🔧 Top 10 Skills by Layoff Estimate")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_skills, use_container_width=True)

with tab2:
    st.subheader(f"Top Jobs by Layoff Estimate in {selected_state}")
    top_jobs = (
        filtered_df.groupby("occupation_title")["layoff_estimate"]
        .sum()
        .reset_index()
        .sort_values(by="layoff_estimate", ascending=False)
        .head(5)
    )
    for _, row in top_jobs.iterrows():
        job = row["occupation_title"]
        subset = filtered_df[filtered_df["occupation_title"] == job]
        with st.expander(f"💼 {job} - Est. Layoffs: {int(row['layoff_estimate'])}"):
            skill_dist = subset.groupby("skill")["layoff_estimate"].sum().reset_index()
            fig = px.bar(skill_dist, x="skill", y="layoff_estimate", title=f"Skills at Risk in {job}")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(skill_dist, use_container_width=True)

with tab3:
    st.info("🌍 Geo Map module coming soon — currently focusing on state-level skill risks.")

# === Footer ===
st.markdown("---")
st.caption("Built for workforce planning and skill risk intelligence | Streamlit SaaS Design")
