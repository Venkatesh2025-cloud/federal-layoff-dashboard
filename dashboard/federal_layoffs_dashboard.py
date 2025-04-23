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
    padding: 0.7rem 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    margin-top: 0.3rem;
    color: white;
    font-family: 'Inter', sans-serif;
    font-size: 1.4rem;
    font-weight: 500;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}
.header-strip .logo {
    height: 36px;
}
</style>
<div class='header-strip'>
    <span>Federal Layoffs & Skills Intelligence Dashboard</span>
    <img class='logo' src='https://draupmedia.s3.us-east-2.amazonaws.com/wp-content/uploads/2024/12/13112230/white-logo.svg' alt='Draup Logo'>
</div>
""", unsafe_allow_html=True)

# === KPI Cards Refined ===
st.markdown("""
<style>
.kpi-container {
    display: flex;
    justify-content: space-between;
    gap: 1.2rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    flex: 1;
    background: #ffffff;
    border-radius: 14px;
    padding: 1.4rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: transform 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
}
.kpi-icon {
    width: 50px;
    height: 50px;
    border-radius: 12px;
    font-size: 1.3rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f3f4f6;
}
.kpi-text h4 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
    font-family: 'Inter', sans-serif;
}
.kpi-text p {
    margin: 0;
    font-size: 0.9rem;
    font-weight: 500;
    color: #6b7280;
    font-family: 'Inter', sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-icon" style="background-color: #d1fae5; color: #059669;">
            <img src="https://cdn-icons-png.flaticon.com/512/747/747376.png" style="width: 24px; height: 24px;">
        </div>
        <div class="kpi-text">
            <h4>{df_filtered['talent_size'].sum():,}</h4>
            <p>Total Workforce</p>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon" style="background-color: #fef3c7; color: #b45309;">
            <img src="https://cdn-icons-png.flaticon.com/512/595/595067.png" style="width: 24px; height: 24px;">
        </div>
        <div class="kpi-text">
            <h4>{df_filtered['estimate_layoff'].sum():,}</h4>
            <p>Estimated Layoffs</p>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon" style="background-color: #dbeafe; color: #1e3a8a;">
            <img src="https://cdn-icons-png.flaticon.com/512/1055/1055687.png" style="width: 24px; height: 24px;">
        </div>
        <div class="kpi-text">
            <h4>{df_filtered['skill'].nunique():,}</h4>
            <p>Unique Skills</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
