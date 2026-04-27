"""
Main Streamlit application for Behavioral Analytics for Energy Security.
"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime

from src.data_loader import load_file, validate_columns
from src.preprocessing import clean_data, extract_features
from src.detector import calculate_user_patterns, detect_rule_based, calculate_risk
from src.ml_model import train_model, predict_anomalies
from src.dashboard import (
    plot_login_hour_distribution,
    plot_daily_login_trend,
    plot_success_failed_pie,
    plot_risk_distribution,
    plot_top_suspicious_users,
    plot_hour_heatmap,
    plot_anomalies_scatter
)
from src.utils import save_report, export_csv

# ---------------------------- PAGE CONFIG ----------------------------
st.set_page_config(
    page_title="Behavioral Analytics | Energy Security",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------- CUSTOM CSS ----------------------------
def local_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css()

# ---------------------------- SESSION STATE ----------------------------
if "df" not in st.session_state:
    st.session_state.df = None
if "anomaly_df" not in st.session_state:
    st.session_state.anomaly_df = None

# ---------------------------- SIDEBAR ----------------------------
st.sidebar.title("🔐 Energy Security Analytics")
uploaded_file = st.sidebar.file_uploader("Upload Login CSV", type=["csv"])

# Load sample data if no upload
if uploaded_file is not None:
    df = load_file(uploaded_file)
    st.sidebar.success("File ready for processing!")
else:
    sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "login_data.csv")
    if os.path.exists(sample_path):
        df = load_file(sample_path)
        st.sidebar.info("Sample dataset ready.")
    else:
        st.error("No dataset found. Please upload a CSV or place sample_data/login_data.csv")
        st.stop()

# Validate columns
expected_cols = ["user_id", "login_time", "status", "location", "device"]
if not validate_columns(df, expected_cols):
    st.error(f"CSV must contain columns: {expected_cols}")
    st.stop()

# Clean & preprocess
df_clean = clean_data(df)
df_feat = extract_features(df_clean)

# Sidebar controls
st.sidebar.markdown("---")
threshold = st.sidebar.slider("Failed attempts threshold", 1, 20, 5)
use_ml = st.sidebar.checkbox("Enable ML (Isolation Forest)", value=True)

st.sidebar.markdown("---")
analyze_btn = st.sidebar.button("🔍 Run Behavioral Analysis", use_container_width=True, type="primary")

# ---------------------------- PROCESSING LOGIC ----------------------------
if analyze_btn or "analysis_done" in st.session_state:
    if analyze_btn or "risk_df" not in st.session_state:
        with st.spinner("🔍 Analyzing behavioral patterns..."):
            # Run detection
            user_patterns, login_data = calculate_user_patterns(df_feat)
            anomaly_df = detect_rule_based(login_data, user_patterns, threshold)
            risk_df = calculate_risk(anomaly_df)

            # ML integration
            if use_ml:
                model, features = train_model(login_data)
                ml_preds = predict_anomalies(model, features)
                login_data['ml_anomaly'] = ml_preds
                mask = (login_data['ml_anomaly'] == 'Suspicious') & (~anomaly_df['is_anomaly'])
                anomaly_df.loc[mask, 'is_anomaly'] = True
                anomaly_df.loc[mask, 'reason'] += " | ML flagged"
                risk_df = calculate_risk(anomaly_df)

            # Persist in session state
            st.session_state.risk_df = risk_df
            st.session_state.anomaly_df = anomaly_df
            st.session_state.login_data = login_data
            st.session_state.analysis_done = True
            st.sidebar.success("Analysis Complete!")
    
    # Retrieve from session state
    risk_df = st.session_state.risk_df
    anomaly_df = st.session_state.anomaly_df
    login_data = st.session_state.login_data
else:
    st.info("👋 Welcome! Please click **'Run Behavioral Analysis'** in the sidebar to begin.")
    st.stop()

st.session_state.df = df_clean
# st.session_state.anomaly_df is already handled above

# ---------------------------- MAIN PAGE TABS ----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📋 Overview", "🚨 Behavioral Analysis", "📊 Dashboard", "📄 Reports", "ℹ️ About"]
)

# ===== TAB 1: OVERVIEW =====
with tab1:
    st.header("Dataset Overview & Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    total_users = df_clean['user_id'].nunique()
    total_logins = len(df_clean)
    anomalies_found = anomaly_df['is_anomaly'].sum()
    high_risk = (risk_df['risk_level'].isin(['High', 'Critical'])).sum()
    col1.metric("Total Users", total_users)
    col2.metric("Total Logins", total_logins)
    col3.metric("Anomalies Found", anomalies_found)
    col4.metric("High Risk Users", high_risk)

    st.subheader("Dataset Preview")
    st.dataframe(df_feat.head(100), width="stretch")

# ===== TAB 2: BEHAVIORAL ANALYSIS =====
with tab2:
    st.header("Suspicious Activity Analysis")
    # Filter controls
    risk_filter = st.multiselect("Filter by Risk Level", options=risk_df['risk_level'].unique().tolist(), default=None)
    if risk_filter:
        display_df = risk_df[risk_df['risk_level'].isin(risk_filter)]
    else:
        display_df = risk_df
    st.dataframe(display_df[display_df['is_anomaly']], width="stretch")

    st.markdown("### Risk Score Distribution")
    st.bar_chart(risk_df['risk_score'].value_counts().sort_index())

# ===== TAB 3: DASHBOARD =====
with tab3:
    st.header("Interactive Analytics Dashboard")
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(plot_login_hour_distribution(df_feat), width="stretch")
    with col_right:
        st.plotly_chart(plot_success_failed_pie(df_feat), width="stretch")

    st.plotly_chart(plot_daily_login_trend(df_feat), width="stretch")

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(plot_risk_distribution(risk_df), width="stretch")
    with col_b:
        st.plotly_chart(plot_top_suspicious_users(risk_df), width="stretch")

    st.plotly_chart(plot_hour_heatmap(df_feat), width="stretch")

    if use_ml:
        st.subheader("ML Anomaly View (PCA projection)")
        st.plotly_chart(plot_anomalies_scatter(login_data), width="stretch")

# ===== TAB 4: REPORTS =====
with tab4:
    st.header("Export Anomaly Report")
    st.dataframe(risk_df[risk_df['is_anomaly']], width="stretch")

    if st.button("Save Report to CSV"):
        report_path = os.path.join(os.path.dirname(__file__), "reports", "anomaly_report.csv")
        save_report(risk_df[risk_df['is_anomaly']], report_path)
        st.success(f"Report saved to {report_path}")
        st.download_button(
            label="Download CSV",
            data=export_csv(risk_df[risk_df['is_anomaly']]),
            file_name=f"anomaly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ===== TAB 5: ABOUT =====
with tab5:
    st.header("Behavioral Analytics for Energy Security")
    st.markdown("""
    ### Objective  
    Detect suspicious login activity in the Energy sector using rule‑based analytics and optional machine learning.

    ### How It Works  
    1. Upload a CSV of login records (user, time, status, location, device).  
    2. The system extracts features (hour, day, weekday, etc.).  
    3. Multiple detection rules flag anomalies:  
       - **Suspicious Time**: login at 3 AM  
       - **Time Deviation**: far from user’s average login time  
       - **Failed Attempts**: exceeding a threshold  
       - **Frequency Spike**: sudden increase in activity  
       - **Unknown Device**: new device for a user  
    4. A **Risk Score** (0‑100) is computed for each flagged event.  
    5. Optionally, an **Isolation Forest** model detects outliers.  
    6. Results are shown on an interactive dashboard and can be exported.

    ### Tech Stack  
    Python, Streamlit, Pandas, Scikit‑learn, Plotly, Matplotlib, Seaborn, Joblib

    ### Author  
    Cybersecurity Analytics Team  
    Energy Sector Threat Intelligence Division
    """)