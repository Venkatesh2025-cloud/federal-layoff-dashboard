
# federal_layoffs_dashboard_enhanced.py

import pandas as pd
import streamlit as st
import plotly.express as px
import os
import altair as alt

st.set_page_config(page_title="Federal Layoffs & Skills Intelligence Dashboard", layout="wide")

# === Safe CSV Reader ===
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

with st.spinner("Loading datasets..."):
    try:
        df, df_summary, df_signal, df_sim = load_data()
    except Exception as e:
        st.error(f"Failed to load datasets: {e}")
        st.stop()

# Clean and prepare data
for d in [df, df_summary, df_signal]:
    d.columns = d.columns.str.lower().str.strip().str.replace(" ", "_")

df_sim.columns = df_sim.columns.str.lower().str.strip()
df_sim.index = df_sim.index.str.lower().str.strip()

df['state'] = df['state'].str.strip().str.title()
df_signal['state'] = df_signal['state'].str.strip().str.title()
df_signal['date'] = pd.to_datetime(df_signal['date'], errors='coerce')
df_signal['estimated_layoff'] = pd.to_numeric(df_signal['estimated_layoff'].replace("Unspecified number", pd.NA), errors='coerce')

# === Sidebar ===
st.sidebar.header("📍 Filter by State")
state_list = sorted(df['state'].unique())
selected_state = st.sidebar.selectbox("State", state_list)
df_filtered = df[df['state'] == selected_state]

# === Header ===
header_html = (
    "<h1 style='text-align: center; background-color: #003366; color: white; "
    "padding: 1rem; border-radius: 8px;'>Federal Layoffs & Skills Intelligence Dashboard</h1>"
)
st.markdown(header_html, unsafe_allow_html=True)

# === KPI Section ===
total_workforce = df_filtered['talent_size'].sum()
total_layoffs = df_filtered['estimate_layoff'].sum()
layoff_rate = (total_layoffs / total_workforce) * 100 if total_workforce else 0
unique_skills = df_filtered['skill'].nunique()

kpi_html = f'''
<div style="display: flex; justify-content: space-around; font-family: 'Inter', sans-serif;">
    <div style="background: #dcfce7; border-radius: 12px; padding: 1rem; text-align: center; width: 23%;">
        <div style="font-size: 1.7rem; font-weight: 600; color: #15803d;">{total_workforce:,}</div>
        <div style="color: #444; font-size: 0.95rem;">Total Workforce</div>
    </div>
    <div style="background: #ffedd5; border-radius: 12px; padding: 1rem; text-align: center; width: 23%;">
        <div style="font-size: 1.7rem; font-weight: 600; color: #c2410c;">{total_layoffs:,}</div>
        <div style="color: #444; font-size: 0.95rem;">Estimated Layoffs</div>
    </div>
    <div style="background: #e0f2fe; border-radius: 12px; padding: 1rem; text-align: center; width: 23%;">
        <div style="font-size: 1.7rem; font-weight: 600; color: #0284c7;">{layoff_rate:.1f}%</div>
        <div style="color: #444; font-size: 0.95rem;">Layoff Rate</div>
    </div>
    <div style="background: #ede9fe; border-radius: 12px; padding: 1rem; text-align: center; width: 23%;">
        <div style="font-size: 1.7rem; font-weight: 600; color: #7c3aed;">{unique_skills:,}</div>
        <div style="color: #444; font-size: 0.95rem;">Unique Skills</div>
    </div>
</div>
'''
st.markdown(kpi_html, unsafe_allow_html=True)

# === Main Tabs ===
t1, t2, t3 = st.tabs(["📊 Layoff Summary", "📰 Layoff News", "🧭 Similar Occupations"])

with t1:
    st.subheader("Most At-Risk Occupations")
    top_jobs = df_filtered.groupby("occupation")[["estimate_layoff", "talent_size"]].sum().reset_index()
    top_jobs["layoff_rate"] = (top_jobs["estimate_layoff"] / top_jobs["talent_size"]) * 100
    top_jobs = top_jobs.sort_values("estimate_layoff", ascending=False).head(5)

    fig_jobs = px.bar(top_jobs, x="occupation", y="layoff_rate", color="layoff_rate",
                      title="Top Occupations by Layoff Rate",
                      labels={"layoff_rate": "% Layoff Rate"},
                      color_continuous_scale=px.colors.sequential.Blues)
    st.plotly_chart(fig_jobs, use_container_width=True)

    st.subheader("Critical Skills in Selected Occupation")
    selected_occ = st.selectbox("Select an Occupation", top_jobs["occupation"].tolist())
    filtered_skills = df_filtered[df_filtered["occupation"] == selected_occ]
    top_skills = filtered_skills.groupby("skill")["estimate_layoff"].sum().reset_index().sort_values("estimate_layoff", ascending=False).head(5)

    fig_skills = px.bar(top_skills, x="skill", y="estimate_layoff", color="estimate_layoff",
                        title=f"Top Skills Impacted in {selected_occ}",
                        color_continuous_scale=px.colors.sequential.Teal)
    st.plotly_chart(fig_skills, use_container_width=True)

with t2:
    st.subheader(f"Layoff News in {selected_state}")
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

        st.markdown("**Layoff News Articles**")
        for _, row in df_signal_filtered.iterrows():
            with st.expander(f"{row['date'].strftime('%b %d, %Y')} — {row['agency_name']}"):
                st.markdown(f"**Title**: {row['article_title']}")
                st.markdown(f"**Estimated Layoffs**: {int(row['estimated_layoff']) if pd.notna(row['estimated_layoff']) else 'Unspecified'}")
                st.markdown(f"[🔗 Source]({row['source_link']})")

with t3:
    st.subheader("Explore Similar Occupations (Optional)")
    occupation_list = sorted(df['occupation'].unique())
    selected_occ_sim = st.selectbox("Choose an occupation", occupation_list)
    selected_key = selected_occ_sim.lower().strip()
    if selected_key in df_sim.index:
        similar_df = df_sim.loc[selected_key].sort_values(ascending=False).head(10).reset_index()
        similar_df.columns = ['occupation', 'similarity']
        fig_sim = px.bar(similar_df, x='occupation', y='similarity',
                         title=f"Most Similar to {selected_occ_sim}",
                         color='similarity',
                         color_continuous_scale=px.colors.sequential.Oranges)
        st.plotly_chart(fig_sim, use_container_width=True)
    else:
        st.info("Similarity data not available for this occupation.")

# === Footer ===
st.markdown("---")
st.caption("Built with ❤️ by your data + design team. Data source: Draup")
