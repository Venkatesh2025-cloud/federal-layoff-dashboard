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
st.sidebar.radio("View Mode", ["National", "City"], index=0)

all_departments = sorted(df['agency_name'].dropna().unique())
selected_agency = st.sidebar.selectbox("Filter by Agency (optional)", ["All"] + all_departments)

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
tab1, tab2, tab3, tab4 = st.tabs([
    "Talent Availability",
    "Layoff News",
    "Federal Agency Staff",
    "Decision Intelligence"
])

with tab1:
    st.subheader("📊 Talent Availability by Skill — US National View")
    skill_view = df.copy()
    if selected_agency != "All":
        skill_view = df[df['agency_name'] == selected_agency]

    skill_summary = skill_view.groupby('skill').agg({
        'employee_count_2024': 'sum'
    }).reset_index().sort_values(by='employee_count_2024', ascending=False)

    fig = px.bar(
        skill_summary,
        x='skill',
        y='employee_count_2024',
        color='employee_count_2024',
        title="Available Talent by Skill Category",
        labels={'employee_count_2024': 'Available Talent'},
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(skill_summary.rename(columns={"skill": "Skill Category", "employee_count_2024": "Available Talent"}), use_container_width=True)

with tab2:
    st.subheader("📰 Layoff News Over Time")
    if 'date' in layoff_signals.columns:
        layoff_signals['date'] = pd.to_datetime(layoff_signals['date'], errors='coerce')
        trend = layoff_signals.groupby(layoff_signals['date'].dt.to_period("M"))['estimated_layoff'].sum().reset_index()
        trend['date'] = trend['date'].astype(str)
        st.line_chart(trend.rename(columns={'estimated_layoff': 'Layoffs'}).set_index('date'))
        st.dataframe(layoff_signals[['date', 'agency', 'estimated_layoff', 'locations impacted']], use_container_width=True)
    else:
        st.warning("Date column missing in layoff signal file.")

with tab3:
    st.subheader("🏢 Federal Agency Workforce Summary")
    if 'agency_name' in summary.columns:
        agency_summary = summary.groupby(['agency_name', 'state']).agg({
            'employee_count_2024': 'sum',
            'layoff_estimate': 'sum'
        }).reset_index()
        fig_summary = px.bar(
            agency_summary,
            x='agency_name',
            y='employee_count_2024',
            color='layoff_estimate',
            title="Federal Agency Workforce Overview",
            labels={'employee_count_2024': 'Employees', 'layoff_estimate': 'Estimated Layoffs'},
            height=450
        )
        st.plotly_chart(fig_summary, use_container_width=True)
        st.dataframe(agency_summary, use_container_width=True)
    else:
        st.warning("Summary dataset missing expected columns.")

with tab4:
    st.subheader("✅ Decision Intelligence — Summary")
    decision_summary = df.groupby('skill').agg({
        'employee_count_2024': 'sum',
        'layoff_estimate': 'sum',
        'ai_exposed': 'sum'
    }).reset_index().sort_values(by='layoff_estimate', ascending=False).head(10)

    st.markdown("These skills show the highest potential disruption and are flagged for upskilling or redeployment.")
    fig_decision = px.bar(
        decision_summary,
        x='skill',
        y='layoff_estimate',
        color='ai_exposed',
        title="Top 10 At-Risk Skills by Layoff Estimate",
        labels={'layoff_estimate': 'Estimated Layoffs', 'ai_exposed': 'AI Exposure'},
        height=450
    )
    st.plotly_chart(fig_decision, use_container_width=True)
    st.dataframe(decision_summary.rename(columns={
        "skill": "Skill Category",
        "employee_count_2024": "Available Talent",
        "layoff_estimate": "Estimated Layoffs",
        "ai_exposed": "AI-Exposed"
    }), use_container_width=True)
