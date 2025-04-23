
# federal_layoffs_dashboard_final_safe.py

import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt
import os

st.set_page_config(page_title="Federal Layoffs & Skills Dashboard", layout="wide")

# === Safe CSV Loader with Encoding Fallback ===
@st.cache_data
def load_data():
    def safe_read_csv(path):
        try:
            return pd.read_csv(path, encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(path, encoding="latin1")

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

# Normalize columns
for d in [df, df_summary, df_signal]:
    d.columns = d.columns.str.lower().str.strip().str.replace(" ", "_")

df_sim.columns = df_sim.columns.str.lower().str.strip()
df_sim.index = df_sim.index.str.lower().str.strip()

df['state'] = df['state'].str.title().str.strip()
df_signal['state'] = df_signal['state'].str.title().str.strip()
df_signal['date'] = pd.to_datetime(df_signal['date'], errors='coerce')
df_signal['estimated_layoff'] = pd.to_numeric(df_signal['estimated_layoff'].replace("Unspecified number", pd.NA), errors='coerce')

# Sidebar
st.sidebar.header("📍 Filter by State")
state_list = sorted(df['state'].unique())
selected_state = st.sidebar.selectbox("State", state_list)
df_filtered = df[df['state'] == selected_state]

# Header
st.markdown("""
<h1 style='text-align: center; background-color: #003366; color: white; padding: 1rem; border-radius: 8px;'>
Federal Layoffs & Skills Intelligence Dashboard
</h1>
""", unsafe_allow_html=True)

# KPI Metrics
total_workforce = df_filtered['talent_size'].sum()
total_layoffs = df_filtered['estimate_layoff'].sum()
unique_skills = df_filtered['skill'].nunique()
layoff_rate = (total_layoffs / total_workforce) * 100 if total_workforce > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Total Workforce", f"{total_workforce:,}")
col2.metric("⚠️ Estimated Layoffs", f"{total_layoffs:,}")
col3.metric("📌 Unique Skills", f"{unique_skills:,}")
col4.metric("📉 Layoff Rate", f"{layoff_rate:.1f}%")

# Tabs
tab1, tab2, tab3 = st.tabs([
    "📊 Top Jobs & Skills",
    "📰 News & Timeline",
    "🔍 Similar Occupations"
])

with tab1:
    st.subheader("Top 5 Occupations by Estimated Layoffs")
    top_jobs = df_filtered.groupby("occupation")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(5)
    fig_jobs = px.bar(top_jobs, x="occupation", y="estimate_layoff", color="estimate_layoff",
                      title="Occupations Most at Risk",
                      color_continuous_scale=px.colors.sequential.Reds)
    st.plotly_chart(fig_jobs, use_container_width=True)

    st.subheader("🔍 Select a Job to Explore Top Skills")
    selected_job = st.selectbox("Choose an Occupation", df_filtered["occupation"].unique())
    job_skills = df_filtered[df_filtered["occupation"] == selected_job]
    top_skills = job_skills.groupby("skill")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(5)
    fig_skills = px.bar(top_skills, x="skill", y="estimate_layoff", color="estimate_layoff",
                        title=f"Top Skills in {selected_job}",
                        color_continuous_scale=px.colors.sequential.Teal)
    st.plotly_chart(fig_skills, use_container_width=True)

    st.download_button("📥 Download Filtered Data (CSV)", data=df_filtered.to_csv(index=False),
                       file_name=f"{selected_state}_layoffs_data.csv", mime="text/csv")

with tab2:
    st.subheader("Layoff Events Timeline")
    df_signal_filtered = df_signal[df_signal['state'] == selected_state]
    if df_signal_filtered.empty:
        st.info("No layoff news found for the selected state.")
    else:
        chart = alt.Chart(df_signal_filtered.dropna(subset=['date'])).mark_bar().encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('estimated_layoff:Q', title='Estimated Layoffs'),
            color=alt.Color('agency_name:N', title='Agency'),
            tooltip=['date', 'agency_name', 'estimated_layoff', 'article_title']
        ).properties(title="Federal Layoffs Over Time")
        st.altair_chart(chart, use_container_width=True)

        for _, row in df_signal_filtered.iterrows():
            with st.expander(f"{row['date'].strftime('%b %d, %Y')} — {row['agency_name']}"):
                st.markdown(f"**Title**: {row['article_title']}")
                st.markdown(f"**Estimated Layoffs**: {int(row['estimated_layoff']) if pd.notna(row['estimated_layoff']) else 'Unspecified'}")
                st.markdown(f"[🔗 Source]({row['source_link']})")

with tab3:
    st.subheader("Explore Similar Occupations (Optional)")
    selected_occ = st.selectbox("Choose an occupation", sorted(df['occupation'].unique()), key="similar_occ")
    selected_key = selected_occ.lower().strip()
    if selected_key in df_sim.index:
        similar_df = df_sim.loc[selected_key].sort_values(ascending=False).head(10).reset_index()
        similar_df.columns = ['occupation', 'similarity']
        fig_sim = px.bar(similar_df, x='occupation', y='similarity',
                         title=f"Most Similar to {selected_occ}",
                         color='similarity',
                         color_continuous_scale=px.colors.sequential.Oranges)
        st.plotly_chart(fig_sim, use_container_width=True)
    else:
        st.info("Similarity data not available for this occupation.")

# Footer
st.markdown("---")
st.caption("Built with ❤️ by your data + design team. Data source: Draup")
