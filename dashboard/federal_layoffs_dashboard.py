
# federal_layoffs_dashboard_final.py

import pandas as pd
import streamlit as st
import plotly.express as px
import os
import altair as alt

st.set_page_config(page_title="Federal Layoffs Dashboard", layout="wide")

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
    return df, df_summary, df_signal

required_files = [
    "data/dashboard_ai_tagged_cleaned.csv",
    "data/dashboard_agency_state_summary.csv",
    "data/federal_layoff_signal.csv"
]

missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    st.error(f"Missing required file(s): {', '.join(missing)}")
    st.stop()

with st.spinner("Loading datasets..."):
    try:
        df, df_summary, df_signal = load_data()
    except Exception as e:
        st.error(f"Failed to load datasets: {e}")
        st.stop()

# Cleanup
df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
df_summary.columns = df_summary.columns.str.lower().str.strip().str.replace(" ", "_")
df_signal.columns = df_signal.columns.str.lower().str.strip().str.replace(" ", "_")

df['state'] = df['state'].str.title().str.strip()
df_summary['state'] = df_summary['state'].str.title().str.strip()
df_signal['state'] = df_signal['state'].str.title().str.strip()
df_signal['date'] = pd.to_datetime(df_signal['date'], errors='coerce')
df_signal['estimated_layoff'] = pd.to_numeric(df_signal['estimated_layoff'].replace("Unspecified number", pd.NA), errors='coerce')

# === Sidebar ===
st.sidebar.header("📍 Filter by State")
state_list = sorted(df['state'].unique())
selected_state = st.sidebar.selectbox("State", state_list)

# === KPI Metrics from Summary Table ===
summary_filtered = df_summary[df_summary["state"] == selected_state]
est_layoffs = summary_filtered["estimated_layoff"].sum()
total_workforce = summary_filtered["talent_size"].sum()

header_html = (
    "<h1 style='text-align: center; background-color: #003366; color: white; "
    "padding: 1rem; border-radius: 8px;'>Federal Layoffs & Skills Intelligence Dashboard</h1>"
)
st.markdown(header_html, unsafe_allow_html=True)

kpi_html = f'''
<div style="display: flex; justify-content: space-around; font-family: 'Inter', sans-serif; margin-top: 1rem;">
    <div style="background: #ffedd5; border-radius: 12px; padding: 1rem; text-align: center; width: 40%;">
        <div style="font-size: 1.7rem; font-weight: 600; color: #b45309;">{est_layoffs:,}</div>
        <div style="color: #444; font-size: 0.95rem;">Estimated Layoffs in {selected_state}</div>
    </div>
    <div style="background: #e0f2fe; border-radius: 12px; padding: 1rem; text-align: center; width: 40%;">
        <div style="font-size: 1.7rem; font-weight: 600; color: #0369a1;">{total_workforce:,}</div>
        <div style="color: #444; font-size: 0.95rem;">Total Federal Workforce in {selected_state}</div>
    </div>
</div>
'''
st.markdown(kpi_html, unsafe_allow_html=True)

# === Tabs: Ordered per CEO feedback ===
tab1, tab2, tab3 = st.tabs([
    "🏢 Federal Agency Staff",
    "📰 Layoff News",
    "📊 Federal Layoff Intelligence"
])

with tab1:
    st.subheader(f"Federal Workforce Overview - {selected_state}")
    df_agency = df_summary[df_summary["state"] == selected_state].sort_values("talent_size", ascending=False).head(10)
    if not df_agency.empty:
        fig_agency = px.bar(df_agency, x="agency_name", y="talent_size",
                            title="Top Federal Agencies by Workforce",
                            color="talent_size",
                            color_continuous_scale=px.colors.sequential.Blues)
        st.plotly_chart(fig_agency, use_container_width=True)
    else:
        st.info("No workforce data available for this state.")

with tab2:
    st.subheader(f"Layoff News in {selected_state}")
    news_filtered = df_signal[df_signal['state'] == selected_state]
    if news_filtered.empty:
        st.info("No layoff news found for the selected state.")
    else:
        chart = alt.Chart(news_filtered.dropna(subset=['date'])).mark_bar().encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('estimated_layoff:Q', title='Estimated Layoffs'),
            color=alt.Color('agency_name:N', title='Agency'),
            tooltip=['date', 'agency_name', 'estimated_layoff', 'article_title']
        ).properties(title="Layoff Events Timeline")
        st.altair_chart(chart, use_container_width=True)

        for _, row in news_filtered.iterrows():
            with st.expander(f"{row['date'].strftime('%b %d, %Y')} — {row['agency_name']}"):
                st.markdown(f"**Title**: {row['article_title']}")
                st.markdown(f"**Estimated Layoffs**: {int(row['estimated_layoff']) if pd.notna(row['estimated_layoff']) else 'Unspecified'}")
                st.markdown(f"[🔗 Source]({row['source_link']})")

with tab3:
    st.subheader(f"Top 5 Occupations and Skills by Estimated Layoffs - {selected_state}")
    df_filtered = df[df["state"] == selected_state]
    top_jobs = df_filtered.groupby("occupation")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(5)
    top_skills = df_filtered.groupby("skill")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(5)

    if not top_jobs.empty:
        fig_jobs = px.bar(top_jobs, x="occupation", y="estimate_layoff", color="estimate_layoff",
                          title="Top 5 Occupations by Estimated Layoffs",
                          color_continuous_scale=px.colors.sequential.Reds)
        st.plotly_chart(fig_jobs, use_container_width=True)

    if not top_skills.empty:
        fig_skills = px.bar(top_skills, x="skill", y="estimate_layoff", color="estimate_layoff",
                            title="Top 5 Skills by Estimated Layoffs",
                            color_continuous_scale=px.colors.sequential.Tealgrn)
        st.plotly_chart(fig_skills, use_container_width=True)

# === Footer ===
st.markdown("---")
st.caption("Built with ❤️ by your data + design team. Data source: Draup")
