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
st.sidebar.header("🌟 Filters")

all_states = sorted(df['location_name'].dropna().unique())
selected_state = st.sidebar.selectbox("Select a State", all_states)

# === KPI ROW ===
st.markdown("""
<div style="display: flex; justify-content: space-between; padding: 10px 0 20px 0;">
    <div style="text-align: center; flex: 1;">
        <h3 style="color: #3366cc;">🎓 Skill Categories</h3>
        <h1 style="color: #111;">{}</h1>
    </div>
    <div style="text-align: center; flex: 1;">
        <h3 style="color: #3366cc;">👥 Available Talent</h3>
        <h1 style="color: #111;">{:,}</h1>
    </div>
    <div style="text-align: center; flex: 1;">
        <h3 style="color: #3366cc;">🏆 Most Available Skill</h3>
        <h1 style="color: #111;">{}</h1>
    </div>
</div>
""".format(
    df['skill'].nunique(),
    df['employee_count_2024'].sum(),
    df.groupby('skill')['employee_count_2024'].sum().idxmax()
), unsafe_allow_html=True)

# === TABS ===
tab1, tab2, tab3 = st.tabs([
    "Federal Agency Staff",
    "Layoff News",
    "Federal Layoff Intelligence"
])

with tab1:
    st.subheader("🏢 Federal Agency Workforce Summary")
    filtered_summary = summary[summary['state'] == selected_state]
    agency_summary = filtered_summary.groupby('agency_name').agg({
        'employee_count_2024': 'sum',
        'layoff_estimate': 'sum'
    }).reset_index().sort_values(by='employee_count_2024', ascending=False).head(10)

    fig_summary = px.bar(
        agency_summary,
        x='agency_name',
        y='employee_count_2024',
        color='layoff_estimate',
        title=f"Top 10 Federal Agencies in {selected_state} by Workforce Size",
        labels={'employee_count_2024': 'Employees', 'layoff_estimate': 'Estimated Layoffs'},
        height=450
    )
    st.plotly_chart(fig_summary, use_container_width=True)
    st.dataframe(agency_summary, use_container_width=True)

with tab2:
    st.subheader(f"📰 Layoff News — {selected_state}")
    filtered_layoffs = layoff_signals[layoff_signals['locations impacted'].str.contains(selected_state, case=False, na=False)]
    if not filtered_layoffs.empty:
        filtered_layoffs['date'] = pd.to_datetime(filtered_layoffs['date'], errors='coerce')
        trend = filtered_layoffs.groupby(filtered_layoffs['date'].dt.to_period("M"))['estimated_layoff'].sum().reset_index()
        trend['date'] = trend['date'].astype(str)
        st.line_chart(trend.rename(columns={'estimated_layoff': 'Layoffs'}).set_index('date'))
        st.dataframe(filtered_layoffs[['date', 'agency', 'estimated_layoff', 'locations impacted']], use_container_width=True)
    else:
        st.info("No layoff data available for this state.")

with tab3:
    st.subheader(f"📉 Federal Layoff Intelligence — {selected_state}")
    state_df = df[df['location_name'] == selected_state]

    top_jobs = state_df.groupby('occupation_title')['layoff_estimate'].sum().reset_index().sort_values(by='layoff_estimate', ascending=False).head(5)
    fig_jobs = px.bar(
        top_jobs,
        x='occupation_title',
        y='layoff_estimate',
        title="Top 5 Occupations by Estimated Layoffs",
        labels={'layoff_estimate': 'Estimated Layoffs'},
        height=400
    )
    st.plotly_chart(fig_jobs, use_container_width=True)

    top_skills = state_df.groupby('skill')['layoff_estimate'].sum().reset_index().sort_values(by='layoff_estimate', ascending=False).head(5)
    fig_skills = px.bar(
        top_skills,
        x='skill',
        y='layoff_estimate',
        title="Top 5 Skills by Estimated Layoffs",
        labels={'layoff_estimate': 'Estimated Layoffs'},
        height=400
    )
    st.plotly_chart(fig_skills, use_container_width=True)

    st.markdown("---")
    st.dataframe(state_df[['occupation_title', 'skill', 'employee_count_2024', 'layoff_estimate', 'ai_exposed']], use_container_width=True)
