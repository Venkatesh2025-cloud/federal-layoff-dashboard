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
st.sidebar.header("\ud83c\udf1f Filters")
st.sidebar.radio("View Mode", ["National", "City"], index=0)

all_departments = sorted(df['agency_name'].dropna().unique())
selected_agency = st.sidebar.selectbox("Filter by Agency (optional)", ["All"] + all_departments)

# === KPI ROW ===
st.markdown("""
<div style="display: flex; justify-content: space-between; padding: 10px 0 20px 0;">
    <div style="text-align: center; flex: 1;">
        <h3 style="color: #3366cc;">\ud83c\udf93 Skill Categories</h3>
        <h1 style="color: #111;">{}</h1>
    </div>
    <div style="text-align: center; flex: 1;">
        <h3 style="color: #3366cc;">\ud83d\udc65 Available Talent</h3>
        <h1 style="color: #111;">{:,}</h1>
    </div>
    <div style="text-align: center; flex: 1;">
        <h3 style="color: #3366cc;">\ud83c\udfc6 Most Available Skill</h3>
        <h1 style="color: #111;">{}</h1>
    </div>
</div>
""".format(
    df['skill'].nunique(),
    df['employee_count_2024'].sum(),
    df.groupby('skill')['employee_count_2024'].sum().idxmax()
), unsafe_allow_html=True)

# === TABS ===
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Talent Availability",
    "Demand vs Supply",
    "Layoff News",
    "Federal Agency Staff",
    "Decision Intelligence"
])

with tab1:
    st.subheader("\ud83d\udcca Talent Availability by Skill \u2014 US National View")
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
    st.info("Demand vs Supply feature not implemented yet. Coming soon!")

with tab3:
    st.info("Layoff news visualization will be added in future enhancements.")

with tab4:
    st.info("Federal agency staffing summary will be integrated here.")

with tab5:
    st.info("Decision intelligence recommendations under development.")
