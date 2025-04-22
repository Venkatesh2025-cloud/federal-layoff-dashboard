import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Federal Layoff Intelligence Dashboard", layout="wide")

# === LOAD DATA ===
df = pd.read_csv("data/dashboard_ai_tagged.csv.gz", compression='gzip')
summary = pd.read_csv("data/dashboard_agency_state_summary.csv")
signal = pd.read_csv("data/federal_layoff_signal.csv", encoding='latin1')
dept_map = pd.read_csv("data/agency_department_map.csv", encoding='latin1')

# === DATA CLEANING ===
def clean_columns(df):
    return df.rename(columns=lambda col: col.strip().lower().replace(" ", "_"))

df = clean_columns(df)
summary = clean_columns(summary)
signal = clean_columns(signal)
dept_map = clean_columns(dept_map)
dept_map = dept_map.rename(columns={'agency_sub_name': 'agency_name'})

# === MERGE DEPARTMENT INFO ===
if 'agency_name' in dept_map.columns and 'department' in dept_map.columns:
    df = df.merge(dept_map[['agency_name', 'department']], on='agency_name', how='left')

# === FILTERS ===
st.sidebar.header("🌟 Filters")
selected_state = st.sidebar.selectbox("Select a State", sorted(df['location_name'].dropna().unique()))

agency_options = sorted(df[df['location_name'] == selected_state]['agency_name'].dropna().unique())
selected_agency = st.sidebar.selectbox("Filter by Agency Name", ["All"] + agency_options)

if 'department' in df.columns:
    dept_options = sorted(df[df['location_name'] == selected_state]['department'].dropna().unique())
    selected_dept = st.sidebar.selectbox("Filter by Department", ["All"] + dept_options)
else:
    selected_dept = "All"

# Apply filters
df_filtered = df[df['location_name'] == selected_state]
if selected_agency != "All":
    df_filtered = df_filtered[df_filtered['agency_name'] == selected_agency]
if selected_dept != "All":
    df_filtered = df_filtered[df_filtered['department'] == selected_dept]

# === KPI ===
st.markdown("""
    <h1 style='text-align: center; color: white; background-color: #003366; padding: 25px; border-radius: 8px'>📊 Federal Layoff Intelligence Dashboard</h1>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Skill Categories", df_filtered['skill'].nunique())
col2.metric("Available Talent", f"{df_filtered['employee_count_2024'].sum():,}")
col3.metric("Most Available Skill", df_filtered.groupby('skill')['employee_count_2024'].sum().idxmax())

# === TABS ===
tab1, tab2, tab3 = st.tabs(["Federal Agency Staff", "Layoff News", "Federal Layoff Intelligence"])

with tab1:
    st.subheader(f"🏢 Federal Agency Workforce Summary – {selected_state}")
    col = 'location_name' if 'location_name' in summary.columns else 'state'
    if col in summary.columns:
        filtered = summary[summary[col] == selected_state]
        agency_col = None
        for name in ['agency_name', 'agency name', 'agency']:
            if name in filtered.columns:
                agency_col = name
                break

        if agency_col:
            grouped = filtered.groupby(agency_col).agg({
                'employee_count_2024': 'sum',
                'layoff_estimate': 'sum'
            }).reset_index().sort_values(by='employee_count_2024', ascending=False).head(10)

            fig = px.bar(grouped, x=agency_col, y='employee_count_2024', color='layoff_estimate',
                         labels={'employee_count_2024': 'Employees', 'layoff_estimate': 'Layoff Estimate'},
                         title=f"Top 10 Agencies in {selected_state}", height=450)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(grouped, use_container_width=True)
        else:
            st.warning("Missing agency column in summary data.")
    else:
        st.warning("Could not find a valid state/location column in the summary data.")

with tab2:
    st.subheader(f"📰 Layoff News – {selected_state}")
    if 'locations_impacted' in signal.columns:
        layoffs = signal[signal['locations_impacted'].str.contains(selected_state, case=False, na=False)]
        if not layoffs.empty:
            if 'date' in layoffs.columns:
                layoffs['date'] = pd.to_datetime(layoffs['date'], errors='coerce')
                if 'estimated_layoff' in layoffs.columns:
                    trend = layoffs.groupby(layoffs['date'].dt.to_period("M"))['estimated_layoff'].sum().reset_index()
                    trend['date'] = trend['date'].astype(str)
                    st.line_chart(trend.rename(columns={'estimated_layoff': 'Layoffs'}).set_index('date'))
            st.dataframe(layoffs[['date', 'agency_name', 'estimated_layoff', 'locations_impacted']], use_container_width=True)
        else:
            st.info("No layoff news for this state.")
    else:
        st.warning("Missing 'locations impacted' column in layoff signal data.")

with tab3:
    st.subheader(f"📉 Federal Layoff Intelligence – {selected_state}")

    top_jobs = df_filtered.groupby('occupation_title')['layoff_estimate'].sum().reset_index()
    top_jobs = top_jobs.sort_values(by='layoff_estimate', ascending=False).head(5)
    job_fig = px.bar(top_jobs, x='occupation_title', y='layoff_estimate',
                    title="Top 5 Occupations by Estimated Layoffs", height=400)
    st.plotly_chart(job_fig, use_container_width=True)

    top_skills = df_filtered.groupby('skill')['layoff_estimate'].sum().reset_index()
    top_skills = top_skills.sort_values(by='layoff_estimate', ascending=False).head(5)
    skill_fig = px.bar(top_skills, x='skill', y='layoff_estimate',
                      title="Top 5 Skills by Estimated Layoffs", height=400)
    st.plotly_chart(skill_fig, use_container_width=True)

    st.dataframe(df_filtered[['occupation_title', 'skill', 'employee_count_2024', 'layoff_estimate']], use_container_width=True)
