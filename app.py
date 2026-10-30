import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="AIOps Log Anomaly Detector", layout="wide")

st.title("🛡️ Intelligent System Log Parsing & Anomaly Detection (AIOps)")
st.markdown("Automated unstructured log parsing with **Drain3** and unsupervised session anomaly detection via **Isolation Forest**.")

@st.cache_data
def load_data():
    parsed = pd.read_csv("data/HDFS_parsed.csv")
    templates = pd.read_csv("data/HDFS_templates.csv")
    results = pd.read_csv("data/anomaly_results.csv")
    return parsed, templates, results

try:
    parsed_df, templates_df, results_df = load_data()

    col1, col2, col3, col4 = st.columns(4)
    total_logs = len(parsed_df)
    total_templates = len(templates_df)
    total_sessions = len(results_df)
    total_anomalies = int(results_df['Anomaly_Flag'].sum())

    col1.metric("Total Raw Logs Processed", f"{total_logs:,}")
    col2.metric("Unique Log Templates (Drain3)", f"{total_templates:,}")
    col3.metric("Total Block Sessions", f"{total_sessions:,}")
    col4.metric("Anomalous Sessions Detected", f"{total_anomalies:,}", f"{(total_anomalies/total_sessions)*100:.2f}% Rate", delta_color="inverse")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Anomaly Score Distribution")
        fig_hist = px.histogram(
            results_df, x="Anomaly_Score", color="Status",
            color_discrete_map={"NORMAL": "#2ecc71", "ANOMALY": "#e74c3c"},
            nbins=40
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        st.subheader("Top Mined Log Templates")
        fig_bar = px.bar(
            templates_df.head(10), x="Occurrences", y="EventId",
            orientation="h", hover_data=["EventTemplate"], color="Occurrences"
        )
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("🔍 Root Cause Session Log Inspector")
    anomalous_blocks = results_df[results_df['Status'] == 'ANOMALY'].sort_values(by='Anomaly_Score')['BlockId'].tolist()
    selected_block = st.selectbox("Select Anomalous BlockId to Inspect Trace:", anomalous_blocks)

    if selected_block:
        trace_df = parsed_df[parsed_df['BlockId'] == selected_block][['LineId', 'Date', 'Time', 'Level', 'EventId', 'Component', 'EventTemplate', 'RawContent']]
        st.dataframe(trace_df, use_container_width=True)

except FileNotFoundError:
    st.warning("Jalankan perintah `python main.py` di terminal terlebih dahulu untuk menghasilkan data parsing dan model.")