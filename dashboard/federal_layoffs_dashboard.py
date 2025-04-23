# federal_layoffs_dashboard_visual_enhanced.py

import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt
import os

st.set_page_config(
    page_title='Federal Layoffs & Skills Intelligence',
    layout='wide',
    page_icon='dashboard/draup-logo.png'
)

# === Custom CSS Loader ===
def inject_custom_css(file_path="dashboard/streamlit_dashboard_custom_style.css"):
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Custom style file not found.")

inject_custom_css()

# === Load CSV with Safe Encoding ===
def safe_read_csv(path):
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin1")

@st.cache_data
def load_data():
    df = safe_read_csv("data/dashboard_ai_tagged_cleaned.csv")
    df_summary = safe_read_csv("data/dashboard_agency_state_summary.csv")
    df_signal = safe_read_csv("data/federal_layoff_signal.csv")
    df_sim = pd.read_csv("data/occupation_similarity_matrix.csv", index_col=0)
    return df, df_summary, df_signal, df_sim

required_files = [
    "data/dashboard_ai_tagged_cleaned.csv",
    "data/dashboard_agency_state_summary.csv",
    "data/federal_layoff_signal.csv",
    "data/occupation_similarity_matrix.csv"
]

missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    st.error(f"Missing required file(s): {', '.join(missing)}")
    st.stop()

df, df_summary, df_signal, df_sim = load_data()

# === Normalize Columns ===
for d in [df, df_summary, df_signal]:
    d.columns = d.columns.str.lower().str.strip().str.replace(" ", "_")
df_sim.columns = df_sim.columns.str.lower().str.strip()
df_sim.index = df_sim.index.str.lower().str.strip()
df['state'] = df['state'].str.strip().str.title()
df_signal['state'] = df_signal['state'].str.strip().str.title()
df_signal['date'] = pd.to_datetime(df_signal['date'], errors='coerce')
df_signal['estimated_layoff'] = pd.to_numeric(df_signal['estimated_layoff'].replace("Unspecified number", pd.NA), errors='coerce')

# === Sidebar ===
with st.sidebar:
    st.markdown("### Filter Options")
    selected_state = st.selectbox("Select a State", sorted(df['state'].unique()))

df_filtered = df[df['state'] == selected_state]

# === Header Polished ===
st.markdown("""
<style>
.header-strip {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #003366;
    padding: 0.3rem 1.2rem;
    border-radius: 10px;
    margin-bottom: 0.2rem;
    margin-top: 0.3rem;
    color: white;
    font-family: 'Inter', sans-serif;
    font-size: 1.4rem;
    font-weight: 600;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
    border: 3px solid #00264d;
}
.header-strip .logo {
    height: 46px;
}
.kpi-container {
    display: flex;
    justify-content: space-between;
    gap: 1.0rem;
    margin-top: 1.2rem;
    margin-bottom: 1.0rem;
}
.kpi-card {
    flex: 1;
    background: #f8fafc;
    border-left: 6px solid #cbd5e1;
    border-radius: 14px;
    padding: 1.2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
}
.kpi-icon {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #e2e8f0;
}
.kpi-text h4 {
    margin: 0;
    font-size: 1.4rem;
    font-weight: 700;
    color: #0f172a;
}
.kpi-text p {
    margin: 0;
    font-size: 0.9rem;
    color: #475569;
}
</style>
<div class='header-strip'>
    <span>Federal Layoffs & Skills Intelligence Dashboard</span>
    <img class='logo' src='https://draupmedia.s3.us-east-2.amazonaws.com/wp-content/uploads/2024/12/13112230/white-logo.svg' alt='Draup Logo'>
</div>
""", unsafe_allow_html=True)

# === KPI Display with Safe Fallback ===
total_workforce = df_filtered['talent_size'].sum() if 'talent_size' in df_filtered.columns else 0
estimated_layoffs = df_filtered['estimate_layoff'].sum() if 'estimate_layoff' in df_filtered.columns else 0
unique_skills = df_filtered['skill'].nunique() if 'skill' in df_filtered.columns else 0

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-icon">
            <img src="https://cdn-icons-png.flaticon.com/512/747/747376.png" style="width: 22px;">
        </div>
        <div class="kpi-text">
            <h4>{total_workforce:,}</h4>
            <p>Total Workforce</p>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">
            <img src="https://cdn-icons-png.flaticon.com/512/595/595067.png" style="width: 22px;">
        </div>
        <div class="kpi-text">
            <h4>{estimated_layoffs:,}</h4>
            <p>Estimated Layoffs</p>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">
            <img src="https://cdn-icons-png.flaticon.com/512/1055/1055687.png" style="width: 22px;">
        </div>
        <div class="kpi-text">
            <h4>{unique_skills:,}</h4>
            <p>Unique Skills</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# === Tabs Section ===
