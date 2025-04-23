import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- SETUP ----------
st.set_page_config("Layoffs & Skills Intelligence", layout="wide")

# ---------- PLACEHOLDER DATA FOR DEMO ----------
skills_df = pd.DataFrame({
    "skill": ["Data Analysis", "Nursing", "Project Management", "SQL", "AI Ethics"],
    "estimate_layoff": [1200, 950, 875, 800, 760],
    "color": ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#d62728"]
})

occupations_df = pd.DataFrame({
    "occupation": ["Data Scientist", "Nurse", "Project Manager", "SQL Developer", "Ethics Officer"],
    "estimate_layoff": [2200, 1700, 1500, 1100, 890]
})

layoff_df = pd.DataFrame({
    "date": pd.date_range(start="2025-01-01", periods=6, freq="M"),
    "layoffs": [1000, 1400, 900, 1300, 1700, 1200]
})

similar_df = pd.DataFrame({
    "occupation": ["Data Engineer", "ML Engineer", "Statistician", "BI Analyst", "AI Researcher"],
    "similarity": [0.91, 0.89, 0.85, 0.83, 0.81]
})

# ---------- HEADER ----------
st.markdown("""
    <h1 style='text-align: center; background-color:#003366; color:white; padding:0.75rem; border-radius:8px;'>
        Federal Layoffs & Skills Intelligence
    </h1>
""", unsafe_allow_html=True)

# ---------- FILTERS ----------
st.sidebar.header("📍 Filters")
state = st.sidebar.selectbox("Select State", ["Texas", "California", "New York"])
agency = st.sidebar.selectbox("Select Agency", ["All", "Veterans Health", "Social Security", "Dept. of Treasury"])

# ---------- SECTION 1: TOP SKILLS AT RISK ----------
st.subheader("🧠 Top 5 Skills at Risk (Prioritized View)")
fig_skills = px.bar(skills_df, x="skill", y="estimate_layoff", color="color", title="Top Skills by Estimated Layoffs",
                    color_discrete_map="identity", labels={"estimate_layoff": "Est. Layoffs"})
fig_skills.update_layout(showlegend=False)
st.plotly_chart(fig_skills, use_container_width=True)

# ---------- SECTION 2: TOP OCCUPATIONS AT RISK ----------
st.subheader("💼 Top 5 Occupations by Estimated Layoffs")
fig_jobs = px.bar(occupations_df, x="occupation", y="estimate_layoff", title="Top Occupations at Risk",
                  color_discrete_sequence=px.colors.sequential.Blues_r)
st.plotly_chart(fig_jobs, use_container_width=True)

# ---------- SECTION 3: LAYOFF TREND EXPLORATION ----------
st.subheader("📉 Federal Layoff Trends Over Time")
st.markdown("Use this section to explore layoff timelines across states and agencies.")
fig_line = px.line(layoff_df, x="date", y="layoffs", markers=True, title="Estimated Layoffs by Month")
st.plotly_chart(fig_line, use_container_width=True)

# ---------- SECTION 4: SIMILAR OCCUPATIONS (Optional) ----------
with st.expander("🔁 Show Similar Occupations (Optional)"):
    st.markdown("*Use this view to identify roles with skill overlap or redeployment potential.*")
    fig_sim = px.bar(similar_df, x="occupation", y="similarity", title="Top Similar Occupations",
                     color="similarity", color_continuous_scale="blues")
    st.plotly_chart(fig_sim, use_container_width=True)

# ---------- FOOTER ----------
st.markdown("---")
st.caption("Dashboard structure inspired by Vijay’s feedback • Built with ❤️ for human clarity.")
