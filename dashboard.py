import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
try:
    from google import genai
    from google.genai import types
    SDK_VERSION = "new"
except ImportError:
    try:
        import google.generativeai as genai
        SDK_VERSION = "legacy"
    except ImportError:
        SDK_VERSION = None
import os

import textwrap

def st_html(html_str, **kwargs):
    # Strip leading/trailing whitespace and drop empty lines to avoid Markdown code blocks
    cleaned = '\n'.join([line.strip() for line in html_str.split('\n') if line.strip()])
    # We force unsafe_allow_html=True internally
    st.markdown(cleaned, unsafe_allow_html=True)

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Precision Earth | Soil Health Monitor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CONSTANTS ─────────────────────────────────────────────────
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    GEMINI_API_KEY = "AIzaSyBXQZwWuXX0vf6HQBTBXoFcCs3ZkGux23M"
WILTING_POINT = 10.0
FIELD_CAPACITY = 35.0
EC_STRESS = 4.0
PH_ACID = 5.5
PH_ALK  = 7.5

# ── GLOBAL CSS ────────────────────────────────────────────────
st.markdown("""
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script id="tailwind-config">
    tailwind.config = {
        corePlugins: { preflight: false }, // Prevent Tailwind from breaking Streamlit's native buttons & sliders
        theme: {
            extend: {
                colors: {
                    "surface-container-low": "#1a1c1a",
                    "error-container": "#93000a",
                    "tertiary": "#ffb3ac",
                    "background": "#0e110e",
                    "tertiary-container": "#79000b",
                    "on-error": "#690005",
                    "secondary": "#a5c8ff",
                    "surface-variant": "#42493e",
                    "on-error-container": "#ffdad6",
                    "surface-bright": "#353a34",
                    "surface": "#1a1c1a",
                    "inverse-primary": "#3b6934",
                    "outline": "#8c9388",
                    "surface-container-lowest": "#0a0c0a",
                    "secondary-container": "#004786",
                    "on-surface-variant": "#c2c9bb",
                    "surface-container-highest": "#313530",
                    "primary-fixed-dim": "#a1d494",
                    "on-tertiary-container": "#ffdad6",
                    "on-primary-fixed": "#002201",
                    "on-tertiary": "#410003",
                    "tertiary-fixed": "#ffdad6",
                    "surface-tint": "#a1d494",
                    "on-primary-fixed-variant": "#23501e",
                    "inverse-on-surface": "#1a1c1a",
                    "primary-container": "#23501e",
                    "primary-fixed": "#bcf0ae",
                    "surface-dim": "#111411",
                    "surface-container-high": "#262b26",
                    "secondary-fixed-dim": "#a5c8ff",
                    "outline-variant": "#42493e",
                    "surface-container": "#1e221e",
                    "on-surface": "#e2e3de",
                    "error": "#ffb4ab",
                    "on-background": "#e2e3de",
                    "on-primary": "#043907",
                    "primary": "#a1d494"
                }
            }
        }
    }
</script>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
<style>
/* UI/UX Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); filter: blur(4px); }
    to { opacity: 1; transform: translateY(0); filter: blur(0); }
}
.animate-enter { animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; }
.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }

/* MD3 Tokens & Global resets */
:root {
    --primary: #a1d494;
    --primary-container: #23501e;
    --on-primary-container: #9dd090;
    --surface-container-low: #1a1c1a;
    --surface-container-lowest: #0a0c0a;
    --surface-container-highest: #2b2f2a;
    --error-container: #93000a;
    --on-error-container: #ffdad6;
    --tertiary-container: #79000b;
    --on-tertiary-container: #ffdad6;
    --outline-variant: rgba(66,73,62,0.3);
    --on-surface-variant: #c2c9bb;
    --on-surface: #e2e3de;
}

*, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; letter-spacing: -0.01em; }
h1, h2, h3, h4, .font-headline { font-family: 'Manrope', sans-serif !important; letter-spacing: -0.02em; }
.font-mono { font-family: 'JetBrains Mono', monospace !important; }

/* Material Symbols Globals */
.material-symbols-outlined {
    font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
}

/* App background */
.stApp { 
    background-color: #0e110e !important; 
    background-image: radial-gradient(rgba(161, 212, 148, 0.05) 1px, transparent 1px) !important;
    background-size: 24px 24px !important;
}

/* Hide default Streamlit decoration and footer, but KEEP header visible for the sidebar toggle */
#MainMenu, footer, [data-testid="stDecoration"] { visibility: hidden !important; }
header[data-testid="stHeader"] { background: transparent !important; color: transparent !important; }
/* Keep the sidebar toggle button (chevron) visible */
header[data-testid="stHeader"] button { visibility: visible !important; color: var(--on-surface) !important; }

.block-container { padding: 2rem 3rem 4rem !important; max-width: 1200px !important; margin: 0 auto; }

/* Sidebar Navigation Fix */
[data-testid="stSidebar"] {
    background-color: var(--surface-container-low) !important;
    border-right: 1px solid var(--outline-variant) !important;
}

/* Streamlit Radio Buttons (Sidebar Menu Styling) */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--on-surface-variant) !important;
    padding: 0.75rem 1rem !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    margin-bottom: 4px !important;
    border: 1px solid transparent !important;
    display: flex !important;
    align-items: center !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background-color: var(--surface-container-highest) !important;
    color: var(--on-surface) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radio"][aria-checked="true"] {
    background-color: var(--primary-container) !important;
    border: 1px solid rgba(161,212,148,0.2) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radio"][aria-checked="true"] p {
    color: var(--on-primary-container) !important;
    font-weight: 700 !important;
}
/* Hide the default radio circle entirely */
[data-testid="stSidebar"] [data-testid="stRadio"] div[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

/* Metric styling */
[data-testid="stMetric"] {
    background: var(--surface-container-lowest) !important;
    border: 1px solid var(--outline-variant) !important;
    border-radius: 16px !important;
}

/* Alert boxes */
.alert-critical {
    background: var(--error-container) !important;
    border-left: 4px solid #ffb4ab !important;
    color: var(--on-error-container) !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.alert-warning {
    background: var(--tertiary-container) !important;
    border-left: 4px solid #ffb3ac !important;
    color: var(--on-tertiary-container) !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    margin-bottom: 1rem !important;
}

/* Plot status cards */
.plot-card {
    background: var(--surface-container-lowest) !important;
    border: 1px solid var(--outline-variant) !important;
    border-radius: 20px !important;
    padding: 1.75rem !important;
    transition: transform 0.3s ease, border-color 0.3s ease;
}
.plot-card:hover { border-color: var(--primary); transform: translateY(-4px); }
.plot-card-critical { border-left: 4px solid #ffb4ab !important; }
.plot-card-warning  { border-left: 4px solid #ffb3ac !important; }
.plot-card-ok       { border-left: 4px solid var(--primary) !important; }

/* Gradient buttons for Sidebar */
div[data-testid="stSidebar"] .stDownloadButton button {
    background: linear-gradient(135deg, var(--primary-container), #a1d494) !important;
    color: #1a1c1a !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    padding: 0.75rem 1rem !important;
    font-size: 13px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
div[data-testid="stSidebar"] .stDownloadButton button:hover {
    filter: brightness(1.1);
    transform: scale(1.02) !important;
}

/* Section label in sidebar */
.sb-sidebar-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #42493e;
    margin-bottom: 0.75rem;
    padding-left: 0.5rem;
}

/* Chatbot styles */
[data-testid="stChatMessage"] {
    background: var(--surface-container-low) !important;
    border: 1px solid var(--outline-variant) !important;
    border-radius: 16px !important;
}

/* Section typography */
.section-label { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:2px; color:var(--primary); margin-bottom:0.25rem; }
.section-title { font-family:'Manrope',sans-serif; font-size:2.25rem; font-weight:800; color:var(--on-surface); line-height:1.1; margin-bottom:0.5rem; }
.section-subtitle { font-size:1rem; color:var(--on-surface-variant); max-width:560px; line-height:1.6; margin-bottom:2rem; }
.divider { border:none; border-top:1px solid var(--outline-variant); margin:2rem 0; }

/* Insight box */
.insight-box {
    background: var(--surface-container-low);
    border-left: 4px solid #f59e0b;
    border-radius: 0 16px 16px 0;
    padding: 1.5rem;
}

/* Action cards */
.action-card {
    background: var(--surface-container-lowest);
    border: 1px solid var(--outline-variant);
    border-radius: 16px;
    padding: 1.75rem;
    transition: transform 0.2s ease;
}
.action-card:hover { transform: translateY(-2px); }
.action-critical { border-left: 4px solid #ffb4ab !important; }
.action-short { border-left: 4px solid #a5c8ff !important; }

/* Metric label */
.plot-metric-label {
    font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:#42493e; margin-bottom:0.25rem;
}
</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ──────────────────────────────────────────────
@st.cache_data
def load_data(uploaded_file=None):
    try:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        else:
            if os.path.exists("plantation_soil_data.xlsm"):
                df = pd.read_excel("plantation_soil_data.xlsm")
            else:
                return pd.DataFrame()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()

def generate_csv_report(df):
    """Generates the full historical dataset as a CSV for export."""
    return df.to_csv(index=False).encode('utf-8')


import io

@st.cache_data
def compute_stats(df_json):
    df = pd.read_json(io.StringIO(df_json))
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    stats = {}
    for plot in df["plot_id"].unique():
        p = df[df["plot_id"] == plot].sort_values("timestamp")
        last = p.iloc[-1]
        m = float(last["soil_moisture_pct"])
        ec = float(last["soil_ec_ds_m"])
        ph = float(last["soil_ph"])
        # Worst values seen in the week
        min_m  = float(p["soil_moisture_pct"].min())
        max_ec = float(p["soil_ec_ds_m"].max())
        min_ph = float(p["soil_ph"].min())

        if m < WILTING_POINT or max_ec > EC_STRESS or min_ph < PH_ACID:
            status = "STRESSED"
        elif m < WILTING_POINT * 1.5 or ec > EC_STRESS * 0.75 or ph < (PH_ACID + 0.5):
            status = "WARNING"
        else:
            status = "OPTIMAL"

        stats[plot] = {
            "moisture": round(m, 1), "ec": round(ec, 2), "ph": round(ph, 2),
            "temp": round(float(last["soil_temp_c"]), 1),
            "min_moisture": round(min_m, 1), "max_ec": round(max_ec, 2),
            "min_ph": round(min_ph, 2), "status": status,
        }
    stats["total_rainfall"] = round(float(df["rainfall_mm"].sum()), 1)
    stats["total_irrigation"] = round(float(df["irrigation_mm"].sum()), 1)
    return stats


# ── GEMINI SETUP ─────────────────────────────────────────────
GEMINI_SYSTEM_PROMPT_TEMPLATE = """You are the AI Farm Assistant for 'Precision Earth', an IoT-based plantation soil health monitoring system.
You help non-expert farm managers understand their soil data in plain English.

CURRENT FARM STATUS (Jan 7, 2025 latest readings):
Plot 1 (North Valley): Moisture {m1}% | EC {ec1} dS/m | pH {ph1} | STATUS: {s1} | Week low: {ml1}% | Peak EC: {mec1} dS/m
Plot 2 (Ridge Side):   Moisture {m2}% | EC {ec2} dS/m | pH {ph2} | STATUS: {s2} | Week low pH: {mph2}
Plot 3 (River Basin):  Moisture {m3}% | EC {ec3} dS/m | pH {ph3} | STATUS: {s3}

CRITICAL: Total irrigation this week = {irr}mm (system OFFLINE). Total rainfall = {rain}mm.

NORMAL RANGES for silty soil crops:
- Soil Moisture: 10-35% (below 10=wilting, above 35=waterlogged)
- EC: 0.5-2.0 dS/m (above 4.0 = toxic salt stress)
- pH: 5.5-7.5 (below 5.5=acid burn, above 7.5=nutrient lockout)

Answer in 3-5 sentences max. Use simple language. Always recommend a concrete action."""


def get_gemini_client():
    if SDK_VERSION == "new":
        return genai.Client(api_key=GEMINI_API_KEY)
    elif SDK_VERSION == "legacy":
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.GenerativeModel('gemini-2.5-flash')
    return None


def build_system_prompt(stats):
    return GEMINI_SYSTEM_PROMPT_TEMPLATE.format(
        m1=stats['Plot1']['moisture'], ec1=stats['Plot1']['ec'], ph1=stats['Plot1']['ph'],
        s1=stats['Plot1']['status'], ml1=stats['Plot1']['min_moisture'], mec1=stats['Plot1']['max_ec'],
        m2=stats['Plot2']['moisture'], ec2=stats['Plot2']['ec'], ph2=stats['Plot2']['ph'],
        s2=stats['Plot2']['status'], mph2=stats['Plot2']['min_ph'],
        m3=stats['Plot3']['moisture'], ec3=stats['Plot3']['ec'], ph3=stats['Plot3']['ph'],
        s3=stats['Plot3']['status'],
        irr=stats['total_irrigation'], rain=stats['total_rainfall'],
    )


# ── MAIN ──────────────────────────────────────────────────────
def main():
    with st.sidebar:
        # ── LOGO ──
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:2.5rem;padding:0.5rem">
            <div style="width:40px;height:40px;background:#a1d494;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#043907">
                <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">agriculture</span>
            </div>
            <div>
                <div style="font-family:'Manrope',sans-serif;font-weight:800;font-size:16px;color:#e2e3de;line-height:1.1">The Precision Earth</div>
                <div style="font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#42493e;font-weight:700">Silty Soil Monitor</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── NAVIGATION ──
        active_tab = st.radio(
            "Navigation",
            options=["📊  Executive Overview", "📈  Historical Trends", "⚡  Action Center", "🚀  Future Upgrades"],
            label_visibility="collapsed"
        )

        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

        # ── DATA MANAGEMENT ──
        st.markdown('<div class="sb-sidebar-label">Data Management</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload plantation telemetry", 
            type=["csv", "xlsx", "xlsm"], 
            label_visibility="collapsed",
            help="Upload the latest soil telemetry spreadsheet"
        )
        if uploaded_file is None:
            st.markdown('<div style="font-size:11px;color:#c2c9bb;padding:0 0.5rem;opacity:0.7">Using default: plantation_soil_data.xlsm</div>', unsafe_allow_html=True)

    df = load_data(uploaded_file)
    if df.empty:
        st.error("No data loaded. Please upload a dataset or ensure plantation_soil_data.xlsm is in the working directory.")
        return

    stats = compute_stats(df.to_json())

    with st.sidebar:
        st.markdown("<div style='flex-grow:1'></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border:none;border-top:1px solid rgba(66,73,62,0.2);margin:1.5rem 0'>", unsafe_allow_html=True)
        
        csv_data = generate_csv_report(df)
        st.download_button(
            label="📥  Export Soil Report",
            data=csv_data,
            file_name="full_telemetry_report.csv",
            mime="text/csv",
        )

        # ── FOOTER LINKS ──
        st.markdown("""
        <div style="padding:0.5rem;margin-top:0.5rem">
            <a href="#" style="display:flex;align-items:center;gap:12px;color:#c2c9bb;text-decoration:none;font-size:13px;margin-bottom:0.75rem">
                <span class="material-symbols-outlined" style="font-size:18px">help</span> Support
            </a>
            <a href="#" style="display:flex;align-items:center;gap:12px;color:#c2c9bb;text-decoration:none;font-size:13px">
                <span class="material-symbols-outlined" style="font-size:18px">logout</span> Sign Out
            </a>
        </div>
        """, unsafe_allow_html=True)

    # ── HEADER RENDERING ─────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 2rem;">
        <div>
            <span style="font-size:10px; font-weight:700; letter-spacing:0.2em; color:var(--on-surface-variant); text-transform:uppercase; margin-bottom:0.5rem; display:block;">Live Dashboard</span>
            <h1 style="font-size: 2.25rem; font-weight: 800; color: var(--on-surface); margin:0; line-height:1;">{active_tab.replace('📊 ', '').replace('📈 ', '').replace('⚡ ', '').replace('🚀 ', '')}</h1>
        </div>
        <div style="display:flex; align-items:center; gap:8px; padding: 0.5rem 1rem; background:var(--surface-container-lowest); border:1px solid var(--outline-variant); border-radius:999px;">
            <div style="width:8px; height:8px; background-color:#ffb4ab; border-radius:50%; animation: pulse 2s infinite;"></div>
            <span style="font-size:12px; font-weight:700; color:var(--on-surface-variant);">LIVE MONITORING ACTIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── PAGE RENDERING ──────────────────────────────────────────
    if "Executive Overview" in active_tab:
        render_overview(df, stats)
    elif "Historical Trends" in active_tab:
        render_trends(df, stats)
    elif "Action Center" in active_tab:
        render_actions(stats)
    elif "Future Upgrades" in active_tab:
        render_upgrades()


# ── TAB 1: EXECUTIVE OVERVIEW ─────────────────────────────────
@st.dialog("Detailed Plot Analytics")
def show_plot_details(plot_id, plot_label, df, s):
    st.markdown(f"## {plot_id}: {plot_label}")
    st.markdown(f"**Current Status:** {s['status']}")
    
    p_df = df[df["plot_id"] == plot_id].copy()
    if p_df.empty:
        st.warning("No historical data available for this plot.")
        return
        
    p_df["date"] = p_df["timestamp"].dt.date
    daily = p_df.groupby("date").agg(
        moisture=("soil_moisture_pct", "mean"),
        ec=("soil_ec_ds_m", "mean"),
        ph=("soil_ph", "mean")
    ).reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["moisture"], name="Moisture %", line=dict(color="#a1d494", width=3)), secondary_y=False)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["ec"], name="EC (dS/m)", line=dict(color="#ffb4ab", width=2, dash="dot")), secondary_y=True)
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#c2c9bb", size=11),
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(title_text="Moisture (%)", secondary_y=False, showgrid=True, gridcolor="rgba(66,73,62,0.2)")
    fig.update_yaxes(title_text="EC (dS/m)", secondary_y=True, showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"**7-Day Summary:** Peak EC was {s['max_ec']} dS/m. Minimum moisture was {s['min_moisture']}%.")

def render_overview(df, stats):
    # Header
    st.markdown('<div class="section-label">Live Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Executive Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Non-expert soil health summary — real-time telemetry</div>', unsafe_allow_html=True)

    # ── CRITICAL ALERTS ──
    st.markdown("### 🚨 Active System Alerts")
    if stats["total_irrigation"] == 0:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:16px;padding:1.25rem;background:var(--error-container);color:var(--on-error-container);border-radius:12px;border-left:4px solid #ffb4ab;margin-bottom:0.75rem;box-shadow:0 4px 12px rgba(0,0,0,0.2)">
            <span style="font-size:24px">🚨</span>
            <div style="flex:1">
                <div style="font-weight:700;font-size:14px;letter-spacing:-0.01em">CRITICAL: Irrigation System Offline (0mm)</div>
                <div style="font-size:12px;opacity:0.8;margin-top:2px">Hardware failure detected. No water delivered despite scheduled cycles. Manual override required.</div>
            </div>
            <span style="font-size:11px;font-weight:700;text-decoration:underline;text-underline-offset:3px;cursor:pointer;white-space:nowrap">ACTION REQUIRED</span>
        </div>""", unsafe_allow_html=True)

    alert_triggered = False
    for plot in sorted(df["plot_id"].unique()):
        s = stats[plot]
        if s["min_moisture"] < WILTING_POINT:
            alert_triggered = True
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:16px;padding:1.25rem;background:var(--error-container);color:var(--on-error-container);border-radius:12px;border-left:4px solid #ffb4ab;margin-bottom:0.75rem;box-shadow:0 4px 12px rgba(0,0,0,0.2)">
                <span style="font-size:24px">⚠️</span>
                <div style="flex:1">
                    <div style="font-weight:700;font-size:14px">CRITICAL: {plot} Drought &amp; Salinity Stress ({s['min_moisture']}% Moisture, {s['max_ec']} dS/m EC)</div>
                    <div style="font-size:12px;opacity:0.8;margin-top:2px">Root zone moisture below survival threshold. Salinity spike detected.</div>
                </div>
                <span style="font-size:11px;font-weight:700;text-decoration:underline;text-underline-offset:3px;cursor:pointer;white-space:nowrap">VIEW MAP</span>
            </div>""", unsafe_allow_html=True)

        if s["min_ph"] < PH_ACID:
            alert_triggered = True
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:16px;padding:1.25rem;background:var(--tertiary-container);color:var(--on-tertiary-container);border-radius:12px;border-left:4px solid #ffb3ac;margin-bottom:0.75rem">
                <span style="font-size:24px">🧪</span>
                <div style="flex:1">
                    <div style="font-weight:700;font-size:14px">WARNING: {plot} Acidity Dip (pH {s['min_ph']})</div>
                    <div style="font-size:12px;opacity:0.8;margin-top:2px">Nitrogen-induced acidification trending downwards. Immediate liming recommended.</div>
                </div>
                <span style="font-size:11px;font-weight:700;text-decoration:underline;text-underline-offset:3px;cursor:pointer;white-space:nowrap">SCHEDULE LIMING</span>
            </div>""", unsafe_allow_html=True)

    if not alert_triggered and stats["total_irrigation"] > 0:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:16px;padding:1.25rem;background:var(--primary-container);color:var(--on-primary-container);border-radius:12px;border-left:4px solid #a1d494;margin-bottom:0.75rem">
            <span style="font-size:24px">✅</span>
            <div style="flex:1">
                <div style="font-weight:700;font-size:14px">All Systems Nominal</div>
                <div style="font-size:12px;opacity:0.8;margin-top:2px">No critical alerts detected in the current telemetry window.</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── PLOT STATUS CARDS ──
    st.markdown("### 🗺️ Plot Status Monitor")
    st.markdown("<p style='color:var(--on-surface-variant); font-size:14px; margin-bottom:1.5rem;'>Live telemetry from edge sensors.</p>", unsafe_allow_html=True)
    
    cols = st.columns(3, gap="large")

    for i, plot in enumerate(sorted(df["plot_id"].unique())):
        s = stats[plot]
        # Match Tailwind semantic colors to status
        css_cls = {"STRESSED":"error","WARNING":"tertiary","OPTIMAL":"primary"}[s["status"]]
        
        with cols[i]:
            delay = (i + 1) * 100
            st_html(f"""
            <div class="animate-enter delay-{delay} bg-surface-container-lowest/80 backdrop-blur-md p-6 rounded-2xl border border-outline-variant/20 hover:border-primary/50 hover:bg-surface-container-low relative group shadow-sm hover:shadow-lg transition-all duration-300 h-full flex flex-col justify-between" style="transform:translateZ(0)">
                <div class="absolute left-0 top-1/4 bottom-1/4 w-1 bg-{css_cls} rounded-r-full group-hover:h-3/4 group-hover:top-[12.5%] transition-all duration-300 ease-out"></div>
                <div>
                    <div class="flex justify-between items-start mb-6 pl-2">
                        <span class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">{plot}</span>
                        <span class="bg-{css_cls}-container/40 text-{css_cls} px-2 py-0.5 rounded text-[10px] font-bold border border-{css_cls}/20 tracking-wide">{s['status']}</span>
                    </div>
                    <div class="mb-4 pl-2">
                        <h4 class="text-[2.75rem] font-extrabold text-{css_cls} mb-0 leading-none" style="font-family: 'JetBrains Mono', monospace;">{s['moisture']}<span class="text-base font-medium text-on-surface-variant ml-1">%</span></h4>
                        <p class="text-[11px] font-semibold text-on-surface-variant mt-2 uppercase tracking-wide">Volumetric Water Content</p>
                    </div>
                </div>
                
                <div class="mt-4 pt-4 border-t border-outline-variant/20 pl-2">
                    <div class="grid grid-cols-2 gap-y-3 gap-x-2 text-xs">
                        <div><span class="text-on-surface-variant font-medium">EC:</span> <span class="font-bold text-on-surface ml-1">{s['ec']} dS/m</span></div>
                        <div><span class="text-on-surface-variant font-medium">pH:</span> <span class="font-bold text-on-surface ml-1">{s['ph']}</span></div>
                        <div><span class="text-on-surface-variant font-medium">Temp:</span> <span class="font-bold text-on-surface ml-1">{s['temp']}°C</span></div>
                        <div><span class="text-on-surface-variant font-medium">Min:</span> <span class="font-black text-error ml-1">{s['min_moisture']}%</span></div>
                    </div>
                </div>
            </div>
            """)
            if st.button(f"🔍 View {plot} Details", key=f"btn_pop_{plot}", use_container_width=True):
                show_plot_details(plot, plot, df, s)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── AI CHATBOT ──
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem">
        <div style="width:40px;height:40px;background:rgba(45,90,39,0.4);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px">🤖</div>
        <div>
            <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:18px;color:#e2e3de">AI Farm Assistant</div>
            <div style="font-size:12px;color:#42493e">Powered by Google Gemini · Ask anything about your soil</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Init chat history + gemini client
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "gemini_client" not in st.session_state:
        st.session_state.gemini_client = get_gemini_client()
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = build_system_prompt(stats)

    # Display existing messages
    if not st.session_state.chat_history:
        with st.chat_message("assistant", avatar="🌱"):
            st.markdown("**Hello, Farm Manager!** I've analysed your sensor data. Plot 1 is your priority — moisture dropped to 1.0% this week and salt levels are dangerously high. The irrigation system has also recorded **zero output** for 7 days. Ask me anything about what's happening in your plots.")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🌱"):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask about soil health, irrigation, or what action to take..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🌱"):
            with st.spinner("..."):
                try:
                    # Build conversation history for multi-turn chat
                    if SDK_VERSION == "new":
                        contents = []
                        for msg in st.session_state.chat_history:
                            role = "user" if msg["role"] == "user" else "model"
                            contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
    
                        response = st.session_state.gemini_client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=contents,
                            config=types.GenerateContentConfig(
                                system_instruction=st.session_state.system_prompt,
                                max_output_tokens=1000,
                            ),
                        )
                        reply = response.text
                    elif SDK_VERSION == "legacy":
                        # Simple single-turn for legacy fallback to keep it robust
                        chat = st.session_state.gemini_client.start_chat(history=[])
                        full_prompt = f"{st.session_state.system_prompt}\n\nUser: {prompt}"
                        response = chat.send_message(full_prompt)
                        reply = response.text
                    else:
                        reply = "⚠️ Gemini library not installed."
                except Exception as e:
                    reply = f"⚠️ Gemini API error: {e}"
            st.markdown(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})