tab1, tab2, tab3 = st.tabs(["Layoff Intelligence", "Layoff Signals", "Alternative Career Paths"])

# === Tab 1: Layoff Intelligence ===
with tab1:
    st.markdown("""
    <div class='alt-container'>
    <h4 style="margin-bottom: 0.5rem;">Top Skills at Risk</h4>
    """, unsafe_allow_html=True)

    skill_top_n = st.radio("Select number of top skills", options=[5, 10], horizontal=True)
    top_skills = df_filtered.dropna(subset=['skill', 'estimate_layoff']) \
        .groupby("skill")["estimate_layoff"].sum().reset_index() \
        .sort_values("estimate_layoff", ascending=False).head(skill_top_n)
    top_skills['skill'] = top_skills['skill'].str.title()

    if not top_skills.empty:
        fig_skills = px.bar(top_skills, x="skill", y="estimate_layoff", 
                            title=f"Top {skill_top_n} Skills by Estimated Layoffs in {selected_state}",
                            color="estimate_layoff",
                            color_continuous_scale=px.colors.sequential.Teal)
        fig_skills.update_layout(xaxis_title="Skill", yaxis_title="Layoffs", title_font=dict(size=16))
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.warning("No skill data available for selected state.")

    st.markdown("""
    <h4 style="margin-top: 1.5rem;">Top Occupations at Risk</h4>
    """, unsafe_allow_html=True)

    job_top_n = st.radio("Select number of top occupations", options=[5, 10], horizontal=True)
    top_jobs = df_filtered.dropna(subset=['occupation', 'estimate_layoff']) \
        .groupby("occupation")["estimate_layoff"].sum().reset_index() \
        .sort_values("estimate_layoff", ascending=False).head(job_top_n)
    top_jobs['occupation'] = top_jobs['occupation'].str.title()

    if not top_jobs.empty:
        fig_jobs = px.bar(top_jobs, x="occupation", y="estimate_layoff",
                         title=f"Top {job_top_n} Occupations by Estimated Layoffs in {selected_state}",
                         color="estimate_layoff",
                         color_continuous_scale=px.colors.sequential.Blues)
        fig_jobs.update_layout(xaxis_title="Occupation", yaxis_title="Layoffs", title_font=dict(size=16))
        st.plotly_chart(fig_jobs, use_container_width=True)
    else:
        st.warning("No occupation data available for selected state.")

    st.markdown("</div>", unsafe_allow_html=True)

# === Tab 2: Layoff Signals ===
with tab2:
  with tab2:
    st.markdown("""
    <style>
    .layoff-header {{
        font-size: 1.3rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        color: #0f172a;
        margin-bottom: 1rem;
    }}
    .layoff-articles-title {{
        font-size: 1.1rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        color: #334155;
        margin-top: 2rem;
    }}
    </style>
    <div class='layoff-header'>Layoff News & Timeline in {}</div>
    """.format(selected_state), unsafe_allow_html=True)

    df_signal_filtered = df_signal[df_signal['state'].str.contains(selected_state, case=False, na=False)]

    if df_signal_filtered.empty:
        st.info("No layoff news found for the selected state.")
    else:
        chart = alt.Chart(df_signal_filtered.dropna(subset=['date'])).mark_bar().encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('estimated_layoff:Q', title='Estimated Layoffs'),
            color=alt.Color('agency_name:N', title='Agency'),
            tooltip=[
                alt.Tooltip('date:T', title="Date"),
                alt.Tooltip('agency_name:N', title="Agency"),
                alt.Tooltip('estimated_layoff:Q', title="Layoffs"),
                alt.Tooltip('article_title:N', title="Article")
            ]
        ).properties(title="Layoff Events Timeline")
        st.altair_chart(chart, use_container_width=True)

        st.markdown("""
        <div class='layoff-articles-title'>Layoff News Articles</div>
        """, unsafe_allow_html=True)

        for _, row in df_signal_filtered.iterrows():
            article_date = row['date'].strftime('%b %d, %Y') if pd.notna(row['date']) else "Unknown Date"
            layoffs = f"{int(row['estimated_layoff']):,}" if pd.notna(row['estimated_layoff']) else "Unspecified"
            with st.expander(f"{article_date} — {row['agency_name']}"):
                st.markdown(f"**Title:** {row['article_title']}")
                st.markdown(f"**Estimated Layoffs:** {layoffs}")
                st.markdown(f"[Read Article]({row['source_link']})")
