
# federal_layoffs_dashboard_visual_enhanced.py

import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt
import os

st.set_page_config(

with open("streamlit_dashboard_custom_style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

page_title="🧠 Federal Layoffs & Skills Intelligence", layout="wide")

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
    st.markdown("### 🔎 Filter Options")
    selected_state = st.selectbox("📍 Select a State", sorted(df['state'].unique()))

df_filtered = df[df['state'] == selected_state]

# === Header ===
st.markdown("""
<style>
    .main-title {
        font-family: 'Segoe UI', sans-serif;
        background-color: #003366;
        padding: 1rem;
        color: white;
        border-radius: 8px;
        text-align: center;
        font-size: 1.8rem;
        margin-bottom: 1.5rem;
    }
</style>
<div class='main-title'>
    🧠 Federal Layoffs & Skills Intelligence Dashboard
</div>
""", unsafe_allow_html=True)

# === KPIs using st.columns ===
col1, col2, col3 = st.columns(3)
col1.metric("👥 Total Workforce", f"{df_filtered['talent_size'].sum():,}")
col2.metric("⚠️ Estimated Layoffs", f"{df_filtered['estimate_layoff'].sum():,}")
col3.metric("🎯 Unique Skills", f"{df_filtered['skill'].nunique():,}")

# === Tabs Layout ===
tab1, tab2, tab3 = st.tabs(["📊 Top Skills & Jobs", "📰 Layoff News", "🔍 Similar Occupations"])

with tab1:
    st.subheader(f"🔥 Top 10 Skills at Risk in {selected_state}")
    top_skills = df_filtered.groupby("skill")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(10)
    fig_skills = px.bar(top_skills, x="skill", y="estimate_layoff",
                        color="estimate_layoff", text_auto=True,
                        title=f"Top Skills by Estimated Layoffs in {selected_state}",
                        color_continuous_scale=px.colors.sequential.Teal)
    fig_skills.update_layout(xaxis_title="", yaxis_title="Layoffs")
    st.plotly_chart(fig_skills, use_container_width=True)

    st.subheader("💼 Top 10 Occupations by Estimated Layoffs")
    top_jobs = df_filtered.groupby("occupation")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(10)
    fig_jobs = px.bar(top_jobs, x="occupation", y="estimate_layoff",
                      color="estimate_layoff", text_auto=True,
                      title="Top Occupations by Estimated Layoffs",
                      color_continuous_scale=px.colors.sequential.Blues)
    fig_jobs.update_layout(xaxis_title="", yaxis_title="Layoffs")
    st.plotly_chart(fig_jobs, use_container_width=True)

with tab2:
    st.subheader(f"🗞️ Layoff News and Events in {selected_state}")
    df_signal_filtered = df_signal[df_signal['state'].str.contains(selected_state, na=False)]
    if df_signal_filtered.empty:
        st.info("No layoff news found for the selected state.")
    else:
        chart = alt.Chart(df_signal_filtered.dropna(subset=['date'])).mark_bar().encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('estimated_layoff:Q', title='Estimated Layoffs'),
            color=alt.Color('agency_name:N', title='Agency'),
            tooltip=['date', 'agency_name', 'estimated_layoff', 'article_title']
        ).properties(title="Layoff Events Timeline")
        st.altair_chart(chart, use_container_width=True)

        st.markdown("### 📰 Layoff News Articles")
        for _, row in df_signal_filtered.iterrows():
            with st.expander(f"{row['date'].strftime('%b %d, %Y')} — {row['agency_name']}"):
                st.markdown(f"**📝 Title**: {row['article_title']}")
                st.markdown(f"**🔢 Estimated Layoffs**: {int(row['estimated_layoff']) if pd.notna(row['estimated_layoff']) else 'Unspecified'}")
                st.markdown(f"[🔗 Source]({row['source_link']})")

with tab3:
    st.subheader("🧬 Similar Occupation Explorer")
    selected_occ = st.selectbox("🔄 Choose an occupation", sorted(df['occupation'].unique()), key="similar_occ")
    selected_key = selected_occ.lower().strip()
    if selected_key in df_sim.index:
        similar_df = df_sim.loc[selected_key].sort_values(ascending=False).head(10).reset_index()
        similar_df.columns = ['occupation', 'similarity']
        fig_sim = px.bar(similar_df, x='occupation', y='similarity',
                         title=f"👯 Similar to: {selected_occ}",
                         color='similarity', text_auto=True,
                         color_continuous_scale=px.colors.sequential.Oranges)
        fig_sim.update_layout(xaxis_title="", yaxis_title="Similarity Score")
        st.plotly_chart(fig_sim, use_container_width=True)
    else:
        st.warning("⚠️ Similarity data not available for this occupation.")

st.markdown("---")
st.caption("🚀 Built by your data + design team | 📊 Source: Draup")
