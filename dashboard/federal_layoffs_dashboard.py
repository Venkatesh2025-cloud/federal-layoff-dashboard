import streamlit as st
import pandas as pd
import altair as alt

# Placeholder data (replace with real dataset)
states = ['Texas', 'California', 'Florida', 'New York', 'Arkansas']
selected_state = st.sidebar.selectbox("Select State", states)

# Dummy Data for Selected State (to be replaced by real filtered data)
estimated_layoffs = 15432  # Example number
top_jobs_data = pd.DataFrame({
    'Occupation': ['Nurse', 'Software Engineer', 'Teacher', 'Data Analyst', 'HR Specialist'],
    'Estimated Layoffs': [3000, 2500, 1800, 1200, 800]
})
top_skills_data = pd.DataFrame({
    'Skill': ['Python', 'Data Analysis', 'Communication', 'SQL', 'Project Management'],
    'Frequency': [2200, 2000, 1800, 1700, 1600]
})

# ---------------- HEADER -----------------
st.title("Federal Layoff Intelligence")
st.caption(f"Overview of impacted occupations and skill clusters in {selected_state}")

# ---------------- METRIC -----------------
st.metric("Estimated Layoffs", f"{estimated_layoffs:,}")

# ---------------- LAYOUT -----------------
tab1, tab2 = st.tabs(["Federal Layoff Intelligence", "Layoff News"])

# ---------------- TAB 1: Layoff Intelligence -----------------
with tab1:
    st.subheader(f"Top 5 Occupations Affected by Layoffs in {selected_state}")
    chart_jobs = alt.Chart(top_jobs_data).mark_bar().encode(
        x=alt.X('Estimated Layoffs:Q', title='Layoffs'),
        y=alt.Y('Occupation:N', sort='-x'),
        tooltip=['Occupation', 'Estimated Layoffs']
    ).properties(height=300)
    st.altair_chart(chart_jobs, use_container_width=True)

    st.subheader("Top 5 Skills in Affected Occupations")
    chart_skills = alt.Chart(top_skills_data).mark_bar().encode(
        x=alt.X('Frequency:Q', title='Mentions in Job Data'),
        y=alt.Y('Skill:N', sort='-x'),
        tooltip=['Skill', 'Frequency']
    ).properties(height=300)
    st.altair_chart(chart_skills, use_container_width=True)

# ---------------- TAB 2: Layoff News -----------------
with tab2:
    st.subheader(f"Recent Layoff News in {selected_state}")
    layoff_news = pd.DataFrame({
        'Company': ['HealthCorp', 'FinTechX', 'EduSpark'],
        'Sector': ['Healthcare', 'Finance', 'Education'],
        'Impact': ['2,500', '1,800', '1,200'],
        'Date': ['2025-04-01', '2025-03-15', '2025-03-10']
    })
    st.dataframe(layoff_news)

# ---------------- FOOTER -----------------
st.markdown("---")
st.caption("Powered by Draup • Last updated automatically • Prototype View")
