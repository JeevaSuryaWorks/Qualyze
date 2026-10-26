from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from datasentinel.audit import audit_dataframe
from datasentinel.cleaning import clean_dataframe
from datasentinel.reporting import build_html_report
from datasentinel.storage import init_db, save_audit, recent_audits

ROOT = Path(__file__).parent
SAMPLE = ROOT / "data" / "sample_customers.csv"

st.set_page_config(
    page_title="DataSentinel · Autonomous Dataset Quality Engineer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

# ==========================================
# MODERN AESTHETIC CUSTOM CSS & DESIGN SYSTEM
# ==========================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
/* Base typography and smooth rendering */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Background atmospheric subtle gradients */
.stApp {
    background: radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.08) 0%, transparent 45%),
                radial-gradient(circle at 85% 80%, rgba(14, 165, 233, 0.06) 0%, transparent 45%),
                #0b0f19 !important;
    color: #f8fafc;
}

/* Main Container margins */
.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1350px !important;
}

/* Hero Header Styling */
.hero-container {
    background: linear-gradient(135deg, rgba(26, 34, 53, 0.75) 0%, rgba(15, 23, 42, 0.85) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 30px 36px;
    margin-bottom: 24px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    position: relative;
    overflow: hidden;
}

.hero-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #06b6d4, #10b981, #6366f1);
    background-size: 200% 100%;
    animation: gradientMove 6s linear infinite;
}

@keyframes gradientMove {
    0% { background-position: 0% 0%; }
    100% { background-position: 200% 0%; }
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.3);
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    color: #818cf8;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.hero-pill-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 10px #10b981;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.9); }
}

.hero-title {
    font-size: 34px !important;
    font-weight: 800 !important;
    letter-spacing: -0.8px !important;
    margin: 0 0 8px 0 !important;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: flex;
    align-items: center;
    gap: 12px;
}

.hero-subtitle {
    font-size: 15px !important;
    color: #94a3b8 !important;
    margin-bottom: 18px !important;
    font-weight: 400;
    line-height: 1.5;
}

.hero-badges {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.hero-badge-item {
    font-size: 12px;
    font-weight: 500;
    color: #cbd5e1;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.07);
    padding: 4px 12px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* Glassmorphism KPI Stat Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.kpi-card {
    background: linear-gradient(145deg, rgba(20, 27, 45, 0.8) 0%, rgba(13, 19, 33, 0.9) 100%);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.35);
    position: relative;
    overflow: hidden;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

.kpi-card:hover {
    transform: translateY(-3px);
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 16px 32px -8px rgba(0, 0, 0, 0.5), 0 0 20px rgba(99, 102, 241, 0.15);
}

.kpi-icon {
    font-size: 20px;
    margin-bottom: 10px;
    display: inline-block;
}

.kpi-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #94a3b8;
    margin-bottom: 4px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
    font-family: 'JetBrains Mono', monospace;
}

.kpi-sub {
    font-size: 11px;
    color: #64748b;
    margin-top: 6px;
}

/* Score Ribbon & Health Status */
.health-ribbon {
    background: linear-gradient(145deg, rgba(19, 27, 46, 0.85) 0%, rgba(11, 16, 29, 0.95) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 18px 24px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    flex-wrap: wrap;
}

.score-badge {
    padding: 6px 14px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* Streamlit Tabs Polish */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(15, 23, 42, 0.7);
    padding: 6px;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    margin-bottom: 20px;
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 10px;
    color: #94a3b8;
    font-size: 14px;
    font-weight: 600;
    border: none !important;
    padding: 0 20px;
    transition: all 0.2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.04);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
}

/* Findings Cards */
.finding-card {
    background: linear-gradient(145deg, rgba(19, 27, 46, 0.7) 0%, rgba(13, 19, 33, 0.8) 100%);
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 18px 22px;
    margin-bottom: 14px;
    transition: all 0.2s ease;
}

.finding-card:hover {
    transform: translateX(4px);
}

.finding-card.severity-high {
    border-left: 5px solid #ef4444;
    box-shadow: -4px 0 16px -4px rgba(239, 68, 68, 0.3);
}

.finding-card.severity-medium {
    border-left: 5px solid #f59e0b;
    box-shadow: -4px 0 16px -4px rgba(245, 158, 11, 0.3);
}

.finding-card.severity-low {
    border-left: 5px solid #06b6d4;
    box-shadow: -4px 0 16px -4px rgba(6, 182, 212, 0.3);
}

.pill-high {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}

.pill-medium {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.3);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}

