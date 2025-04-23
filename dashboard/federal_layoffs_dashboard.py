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
    st.markdown("### 🔎 Filter Options")
    selected_state = st.selectbox("📍 Select a State", sorted(df['state'].unique()))

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
.alt-container {
    background-color: #f9fafb;
    padding: 1.2rem 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    margin-top: 1rem;
}
.row-2x {
    display: flex;
    justify-content: space-between;
    gap: 1.5rem;
}
</style>
<div class='header-strip'>
    <span>Federal Layoffs & Skills Intelligence Dashboard</span>
    <img class='logo' src='https://draupmedia.s3.us-east-2.amazonaws.com/wp-content/uploads/2024/12/13112230/white-logo.svg' alt='Draup Logo'>
</div>
""", unsafe_allow_html=True)

# === Similar Occupation Explorer ===
st.markdown("""
<div class='alt-container'>
<h4 style="margin-bottom: 0.5rem;">
    🔁 Similar Occupation Explorer
</h4>
""", unsafe_allow_html=True)

df['occupation_display'] = df['occupation'].str.title()
selected_occ = st.selectbox("Select an Occupation", sorted(df['occupation_display'].unique()))
selected_key = selected_occ.lower().strip()

if selected_key in df_sim.index:
    similar_df = df_sim.loc[selected_key].sort_values(ascending=False).head(10).reset_index()
    similar_df.columns = ['occupation', 'similarity']
    similar_df['occupation'] = similar_df['occupation'].str.title()

    fig3 = px.bar(similar_df, x="similarity", y="occupation", orientation="h",
                  title=f"Occupations Similar to: {selected_occ}",
                  color="similarity",
                  color_continuous_scale=px.colors.sequential.Oranges)

    fig3.update_layout(xaxis_title="Similarity Score", yaxis_title="", title_font=dict(size=16))
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("⚠️ Similarity data not available for this occupation.")

st.markdown("</div>", unsafe_allow_html=True)
