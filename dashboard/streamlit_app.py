"""
Log Intelligence Pipeline Dashboard

This Streamlit app visualizes insights from DuckDB:
- Event volume over time
- Error trends
- Device health
- Top error codes
- Pipeline quality overview
- Anomaly detection
"""

import duckdb
import plotly.express as px
import streamlit as st

from log_intelligence.config import config
from log_intelligence.pipeline import run_pipeline


# -----------------------------
# DB connection
# -----------------------------
@st.cache_resource
def get_conn():
    """Create and cache a DuckDB connection for dashboard queries."""
    return duckdb.connect(str(config.db_path))


conn = get_conn()

pipeline_stats = conn.execute("""
    SELECT *
    FROM pipeline_runs
    ORDER BY started_at DESC
    LIMIT 1
""").fetchdf()

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filters")

device_list = conn.execute("""
    SELECT DISTINCT device_id
    FROM events
    ORDER BY device_id
""").fetchdf()["device_id"].tolist()

selected_device = st.sidebar.selectbox(
    "Select Device",
    ["All"] + device_list
)

date_range = st.sidebar.date_input(
    "Date range",
    []
)

st.title("📊 Log Intelligence Pipeline Dashboard")

# -----------------------------
# KPI Cards
# -----------------------------
pipeline_stats_latest = pipeline_stats.iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Events", pipeline_stats_latest["records_seen"])
col2.metric("Valid", pipeline_stats_latest["valid_records"])
col3.metric("Invalid", pipeline_stats_latest["invalid_records"])
col4.metric("Duplicates", pipeline_stats_latest["duplicate_records"])

# -----------------------------
# Pipeline refresh
# -----------------------------
if st.sidebar.button("🔄 Rerun Pipeline"):
    run_pipeline(records=1000)
    st.sidebar.success("Pipeline executed successfully")

# -----------------------------
# 1. Pipeline overview
# -----------------------------
st.header("Pipeline Health")

st.dataframe(pipeline_stats)


# -----------------------------
# 2. Event volume over time
# -----------------------------
st.header("Event Volume Over Time")

events_ts = conn.execute("""
    SELECT *
    FROM v_event_volume_hourly
""").fetchdf()

fig = px.line(events_ts, x="hour", y="total_events", title="Event Volume")
st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# 3. Error trends
# -----------------------------
st.header("Error Trends")

errors_ts = conn.execute("""
    SELECT *
    FROM v_failure_trends
""").fetchdf()

fig2 = px.line(errors_ts, x="hour", y="error_count", title="Error Trend")
st.plotly_chart(fig2, use_container_width=True)


# -----------------------------
# 4. Top error codes
# -----------------------------
st.header("Top Error Codes")

error_codes = conn.execute("""
    SELECT *
    FROM v_top_error_codes
""").fetchdf()

fig3 = px.bar(
    error_codes,
    x="error_code",
    y="occurrences",
    title="Most Frequent Error Codes"
)

st.plotly_chart(fig3, use_container_width=True)


# -----------------------------
# 5. Device error rate
# -----------------------------
st.header("Device Error Rate")

device_errors = conn.execute("""
    SELECT *
    FROM v_error_rate_per_device
""").fetchdf()

fig4 = px.bar(
    device_errors,
    x="device_id",
    y="error_rate",
    title="Error Rate per Device"
)

st.plotly_chart(fig4, use_container_width=True)


# -----------------------------
# 6. Device activity
# -----------------------------
st.header("Device Activity Status")

device_activity = conn.execute("""
    SELECT *
    FROM v_device_activity
""").fetchdf()

fig5 = px.pie(
    device_activity,
    names="status",
    title="Active vs Inactive Devices"
)

st.plotly_chart(fig5, use_container_width=True)


# -----------------------------
# 7. Anomalies
# -----------------------------
st.header("Anomaly Detection (Spikes)")

spikes = conn.execute("""
    SELECT *
    FROM v_error_spikes
""").fetchdf()

fig = px.scatter(
    spikes,
    x="hour",
    y="error_count",
    color="anomaly_flag",
    size="error_count",
    title="Anomaly Detection (Spikes)"
)

st.plotly_chart(fig, use_container_width=True)

spike_events = spikes[spikes["anomaly_flag"] == "SPIKE"]

if not spike_events.empty:
    st.subheader("Detected Spikes")
    st.dataframe(spike_events)
else:
    st.info("No spikes detected in current dataset.")
