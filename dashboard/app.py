import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Federal Layoffs Dashboard", layout="wide")

# === HEADER ===
st.markdown("""
    <h1 style='text-align: center; color: white; background-color: #003366; padding: 25px; border-radius: 8px'>
    📊 Federal Workforce Layoffs and AI Exposure
    </h1>
""", unsafe_allow_html=True)

# === LOAD DATA ===
df = pd.read_csv("data/dashboard_ai_tagged.csv.gz", compression='gzip')
summary = pd.read_csv("data/dashboard_agency_state_summary.csv")
layoff_signals = pd.read_csv("data/federal_layoff_signal.csv", encoding='latin1')

# Check actual column names for layoff_signals
layoff_signals.columns = layoff_signals.columns.str.strip().str.lower()

# === SIDEBAR FILTERS ===
st.sidebar.header("🔍 Filter Dashboard")

# SaaS-style State Filter
st.sidebar.markdown("### 📺 Select State(s)")
all_states = sorted(df['location_name'].dropna().unique())
select_all_states = st.sidebar.checkbox("Select All States", value=True)
if select_all_states:
    selected_states = st.sidebar.multiselect("States", all_states, default=all_states)
else:
    selected_states = st.sidebar.multiselect("States", all_states)

# SaaS-style Agency Filter
st.sidebar.markdown("### 🏢 Select Department(s)")
all_departments = sorted(df['agency_name'].dropna().unique())
select_all_departments = st.sidebar.checkbox("Select All Departments", value=True)
if select_all_departments:
    selected_departments = st.sidebar.multiselect("Departments", all_departments, default=all_departments)
else:
    selected_departments = st.sidebar.multiselect("Departments", all_departments)

# AI Filter
ai_filter = st.sidebar.selectbox("AI Exposure Filter", options=["All", "AI-Exposed Only", "Non-AI"])

# === APPLY FILTERS ===
filtered_df = df[df['location_name'].isin(selected_states) & df['agency_name'].isin(selected_departments)]
if ai_filter == "AI-Exposed Only":
    filtered_df = filtered_df[filtered_df['ai_exposed'] == 1]
elif ai_filter == "Non-AI":
    filtered_df = filtered_df[filtered_df['ai_exposed'] == 0]

# === KPI METRICS ===
st.subheader("📊 Key Workforce Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("👥 Total Employees", int(filtered_df['employee_count_2024'].sum()))
col2.metric("🚫 Estimated Layoffs", int(filtered_df['layoff_estimate'].sum()))
col3.metric("🧑‍🤖 AI-Tagged Roles", int(filtered_df['ai_exposed'].sum()))

# === CHARTS SECTION ===
st.markdown("### 🔺 Layoff Estimates by Department")
barchart = filtered_df.groupby('agency_name')['layoff_estimate'].sum().sort_values(ascending=False).head(10)
st.plotly_chart(px.bar(
    barchart,
    x=barchart.index,
    y=barchart.values,
    labels={'x': 'Agency', 'y': 'Layoff Estimate'},
    title="Top 10 Agencies by Layoff Estimate"
), use_container_width=True)

st.markdown("### 🤖 Top AI-Exposed Job Titles")
ai_jobs = filtered_df[filtered_df['ai_exposed'] == 1].groupby('occupation_title')['employee_count_2024'].sum().sort_values(ascending=False).head(10)
st.plotly_chart(px.bar(
    ai_jobs,
    x=ai_jobs.index,
    y=ai_jobs.values,
    labels={'x': 'Occupation', 'y': 'Employees'},
    title="Top AI-Tagged Roles by Headcount"
), use_container_width=True)

# === LAYOFF TREND SECTION ===
st.markdown("### 📉 Layoff News Trend Over Time")
if 'date' in layoff_signals.columns:
    layoff_signals['date'] = pd.to_datetime(layoff_signals['date'], dayfirst=True)
    layoff_signals['estimated_layoff'] = pd.to_numeric(layoff_signals['estimated_layoff'], errors='coerce')
    trend = layoff_signals.groupby(layoff_signals['date'].dt.to_period("M"))['estimated_layoff'].sum().reset_index()
    trend['date'] = trend['date'].astype(str)
    st.line_chart(trend.rename(columns={'estimated_layoff': 'Layoffs'}).set_index('date'))
else:
    st.warning("\u26a0\ufe0f 'date' column not found in layoff_signals.csv. Please check column headers.")

# === FOOTER ===
st.markdown("---")
st.caption("Built with Streamlit | Data: US Federal Workforce & Layoffs | Powered by Plotly")
