import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("data/dashboard_ai_tagged.csv.gz", compression="gzip")
summary = pd.read_csv("data/dashboard_agency_state_summary.csv")
layoff_signals = pd.read_csv("data/federal_layoff_signal.csv", encoding="ISO-8859-1")

# Title
st.title("Federal Workforce Layoffs Dashboard")
st.markdown("A visual exploration of skills, layoffs, and AI exposure across U.S. federal agencies.")

# Sidebar filters
states = st.sidebar.multiselect("Select State(s)", options=df['location_name'].unique(), default=df['location_name'].unique())
departments = st.sidebar.multiselect("Select Department(s)", options=df['agency_name'].unique(), default=df['agency_name'].unique())
ai_filter = st.sidebar.selectbox("AI Exposure", options=["All", "AI-Exposed Only", "Non-AI"])

# Filter logic
filtered_df = df[df['location_name'].isin(states) & df['agency_name'].isin(departments)]
if ai_filter == "AI-Exposed Only":
    filtered_df = filtered_df[filtered_df['ai_exposed'] == 1]
elif ai_filter == "Non-AI":
    filtered_df = filtered_df[filtered_df['ai_exposed'] == 0]

# KPI section
col1, col2, col3 = st.columns(3)
col1.metric("Total Employees", int(filtered_df['employee_count_2024'].sum()))
col2.metric("Est. Layoffs", int(filtered_df['layoff_estimate'].sum()))
col3.metric("AI-Tagged Roles", int(filtered_df['ai_exposed'].sum()))

# Charts
st.subheader("Layoff Estimates by Department")
barchart = filtered_df.groupby('agency_name')['layoff_estimate'].sum().sort_values(ascending=False).head(10)
st.plotly_chart(px.bar(barchart, x=barchart.index, y=barchart.values, labels={'x': 'Agency', 'y': 'Layoff Estimate'}))

st.subheader("Top AI-Exposed Job Titles")
ai_jobs = filtered_df[filtered_df['ai_exposed'] == 1].groupby('occupation_title')['employee_count_2024'].sum().sort_values(ascending=False).head(10)
st.plotly_chart(px.bar(ai_jobs, x=ai_jobs.index, y=ai_jobs.values, labels={'x': 'Occupation', 'y': 'Employees'}))

# Layoff trend
st.subheader("Layoff News Signal Trend")
layoff_signals['date'] = pd.to_datetime(layoff_signals['date'], dayfirst=True)
layoff_signals['estimated_layoff'] = pd.to_numeric(layoff_signals['estimated_layoff'], errors='coerce')
trend = layoff_signals.groupby(layoff_signals['date'].dt.to_period("M"))['estimated_layoff'].sum().reset_index()
trend['date'] = trend['date'].astype(str)
st.line_chart(trend.rename(columns={'estimated_layoff': 'Layoffs'}).set_index('date'))

# Footer
st.markdown("---")
st.caption("Built with Streamlit | Data: US Federal Layoffs + Workforce Insights")