.pill-low {
    background: rgba(6, 182, 212, 0.15);
    color: #38bdf8;
    border: 1px solid rgba(6, 182, 212, 0.3);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}

.affected-badge {
    background: rgba(255, 255, 255, 0.05);
    color: #cbd5e1;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
}

.section-box {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 20px;
}

/* Custom Buttons & Download buttons */
.stButton > button, .stDownloadButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4) !important;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 22px rgba(99, 102, 241, 0.6) !important;
    transform: translateY(-1px) !important;
}

/* Dataframe Styling */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #0c101c !important;
    border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
}

/* Custom Callout */
.info-callout {
    background: rgba(99, 102, 241, 0.08);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-left: 4px solid #6366f1;
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 13px;
    color: #cbd5e1;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
        <span style="font-size:26px;">🛡️</span>
        <div>
            <div style="font-weight:800;font-size:18px;color:#fff;letter-spacing:-0.5px;">DataSentinel</div>
            <div style="font-size:11px;color:#818cf8;font-weight:600;letter-spacing:0.5px;">PROFILER & RADAR v1.2</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📂 Dataset Source")
    
    uploaded = st.file_uploader("Upload CSV dataset", type=["csv"], help="Upload any tabular CSV dataset to audit.")
    use_sample = st.checkbox("Load demonstration sample", value=uploaded is None, help="Uses the customer churn demo dataset.")
    
    st.markdown("### 🎯 Target Variable")
    target_option = st.text_input("Target column name (optional)", value="churn", help="Specify supervised learning target for leakage & association checks.")
    
    st.markdown("---")
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:12px;font-size:12px;color:#94a3b8;">
        <div style="font-weight:600;color:#cbd5e1;margin-bottom:6px;">⚡ Guardrail Protocol</div>
        <div>• 100% In-memory execution</div>
        <div>• Zero telemetry or cloud egress</div>
        <div>• Non-destructive cleaning</div>
        <div>• Local SQLite audit history</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# MAIN APPLICATION LOGIC
# ==========================================
try:
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        source_name = uploaded.name
    elif use_sample:
        df = pd.read_csv(SAMPLE)
        source_name = "sample_customers.csv"
    else:
        st.markdown("""
        <div style="text-align:center;padding:80px 20px;">
            <div style="font-size:48px;margin-bottom:16px;">📂</div>
            <h2 style="color:#cbd5e1;">Awaiting Dataset Input</h2>
            <p style="color:#64748b;max-width:480px;margin:0 auto 20px auto;">
                Upload a CSV in the sidebar or toggle "Load demonstration sample" to start the automated dataset audit.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # Target resolution
    target = target_option.strip() if target_option.strip() in df.columns else None
    
    # Audit Execution
    report = audit_dataframe(df, target=target)
    summary = report["summary"]
    findings = report["findings"]
    score = summary["quality_score"]

    # Determine health grade
    if score >= 90:
        grade = "Grade A"
        grade_desc = "Optimal Production Quality"
        badge_style = "background:rgba(16,185,129,0.15);color:#34d399;border:1px solid rgba(16,185,129,0.3);"
        score_color = "#10b981"
    elif score >= 75:
        grade = "Grade B"
        grade_desc = "Acceptable · Minor Anomalies"
        badge_style = "background:rgba(56,189,248,0.15);color:#38bdf8;border:1px solid rgba(56,189,248,0.3);"
        score_color = "#38bdf8"
    elif score >= 60:
        grade = "Grade C"
        grade_desc = "Review Required · Leakage Risks"
        badge_style = "background:rgba(245,158,11,0.15);color:#fbbf24;border:1px solid rgba(245,158,11,0.3);"
        score_color = "#f59e0b"
    else:
        grade = "Grade D"
        grade_desc = "High ML Readiness Risks"
        badge_style = "background:rgba(239,68,68,0.15);color:#f87171;border:1px solid rgba(239,68,68,0.3);"
        score_color = "#ef4444"

    # Hero Banner
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-pill">
            <span class="hero-pill-dot"></span>
            ACTIVE AUDIT · {source_name}
        </div>
        <h1 class="hero-title">
            <span>🛡️</span> DataSentinel
        </h1>
        <div class="hero-subtitle">
            Autonomous Dataset Quality Engineer & Machine Learning Readiness Profiler
        </div>
        <div class="hero-badges">
            <div class="hero-badge-item">🎯 Target: <b>{target if target else 'Unspecified (General Profiling)'}</b></div>
            <div class="hero-badge-item">🧠 Heuristic ML Leakage Radar</div>
            <div class="hero-badge-item">⚡ 1-Click Conservative Repair</div>
            <div class="hero-badge-item">📜 Local Ledger Enabled</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if target_option.strip() and target is None:
        st.markdown(f"""
        <div class="info-callout" style="border-left-color:#f59e0b;background:rgba(245,158,11,0.08);">
            ⚠️ Specified target column <b>'{target_option.strip()}'</b> was not found in dataset headers. Target-specific leakage and association checks were bypassed.
        </div>
        """, unsafe_allow_html=True)

    # Glassmorphism KPI Grid
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <span class="kpi-icon">📁</span>
            <div class="kpi-label">Total Records</div>
            <div class="kpi-value">{summary['rows']:,}</div>
            <div class="kpi-sub">Dataset row count</div>
        </div>
        <div class="kpi-card">
            <span class="kpi-icon">🏷️</span>
            <div class="kpi-label">Attributes</div>
            <div class="kpi-value">{summary['columns']:,}</div>
            <div class="kpi-sub">Profiled feature columns</div>
        </div>
        <div class="kpi-card">
            <span class="kpi-icon">⚠️</span>
            <div class="kpi-label">Flagged Issues</div>
            <div class="kpi-value" style="color: {'#ef4444' if len(findings) > 0 else '#10b981'}">{len(findings):,}</div>
            <div class="kpi-sub">Requires inspection</div>
        </div>
        <div class="kpi-card">
            <span class="kpi-icon">🛡️</span>
            <div class="kpi-label">Quality Index</div>
            <div class="kpi-value" style="color: {score_color}">{score} <span style="font-size:16px;color:#64748b">/100</span></div>
            <div class="kpi-sub">{grade} · {grade_desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Health & Progress bar
    st.progress(summary["quality_score"] / 100)
    
    st.markdown(f"""
    <div class="health-ribbon">
        <div style="display:flex;align-items:center;gap:12px;">
            <div class="score-badge" style="{badge_style}">
                ● {grade} ({score}/100)
            </div>
            <span style="font-size:13px;color:#cbd5e1;font-weight:500;">
                {grade_desc}
            </span>
        </div>
        <div style="font-size:12px;color:#64748b;">
            Heuristic prioritization index for model risk management
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dataset Intelligence",
        f"🚨 Risk Radar ({len(findings)})",
        "⚡ Remediation & Export",
        "📜 Audit Ledger"
    ])

    # ==========================================
    # TAB 1: DATASET INTELLIGENCE
    # ==========================================
    with tab1:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("#### 📉 Missing Value Distribution")
            missing = report["column_profile"]
            missing_plot = missing[missing["missing_count"] > 0].sort_values("missing_pct", ascending=True)
            
            if missing_plot.empty:
                st.markdown("""
                <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:12px;padding:28px;text-align:center;margin-top:10px;">
                    <div style="font-size:28px;margin-bottom:6px;">✨</div>
                    <div style="color:#34d399;font-weight:600;">Zero Missing Values Detected</div>
                    <div style="font-size:12px;color:#94a3b8;margin-top:4px;">All columns have 100% data completeness.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                fig_missing = px.bar(
                    missing_plot,
                    x="missing_pct",
                    y="column",
                    orientation="h",
                    color="missing_pct",
                    color_continuous_scale=["#38bdf8", "#f59e0b", "#ef4444"],
                    labels={"missing_pct": "Missing (%)", "column": "Feature"}
                )
                fig_missing.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=10, b=10),
                    font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
                    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", ticksuffix="%"),
                    yaxis=dict(showgrid=False),
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_missing, use_container_width=True)

        with col_right:
            st.markdown("#### 🧩 Inferred Attribute Types")
            type_counts = report["column_profile"]["inferred_type"].value_counts().rename_axis("type").reset_index(name="columns")
            
            fig_types = px.pie(
                type_counts,
                names="type",
                values="columns",
                hole=0.6,
                color_discrete_sequence=["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#ec4899"]
            )
            fig_types.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(family="Plus Jakarta Sans", color="#cbd5e1"),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            fig_types.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='#0b0f19', width=2))
            )
            st.plotly_chart(fig_types, use_container_width=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📋 Detailed Column Profiling Matrix")
        st.dataframe(
            report["column_profile"],
            use_container_width=True,
            hide_index=True,
            column_config={
                "column": "Column Name",
                "inferred_type": "Data Type",
                "missing_count": st.column_config.NumberColumn("Missing Cells"),
                "missing_pct": st.column_config.ProgressColumn("Missing %", min_value=0, max_value=100, format="%.2f%%"),
                "unique_values": st.column_config.NumberColumn("Unique Values")
            }
        )

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🔍 Raw Dataset Sample (First 25 Rows)")
        st.dataframe(df.head(25), use_container_width=True)

    # ==========================================
    # TAB 2: RISK RADAR & FINDINGS
    # ==========================================
    with tab2:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        if not findings:
            st.markdown("""
            <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:16px;padding:48px 24px;text-align:center;">
                <div style="font-size:42px;margin-bottom:12px;">🛡️</div>
                <h3 style="color:#34d399;font-weight:700;">Clean Audit: No Risk Flags Triggered</h3>
                <p style="color:#94a3b8;max-width:500px;margin:8px auto 0 auto;">
                    DataSentinel did not find excessive missingness, constant columns, exact duplicates, or high target leakage signals.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            col_filter, col_dl = st.columns([3, 1])
            with col_filter:
                severity_filter = st.multiselect(
                    "Filter by Risk Severity",
                    ["High", "Medium", "Low"],
                    default=["High", "Medium", "Low"],
                    label_visibility="collapsed"
                )
            with col_dl:
                st.download_button(
                    "📥 Export Findings JSON",
                    json.dumps(findings, indent=2).encode("utf-8"),
                    file_name=f"{source_name}_findings.json",
                    mime="application/json",
                    use_container_width=True
                )

            shown = [f for f in findings if f["severity"] in severity_filter]
            
            if not shown:
                st.info("No findings match the selected severity filter.")
            else:
                for f in shown:
                    sev = f["severity"].lower()
                    sev_class = f"severity-{sev}"
                    pill_class = f"pill-{sev}"
                    
                    st.markdown(f"""
                    <div class="finding-card {sev_class}">
                        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
                            <div style="display:flex;align-items:center;gap:10px;">
                                <span class="{pill_class}">{f['severity'].upper()} RISK</span>
                                <span style="font-weight:700;font-size:16px;color:#fff;">{f['title']}</span>
                                <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#818cf8;background:rgba(99,102,241,0.1);padding:2px 8px;border-radius:4px;">{f['rule_id']}</span>
                            </div>
                            <span class="affected-badge">{f['affected']:,} Affected</span>
                        </div>
                        <div style="color:#cbd5e1;font-size:14px;margin-bottom:12px;line-height:1.5;">
                            {f['description']}
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;background:rgba(0,0,0,0.2);padding:12px;border-radius:8px;font-size:13px;">
                            <div>
                                <span style="color:#f59e0b;font-weight:600;">⚠️ Impact Analysis:</span>
                                <div style="color:#94a3b8;margin-top:2px;">{f['impact']}</div>
                            </div>
                            <div>
                                <span style="color:#10b981;font-weight:600;">💡 Recommended Remediation:</span>
                                <div style="color:#94a3b8;margin-top:2px;">{f['recommendation']}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ==========================================
    # TAB 3: REMEDIATION & EXPORT
    # ==========================================
    with tab3:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="info-callout">
            <span>🛡️</span>
            <div>
                <b>Conservative Execution Protocol:</b> Transformations are applied in-memory and produce a pristine copy. Your source data is never modified.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### ⚙️ Configure Transformation Pipeline")
        
        c1, c2 = st.columns(2)
        with c1:
            drop_duplicates = st.checkbox("🧹 Remove exact duplicate records", value=True, help="Eliminates redundant identical rows.")
            fill_missing = st.checkbox("🩹 Impute missing values (median for numeric, mode for categorical)", value=False, help="Replaces null values conservatively.")
        with c2:
            drop_empty = st.checkbox("🗑️ Drop 100% empty columns", value=False, help="Removes columns with zero valid records.")
            drop_constant = st.checkbox("⏸️ Drop zero-variance (constant) columns", value=False, help="Removes columns that contain only a single value.")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 Execute In-Memory Cleaning Pipeline", type="primary", use_container_width=True):
            cleaned, actions = clean_dataframe(
                df,
                drop_duplicates=drop_duplicates,
                fill_missing=fill_missing,
                drop_empty=drop_empty,
                drop_constant=drop_constant
            )
            st.session_state["cleaned_df"] = cleaned
            st.session_state["clean_actions"] = actions
            st.success("✅ Transformation pipeline completed successfully!")

        if "cleaned_df" in st.session_state:
            cleaned = st.session_state["cleaned_df"]
            actions = st.session_state["clean_actions"]
            
            rows_removed = max(0, len(df) - len(cleaned))
            
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            st.markdown("#### 📊 Transformation Impact Metrics")
            
            kpi_orig, kpi_clean, kpi_delta = st.columns(3)
            with kpi_orig:
                st.metric("Source Records", f"{len(df):,}")
            with kpi_clean:
                st.metric("Cleaned Records", f"{len(cleaned):,}")
            with kpi_delta:
                st.metric("Records Pruned / Filtered", f"{rows_removed:,}", delta=-rows_removed if rows_removed > 0 else 0)

            st.markdown("#### 🔍 Cleaned Dataset Preview")
            st.dataframe(cleaned.head(25), use_container_width=True)

            with st.expander("📋 Execution Pipeline Log & Audit Trail"):
                st.json(actions)

            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                st.download_button(
                    "📥 Download Cleaned CSV",
                    cleaned.to_csv(index=False).encode("utf-8"),
                    file_name=f"{source_name.replace('.csv', '')}_cleaned.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with dl_col2:
                st.download_button(
                    "📥 Download Execution Log JSON",
                    json.dumps(actions, indent=2).encode("utf-8"),
                    file_name=f"{source_name.replace('.csv', '')}_cleaning_log.json",
                    mime="application/json",
                    use_container_width=True
                )

    # ==========================================
    # TAB 4: AUDIT HISTORY LEDGER
    # ==========================================
    with tab4:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        history = recent_audits()
        
        if history:
            hist_df = pd.DataFrame(history)
            
            h_col1, h_col2, h_col3 = st.columns(3)
            with h_col1:
                st.metric("Total Historical Audits", f"{len(hist_df):,}")
            with h_col2:
                st.metric("Average Quality Score", f"{hist_df['quality_score'].mean():.1f} / 100")
            with h_col3:
                st.metric("Total Issues Recorded", f"{hist_df['finding_count'].sum():,}")
                
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            st.markdown("#### 📜 Persistent Audit Ledger (SQLite)")
            st.dataframe(
                hist_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "Audit ID",
                    "source_name": "Source File",
                    "row_count": st.column_config.NumberColumn("Rows"),
                    "column_count": st.column_config.NumberColumn("Cols"),
                    "finding_count": st.column_config.NumberColumn("Issues"),
                    "quality_score": st.column_config.ProgressColumn("Quality Score", min_value=0, max_value=100, format="%d/100"),
                    "created_at": "Timestamp (UTC)"
                }
            )
        else:
            st.info("No saved audit history in SQLite ledger yet.")

    # ==========================================
    # FOOTER & GLOBAL ACTIONS
    # ==========================================
    st.markdown("---")
    foot_left, foot_right = st.columns([2, 1])
    
    with foot_left:
        audit_id = save_audit(source_name, summary, findings)
        st.markdown(f"""
        <div style="font-size:12px;color:#64748b;display:flex;align-items:center;gap:8px;">
            <span>🔒</span>
            <span>Audit committed to local ledger · <b>ID #{audit_id}</b> · SHA-verified in-memory session</span>
        </div>
        """, unsafe_allow_html=True)
        
    with foot_right:
        html_report = build_html_report(source_name, report)
        st.download_button(
            "📄 Export Executive HTML Audit Report",
            html_report.encode("utf-8"),
            file_name=f"{source_name}_executive_report.html",
            mime="text/html",
            use_container_width=True
        )

except Exception as exc:
    st.error(f"Could not audit this dataset: {exc}")
    st.markdown("""
    <div class="info-callout" style="border-left-color:#ef4444;background:rgba(239,68,68,0.08);">
        Please ensure the uploaded file is a valid, uncorrupted CSV with utf-8 or ascii encoding.
    </div>
    """, unsafe_allow_html=True)
