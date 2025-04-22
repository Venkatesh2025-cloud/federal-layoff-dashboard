import streamlit as st
import pandas as pd
import plotly.express as px
import os
import zipfile

st.set_page_config(page_title="Federal Workforce Skill Risk Dashboard", layout="wide")

# === Load Data from ZIP or FileUploader ===
zip_path = "clean_dashboard_ai_tagged.zip"  # Updated filename
csv_name = "data/clean_dashboard_ai_tagged.csv"  # Path inside the ZIP

uploaded_zip = st.sidebar.file_uploader("📁 Upload ZIP with Clean Data", type="zip")
if uploaded_zip is not None:
    with zipfile.ZipFile(uploaded_zip) as z:
        with z.open(csv_name) as f:
            df = pd.read_csv(f)
else:
    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(csv_name) as f:
            df = pd.read_csv(f)

# === Clean Columns ===
df.columns = df.columns.str.strip().str.lower()

# === Sidebar Filters ===
st.sidebar.header("📍 Filter Options")
selected_state = st.sidebar.selectbox("Select a State", sorted(df['location_name'].dropna().unique()))

unique_skills = sorted(df['skill'].unique())
skill_filter = st.sidebar.multiselect("Search or select skills", unique_skills)

ai_only = st.sidebar.checkbox("Show only AI-exposed skills", value=False)

filtered_df = df[df['location_name'] == selected_state]
if skill_filter:
    filtered_df = filtered_df[filtered_df['skill'].isin(skill_filter)]
if ai_only:
    filtered_df = filtered_df[filtered_df['ai_exposed'] == 1]

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
    skill_summary = (
        filtered_df.groupby("skill")["layoff_estimate"]
        .sum()
        .reset_index()
        .sort_values(by="layoff_estimate", ascending=False)
    )

    show_more = st.checkbox("Show full skill list", value=False)
    display_data = skill_summary if show_more else skill_summary.head(10)

    fig = px.bar(display_data, x="skill", y="layoff_estimate", color="layoff_estimate",
                 height=400, title="🔧 Skills by Layoff Estimate",
                 hover_data={"layoff_estimate": True})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(display_data, use_container_width=True)

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