# ── TAB 2: HISTORICAL TRENDS ──────────────────────────────────
def render_trends(df, stats):
    st.markdown('<div class="section-label">Telemetry Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Historical Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Visualizing moisture retention and rainfall correlation — Jan 1–7, 2025</div>', unsafe_allow_html=True)

    # ── DUAL-AXIS CHART ──
    col_chart, col_insight = st.columns([2.5, 1])

    with col_chart:
        st.markdown("#### 💧 Dual-Axis: Soil Moisture vs. Rainfall")
        plot_sel = st.selectbox("Select Plot", ["All Plots", "Plot1", "Plot2", "Plot3"], key="trend_plot")

        df_daily = df.copy()
        df_daily["date"] = df["timestamp"].dt.date
        daily = df_daily.groupby(["date", "plot_id"]).agg(
            moisture=("soil_moisture_pct", "mean"),
            rainfall=("rainfall_mm", "sum"),
        ).reset_index()

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        colors = {"Plot1": "#a1d494", "Plot2": "#a5c8ff", "Plot3": "#ffb3ac"}
        plots_to_show = ["Plot1", "Plot2", "Plot3"] if plot_sel == "All Plots" else [plot_sel]

        # Rainfall bars (secondary y)
        rf_data = daily.groupby("date")["rainfall"].mean().reset_index()
        fig.add_trace(go.Bar(
            x=rf_data["date"], y=rf_data["rainfall"],
            name="Rainfall (mm)", marker_color="rgba(165,200,255,0.4)",
            marker_line_color="rgba(165,200,255,0.8)", marker_line_width=1,
        ), secondary_y=True)

        # Moisture line (primary y)
        for plot in plots_to_show:
            p = daily[daily["plot_id"] == plot]
            fig.add_trace(go.Scatter(
                x=p["date"], y=p["moisture"], name=f"{plot} Moisture",
                mode="lines+markers",
                line=dict(color=colors[plot], width=2.5),
                marker=dict(size=6, color=colors[plot]),
                fill="tozeroy",
                fillcolor=colors[plot].replace(")", ",0.05)").replace("rgb","rgba") if "rgb" in colors[plot] else f"rgba(161,212,148,0.05)",
            ), secondary_y=False)

        # Wilting threshold
        fig.add_hline(y=WILTING_POINT, line_dash="dash", line_color="rgba(255,180,171,0.6)",
                     annotation_text="Wilting Point (10%)", secondary_y=False,
                     annotation_font_color="rgba(255,180,171,0.8)")

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#c2c9bb", size=11),
            legend=dict(orientation="h", x=0, y=1.08, bgcolor="rgba(0,0,0,0)",
                       font=dict(size=11, color="#c2c9bb")),
            margin=dict(l=10, r=10, t=40, b=10),
            height=380,
            xaxis=dict(showgrid=False, zeroline=False, color="#42493e"),
            yaxis=dict(title="Soil Moisture (%)", showgrid=True, gridcolor="rgba(66,73,62,0.2)", zeroline=False),
            yaxis2=dict(title="Rainfall (mm)", showgrid=False, zeroline=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_insight:
        st.markdown("<div style='height:2.5rem'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-box">
            <div style="display:flex;align-items:center;gap:8px;color:#f59e0b;margin-bottom:1rem">
                <span style="font-size:18px">⚠️</span>
                <span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px">Critical Insight</span>
            </div>
            <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:17px;color:#e2e3de;margin-bottom:0.75rem;line-height:1.3">Irrigation Anomaly Detected</div>
            <div style="font-size:13px;color:#c2c9bb;line-height:1.7;margin-bottom:0.75rem">
                The chart reveals a direct dependency on natural rainfall. Moisture levels <strong style="color:#a1d494">only</strong> spike immediately following rainfall bars.
            </div>
            <div style="font-size:13px;color:#c2c9bb;line-height:1.7">
                During dry intervals, there is <strong style="color:#ffb4ab">zero moisture recovery</strong> despite scheduled irrigation cycles — confirming a mechanical failure in the sector pump.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(37,99,235,0.06);border:1px solid rgba(37,99,235,0.2);border-radius:12px;padding:1rem">
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#a5c8ff;margin-bottom:0.5rem">Recommended Action</div>
            <div style="font-size:13px;color:#c2c9bb;line-height:1.6">Deploy field engineer to inspect valve actuators and pressure transducers on the main irrigation controller.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#1a1c1a;border:1px solid rgba(66,73,62,0.3);border-radius:12px;padding:1rem">
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#42493e;margin-bottom:0.75rem">Weekly Summary</div>
            <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(66,73,62,0.2);padding-bottom:0.5rem;margin-bottom:0.5rem">
                <span style="font-size:12px;color:#c2c9bb">Total Rainfall</span>
                <span style="font-size:12px;font-weight:700;color:#a5c8ff">{stats['total_rainfall']} mm</span>
            </div>
            <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(66,73,62,0.2);padding-bottom:0.5rem;margin-bottom:0.5rem">
                <span style="font-size:12px;color:#c2c9bb">Total Irrigation</span>
                <span style="font-size:12px;font-weight:700;color:#ffb4ab">{stats['total_irrigation']} mm</span>
            </div>
            <div style="display:flex;justify-content:space-between">
                <span style="font-size:12px;color:#c2c9bb">Avg Weekly Loss</span>
                <span style="font-size:12px;font-weight:700;color:#a1d494">14.2%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── SOIL STATUS HEATMAP ──
    col_legend, col_heat = st.columns([1, 3])

    with col_legend:
        st.markdown("#### 🗓️ Saturation Lifecycle")
        st.markdown("""
        <div style="margin-top:1rem">
            <p style="font-size:13px;color:#c2c9bb;line-height:1.6;margin-bottom:1rem">
            Daily average soil moisture across all 3 plots. Colour-coded to show drought stress cycles at a glance.
            </p>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.5rem">
                <div style="width:16px;height:16px;background:#a5c8ff;border-radius:3px"></div>
                <div>
                    <div style="font-size:12px;font-weight:700;color:#e2e3de">Wet (&gt;35%)</div>
                    <div style="font-size:10px;color:#42493e">High leaching risk</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.5rem">
                <div style="width:16px;height:16px;background:#a1d494;border-radius:3px"></div>
                <div>
                    <div style="font-size:12px;font-weight:700;color:#e2e3de">Normal (10–35%)</div>
                    <div style="font-size:10px;color:#42493e">Optimal growth zone</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:10px">
                <div style="width:16px;height:16px;background:#93000a;border-radius:3px"></div>
                <div>
                    <div style="font-size:12px;font-weight:700;color:#e2e3de">Drought (&lt;10%)</div>
                    <div style="font-size:10px;color:#42493e">Wilting threshold</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_heat:
        st.markdown("#### &nbsp;")
        df_heat = df.copy()
        df_heat["date"] = df_heat["timestamp"].dt.date
        pivot = df_heat.groupby(["plot_id", "date"])["soil_moisture_pct"].mean().reset_index()
        pivot = pivot.pivot(index="plot_id", columns="date", values="soil_moisture_pct")

        def moisture_color(v):
            if v > FIELD_CAPACITY: return 0.0   # wet = blue
            elif v < WILTING_POINT: return 1.0  # drought = red
            else: return 0.5                     # normal = green

        colorscale = [
            [0.0, "#93000a"],   # Drought — red
            [0.5, "#a1d494"],   # Normal — green
            [1.0, "#a5c8ff"],   # Wet — blue
        ]

        fig2 = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[str(c) for c in pivot.columns],
            y=list(pivot.index),
            colorscale=colorscale,
            zmin=0, zmax=45,
            colorbar=dict(
                title=dict(text="Moisture %", font=dict(color="#c2c9bb", size=11)),
                tickvals=[5, 22, 38],
                ticktext=["Drought", "Normal", "Wet"],
                tickfont=dict(color="#c2c9bb", size=10),
            ),
            text=[[f"{v:.1f}%" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            textfont=dict(color="white", size=11),
            hoverongaps=False,
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#c2c9bb", size=11),
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            xaxis=dict(showgrid=False, color="#42493e", tickangle=-30),
            yaxis=dict(showgrid=False, color="#42493e"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── EDITORIAL FOOTER (stitch_new style) ──
    st.markdown(f"""
    <div style="margin-top:2rem;display:flex;justify-content:space-between;align-items:flex-start;border-top:1px solid rgba(66,73,62,0.3);padding-top:2rem">
        <div style="max-width:420px">
            <p style="color:#8d9388;font-size:13px;font-style:italic;line-height:1.7;margin:0">"Historical trends allow us to see through the immediate noise of weather and uncover the underlying mechanical reliability of the plantation's infrastructure."</p>
            <p style="margin-top:0.5rem;color:#c2c9bb;font-weight:700;font-size:11px">— Chief Agronomist Report, Q3</p>
        </div>
        <div style="display:flex;gap:3rem">
            <div>
                <span style="display:block;font-size:2rem;font-weight:900;color:#a1d494;font-family:Manrope,sans-serif">14.2%</span>
                <span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#42493e">Avg. Weekly Loss</span>
            </div>
            <div>
                <span style="display:block;font-size:2rem;font-weight:900;color:#a5c8ff;font-family:Manrope,sans-serif">{stats['total_rainfall']}mm</span>
                <span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#42493e">Total Precip</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── TAB 3: ACTION CENTER ──────────────────────────────────────
def render_actions(stats):
    st.markdown('<div class="section-label">Technician Dispatch</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Action Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Prioritised operational tasks based on real-time soil telemetry</div>', unsafe_allow_html=True)

    # Bento Grid for Tasks
    st_html(f"""
    <div class="grid grid-cols-12 gap-8">
        <!-- CRITICAL TASK: Main Card -->
        <div class="col-span-12 lg:col-span-8">
            <div class="relative overflow-hidden rounded-xl bg-surface-container-lowest p-1 border-l-4 border-error shadow-sm">
                <div class="p-8">
                    <div class="flex justify-between items-start mb-8">
                        <div>
                            <span class="bg-error-container text-on-error-container text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider mb-3 inline-block">Immediate Action Required</span>
                            <h2 class="text-2xl font-bold text-on-surface">Inspect BMS Irrigation Controller & Pumps</h2>
                        </div>
                        <div class="w-12 h-12 rounded-full bg-surface-container-high flex items-center justify-center text-on-surface-variant">
                            <span class="material-symbols-outlined">check_box_outline_blank</span>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-12 mb-8">
                        <div>
                            <p class="text-on-surface-variant text-sm mb-2 font-semibold">Issue Description</p>
                            <p class="text-on-surface leading-relaxed text-sm">System has recorded <span class="text-error font-bold">{stats['total_irrigation']}mm</span> of irrigation for 7 straight days despite scheduled cycles. Potential mechanical failure or signal blockage at the main controller.</p>
                        </div>
                        <div class="flex flex-col justify-end">
                            <div class="bg-surface-container p-4 rounded-lg">
                                <div class="flex items-center justify-between mb-2">
                                    <span class="text-xs font-semibold text-on-surface-variant">System Pressure</span>
                                    <span class="text-xs font-bold text-error">LOW</span>
                                </div>
                                <div class="w-full bg-surface-variant h-1 rounded-full overflow-hidden">
                                    <div class="bg-error h-full w-[8%]"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="flex items-center gap-6 pt-6 border-t border-outline-variant/10">
                        <div class="flex items-center gap-2">
                            <span class="material-symbols-outlined text-on-surface-variant text-lg">location_on</span>
                            <span class="text-sm font-medium">Main Hub - Sector Alpha</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="material-symbols-outlined text-on-surface-variant text-lg">schedule</span>
                            <span class="text-sm font-medium">Due: Immediate</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Stats / Map Sidebar for Context -->
        <div class="col-span-12 lg:col-span-4 space-y-8">
            <div class="bg-surface-container rounded-xl p-6 h-full flex flex-col border border-outline-variant/10">
                <h3 class="font-bold text-on-surface mb-4">Location Context</h3>
                <div class="flex-1 min-h-[160px] rounded-lg overflow-hidden relative mb-4">
                    <img alt="Plantation Grid" class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAwamBr4NotdTh8akat6sQN8tLQzWIZs8n6Oj34eAbJVxQaPOzpLZvgLmPEEX9FsBbdWq1l8Oj5xBnhr0wh-jMdA3vecbSs4XsGR-eQhYkUAAj7KIY0VlSeIsYmHYzhpsY6NUK0Xd9ItLKLafuufRgQw7VIPlPXFe591eGSe6E4eBKNBL5fv0Emt84QL1sY8YHPSQatGYnJ8aMYxQM86lDo7T6NVZOkj6VFQl_-3WcjbEVoZDW2DDfj_vuzujZjeVKP3Yzathm2pOk"/>
                    <div class="absolute inset-0 bg-gradient-to-t from-surface-container to-transparent opacity-60"></div>
                </div>
                <div class="space-y-3">
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-on-surface-variant">Last Pulse</span>
                        <span class="font-mono text-on-surface font-bold">14:02 UTC</span>
                    </div>
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-on-surface-variant">Sensors Online</span>
                        <span class="font-mono text-on-surface font-bold">3/3 (100%)</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Secondary Actions -->
        <div class="col-span-12 grid grid-cols-1 md:grid-cols-2 gap-8 mt-4">
            <!-- Action 2: Plot 1 Flush -->
            <div class="bg-surface-container-low rounded-xl p-8 hover:bg-surface-container transition-all group border border-outline-variant/10">
                <div class="flex justify-between items-start mb-6">
                    <div class="w-12 h-12 rounded bg-secondary-container/20 flex items-center justify-center text-secondary">
                        <span class="material-symbols-outlined">water_drop</span>
                    </div>
                    <div class="w-10 h-10 rounded-full border border-outline-variant/30 flex items-center justify-center text-on-surface-variant group-hover:bg-surface-container-highest transition-colors cursor-pointer">
                        <span class="material-symbols-outlined">check</span>
                    </div>
                </div>
                <span class="text-[10px] font-bold text-secondary uppercase tracking-widest mb-2 block">Short-term Action</span>
                <h3 class="text-xl font-bold text-on-surface mb-3 tracking-tight">Perform Fresh-water Flush on Plot 1</h3>
                <p class="text-on-surface-variant text-sm mb-6 leading-relaxed">
                    Wash accumulated surface salts (<span class="text-on-surface font-bold">{stats['Plot1']['max_ec']} dS/m</span>) back down below the active root zone to prevent osmotic stress.
                </p>
                <div class="flex items-center justify-between pt-4 border-t border-outline-variant/10">
                    <div class="flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full bg-secondary"></div>
                        <span class="text-xs font-bold text-on-surface-variant">Water Team Assigned</span>
                    </div>
                    <span class="text-xs font-bold text-on-surface-variant">Priority: High</span>
                </div>
            </div>

            <!-- Action 3: Plot 2 pH Buffer -->
            <div class="bg-surface-container-low rounded-xl p-8 hover:bg-surface-container transition-all group border border-outline-variant/10">
                <div class="flex justify-between items-start mb-6">
                    <div class="w-12 h-12 rounded bg-tertiary-container/20 flex items-center justify-center text-tertiary">
                        <span class="material-symbols-outlined">science</span>
                    </div>
                    <div class="w-10 h-10 rounded-full border border-outline-variant/30 flex items-center justify-center text-on-surface-variant group-hover:bg-surface-container-highest transition-colors cursor-pointer">
                        <span class="material-symbols-outlined">check</span>
                    </div>
                </div>
                <span class="text-[10px] font-bold text-tertiary uppercase tracking-widest mb-2 block">Short-term Action</span>
                <h3 class="text-xl font-bold text-on-surface mb-3 tracking-tight">Apply pH Buffer (Agricultural Lime)</h3>
                <p class="text-on-surface-variant text-sm mb-6 leading-relaxed">
                    Apply to Plot 2 to neutralize the <span class="text-tertiary font-bold">{stats['Plot2']['min_ph']} acidic dip</span>. Target pH range: 6.2 - 6.8 for optimal nutrient uptake.
                </p>
                <div class="flex items-center justify-between pt-4 border-t border-outline-variant/10">
                    <div class="flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full bg-tertiary"></div>
                        <span class="text-xs font-bold text-on-surface-variant">Chem-Group Required</span>
                    </div>
                    <span class="text-xs font-bold text-on-surface-variant">Priority: Med</span>
                </div>
            </div>
        </div>

        <!-- Footer Stats -->
        <div class="col-span-12 mt-4 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div class="p-6 bg-surface-container-lowest rounded-xl border border-outline-variant/10">
                <p class="text-xs font-bold text-on-surface-variant uppercase mb-4 tracking-widest">Completion Rate</p>
                <div class="flex items-end gap-3">
                    <span class="text-4xl font-extrabold text-primary">82%</span>
                    <span class="text-[10px] text-primary pb-1 font-bold tracking-tight">+4.2% from last week</span>
                </div>
            </div>
            <div class="p-6 bg-surface-container-lowest rounded-xl border border-outline-variant/10">
                <p class="text-xs font-bold text-on-surface-variant uppercase mb-4 tracking-widest">Avg Response Time</p>
                <div class="flex items-end gap-3">
                    <span class="text-4xl font-extrabold text-on-surface">2.4h</span>
                    <span class="text-[10px] text-on-surface-variant pb-1 font-bold">Operational Standard: < 4h</span>
                </div>
            </div>
            <div class="p-6 bg-surface-container-lowest rounded-xl border border-outline-variant/10">
                <p class="text-xs font-bold text-on-surface-variant uppercase mb-4 tracking-widest">Fleet Status</p>
                <div class="flex items-end gap-3">
                    <span class="text-4xl font-extrabold text-on-surface">12/14</span>
                    <span class="text-[10px] text-on-surface-variant pb-1 font-bold uppercase tracking-tight">Technicians Active</span>
                </div>
            </div>
        </div>
    </div>
    """)


# ── TAB 4: FUTURE UPGRADES ────────────────────────────────────
def render_upgrades():
    st.markdown('<div class="section-label">Tier 2 Strategic Expansion</div>', unsafe_allow_html=True)
    st.markdown('<style>.future-title{font-size:clamp(2.5rem,5vw,4rem);font-weight:800;font-family:Manrope,sans-serif;color:#e2e3de;line-height:1.1;margin-bottom:1rem}</style>', unsafe_allow_html=True)
    st.markdown('<div class="future-title">Anticipated<br>Infrastructure.</div>', unsafe_allow_html=True)

    col_desc, col_roi = st.columns([2, 1])
    with col_desc:
        st.markdown("""<div style="font-size:1.1rem;color:#c2c9bb;max-width:560px;line-height:1.7">
            Elevate plantation yield through advanced subsurface monitoring. These upcoming sensor integrations are designed to mitigate risk in high-variability silty soil environments.
        </div>""", unsafe_allow_html=True)
    with col_roi:
        st.markdown("""
        <div style="background:#1a1c1a;border-radius:12px;padding:1.25rem;border-left:4px solid #a1d494">
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#42493e;margin-bottom:4px">ROI Potential</div>
            <div style="font-family:Manrope,sans-serif;font-size:2rem;font-weight:800;color:#e2e3de">+22.4% <span style="font-size:1rem;font-weight:400;color:#42493e">Annual Yield</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    upgrades = [
        ("01", "layers", "Multi-depth Tensiometers", "Precision monitoring at 15cm, 30cm, and 60cm depths. Essential for tracking vertical water migration in silt-heavy soil compositions to determine if drought is surface-level or killing deep roots.", "$1,240", "15%", "$18,500", "85%", "Premium Upgrade Only"),
        ("02", "opacity", "Drainage Lysimeters", "Volumetric measurement of water percolating through the soil profile. Definitively proves or disproves the capillary rise hypothesis by tracking salt moving upward vs. downward.", "$4,800", "25%", "$32,000", "90%", "Unlocks in Q3"),
        ("03", "speed", "Automated Flow Totalizers", "Real-time irrigation flow monitoring on all water mains. Determines if the irrigation failure is a software signal issue or a physical pipe blockage — answers the 'why' behind zero irrigation output.", "$2,100", "20%", "$24,500", "78%", "Hardware Pending"),
    ]

    cols = st.columns(3)
    for i, (num, icon, title, desc, cost, cost_w, loss, loss_w, badge) in enumerate(upgrades):
        with cols[i]:
            st_html(f"""
            <div style="background:#111411;border-radius:16px;padding:1.5rem;border:1px solid rgba(66,73,62,0.3);position:relative;overflow:hidden;min-height:380px">
                <!-- Locked overlay -->
                <div style="position:absolute;inset:0;background:rgba(14,17,14,0.75);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:10;border-radius:16px;backdrop-filter:blur(2px)">
                    <div style="font-size:2rem;margin-bottom:0.5rem">🔒</div>
                    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#c2c9bb">{badge}</div>
                </div>
                <!-- Card content (blurred underneath) -->
                <div style="filter:blur(1px);opacity:0.4">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:3rem">
                        <div style="width:48px;height:48px;background:rgba(66,73,62,0.3);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.5rem">📡</div>
                        <span style="font-family:Manrope,sans-serif;font-size:2.5rem;font-weight:800;color:rgba(66,73,62,0.5)">{num}</span>
                    </div>
                    <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:1.3rem;color:#42493e;margin-bottom:0.75rem">{title}</div>
                    <div style="font-size:12px;color:#313530;line-height:1.6;margin-bottom:1.5rem">{desc}</div>
                    <div style="background:#0c0e0c;border-radius:8px;padding:1rem">
                        <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px">
                            <span style="color:#42493e;text-transform:uppercase;font-weight:700">Unit Cost</span>
                            <span style="color:#313530;font-family:monospace">{cost}</span>
                        </div>
                        <div style="background:rgba(66,73,62,0.2);border-radius:4px;height:4px;overflow:hidden;margin-bottom:0.75rem">
                            <div style="background:#a5c8ff;height:100%;width:{cost_w}"></div>
                        </div>
                        <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px">
                            <span style="color:#42493e;text-transform:uppercase;font-weight:700">Potential Crop Loss</span>
                            <span style="color:#93000a;font-family:monospace;font-weight:700">{loss}</span>
                        </div>
                        <div style="background:rgba(66,73,62,0.2);border-radius:4px;height:4px;overflow:hidden">
                            <div style="background:#93000a;height:100%;width:{loss_w}"></div>
                        </div>
                    </div>
                </div>
            </div>
            """)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Cost of inaction section
    col_text, col_visual = st.columns([1, 1.5])
    with col_text:
        st.markdown("""
        <div style="font-family:Manrope,sans-serif;font-size:2rem;font-weight:700;color:#e2e3de;margin-bottom:1rem">The Cost of Inaction</div>
        <div style="font-size:13px;color:#c2c9bb;line-height:1.7;margin-bottom:1.5rem">
            Data gaps in plantation management aren't just technical oversights — they represent direct financial leakage. By integrating Tier 2 sensors, ROI is realised within the first 14 months through precision irrigation and nutrient retention.
        </div>
        """, unsafe_allow_html=True)
        for item in ["Predictive Osmotic Pressure Modelling", "AI-Driven Capillary Break Detection", "Automated Nutrient Leaching Alerts"]:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:0.5rem">
                <div style="width:28px;height:28px;border-radius:50%;border:1px solid rgba(66,73,62,0.4);display:flex;align-items:center;justify-content:center;font-size:12px;color:#42493e">✓</div>
                <span style="font-size:13px;color:#c2c9bb">{item}</span>
            </div>""", unsafe_allow_html=True)

    with col_visual:
        # Simple cost comparison bar chart
        fig = go.Figure()
        categories = ["Multi-depth\nTensiometers", "Drainage\nLysimeters", "Flow\nTotalizers"]
        costs  = [1240, 4800, 2100]
        losses = [18500, 32000, 24500]

        fig.add_trace(go.Bar(name="Sensor Cost ($)", x=categories, y=costs,
                            marker_color="rgba(165,200,255,0.7)", marker_line_color="#a5c8ff",
                            marker_line_width=1))
        fig.add_trace(go.Bar(name="Crop Loss Risk ($)", x=categories, y=losses,
                            marker_color="rgba(147,0,10,0.6)", marker_line_color="#ffb4ab",
                            marker_line_width=1))
        fig.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#c2c9bb", size=11),
            legend=dict(orientation="h", x=0, y=1.05, bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=10, t=40, b=10),
            height=280,
            xaxis=dict(showgrid=False, color="#42493e"),
            yaxis=dict(showgrid=True, gridcolor="rgba(66,73,62,0.2)", color="#42493e",
                      tickprefix="$", tickformat=",.0f"),
        )
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
