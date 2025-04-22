import streamlit as st
import pandas as pd
import plotly.express as px

# --- Simulated clean dataset ---
df = pd.DataFrame({
    "location_name": ["Texas"] * 8,
    "occupation_title": ["Nurse", "Nurse", "Nurse", "Data Analyst", "Data Analyst", "Data Analyst", "Cybersecurity Analyst", "Cybersecurity Analyst"],
    "skill": ["Patient Monitoring", "Medication Safety", "Record Keeping", "SQL", "Python", "PowerBI", "Network Defense", "SIEM Monitoring"],
    "employee_count_2024": [3000, 3000, 3000, 2000, 2000, 2000, 1800, 1800],
    "layoff_estimate": [700, 500, 300, 300, 200, 180, 150, 120]
})

# === PAGE CONFIG ===
st.set_page_config(page_title="Vijay's Federal Layoff Intelligence", layout="wide")

# === HEADER ===
st.markdown("""
    <h1 style='text-align: center; color: white; background-color: #003366; padding: 25px; border-radius: 8px'>
    🧠 Federal Skill Risk Dashboard — Decision Intelligence View
    </h1>
""", unsafe_allow_html=True)

# === STATE FILTER (Only one filter!) ===
selected_state = st.selectbox("📍 Select a State", sorted(df['location_name'].unique()))

filtered = df[df['location_name'] == selected_state]

# === KPIs ===
st.markdown("### 🔢 Quick Snapshot")
k1, k2, k3 = st.columns(3)
k1.metric("🧑‍💼 Total Employees", f"{filtered['employee_count_2024'].sum():,}")
k2.metric("⚠️ Estimated Layoffs", f"{filtered['layoff_estimate'].sum():,}")
top_skill = filtered.groupby("skill")["layoff_estimate"].sum().idxmax()
k3.metric("🏆 Most At-Risk Skill", top_skill)

# === Main Section ===
st.markdown("---")
st.subheader("📉 Federal Layoff Intelligence — Skill Drilldown by Occupation")

top_jobs = (
    filtered.groupby("occupation_title")["layoff_estimate"]
    .sum()
    .reset_index()
    .sort_values(by="layoff_estimate", ascending=False)
    .head(5)
)

for _, row in top_jobs.iterrows():
    job = row["occupation_title"]
    est = row["layoff_estimate"]
    subset = filtered[filtered["occupation_title"] == job]

    with st.expander(f"💼 {job} — Total Layoffs Estimated: {est}"):
        fig = px.bar(subset, x="skill", y="layoff_estimate", color="layoff_estimate",
                     title=f"Skills at Risk for {job}", height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(subset[["skill", "employee_count_2024", "layoff_estimate"]], use_container_width=True)

# Optional footer
st.markdown("---")
st.caption("Designed with 🧠 by a Data Product Designer for Decision Makers.")
