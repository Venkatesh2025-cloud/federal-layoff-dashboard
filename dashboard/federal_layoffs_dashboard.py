import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# ----------- HEADER -----------
st.set_page_config(page_title="Vijay's Dashboard", layout="wide")
st.title("Hi Vijay 👋, here’s what’s happening today.")

col1, col2, col3 = st.columns([4, 2, 1])
with col1:
    user_filter = st.text_input("User Filter", placeholder="Search or filter by user persona")
with col2:
    date_range = st.date_input("Select Date Range", [datetime(2023, 1, 1), datetime.today()])
with col3:
    st.button("🔄 Refresh")

# ----------- KPI CARDS -----------
st.markdown("### 🔢 Key Performance Indicators")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Revenue", "₹12.5M", "↑ 5%")
kpi2.metric("Active Users", "4,320", "↓ 2%")
kpi3.metric("Churn Rate", "1.1%", "-")
kpi4.metric("Conversion", "2.7%", "↑ 0.3%")

# ----------- TABBED CONTENT -----------
st.markdown("### 📊 Insights Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🧭 Segment Analysis", "🌍 Geographic View", "⚙️ Operational Insights"])

with tab1:
    st.subheader("Engagement Trends Over Time")
    st.caption("Spot anomalies, surges, or drop-offs in performance")
    data = pd.DataFrame({
        "date": pd.date_range(start="2024-01-01", periods=100),
        "value": pd.Series(range(100)).apply(lambda x: x + (x%7)*2)
    })
    line_chart = alt.Chart(data).mark_line().encode(x='date', y='value')
    st.altair_chart(line_chart, use_container_width=True)

with tab2:
    st.subheader("User Segment Analysis")
    st.caption("Identify user behaviors by persona or cohort")
    st.selectbox("Filter by Persona", options=["All", "New Users", "Returning Users", "Churn Risk"])
    st.bar_chart([3, 6, 2, 4])

with tab3:
    st.subheader("Geographic Distribution")
    st.caption("Where are users coming from?")
    st.map(pd.DataFrame({
        'lat': [19.0760, 28.6139, 13.0827],
        'lon': [72.8777, 77.2090, 80.2707]
    }))

with tab4:
    st.subheader("Operational Insights")
    st.caption("Backend/API/system health at a glance")
    st.bar_chart([10, 20, 15, 35])

# ----------- DATA TABLE -----------
st.markdown("### 🔍 Advanced Table View")

with st.expander("🔧 Filter Panel"):
    st.multiselect("Select Columns", options=["User ID", "Event Type", "Timestamp", "Location"])
    st.checkbox("Show only anomalies")

st.download_button("Download CSV", data.to_csv(index=False), file_name="export.csv")

st.dataframe(data.tail(10), use_container_width=True)

# ----------- FOOTER -----------
st.markdown("---")
st.caption("Feedback / Version 1.0 / Powered by Draup")

