import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google import genai
from google.genai import types
import os

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Precision Earth | Soil Health Monitor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CONSTANTS ─────────────────────────────────────────────────
GEMINI_API_KEY = "AIzaSyBXQZwWuXX0vf6HQBTBXoFcCs3ZkGux23M"
WILTING_POINT = 10.0
FIELD_CAPACITY = 35.0
EC_STRESS = 4.0
PH_ACID = 5.5
PH_ALK  = 7.5

# ── GLOBAL CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

/* Global reset */
*, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; }
h1, h2, h3, h4 { font-family: 'Manrope', sans-serif !important; }

/* App background */
.stApp { background-color: #0e110e !important; }

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 100% !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111411 !important;
    border-right: 1px solid rgba(66,73,62,0.4) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1rem !important; }

/* Sidebar radio (nav) */
[data-testid="stSidebar"] .stRadio > label { display: none !important; }
[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
[data-testid="stSidebar"] .stRadio > div > label {
    width: 100% !important;
    padding: 0.65rem 1rem !important;
    border-radius: 8px !important;
    color: #c2c9bb !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(66,73,62,0.5) !important;
    color: #e2e3de !important;
}
[data-testid="stSidebar"] .stRadio > div > label[data-testid="stMarkdownContainer"] span { display: none !important; }
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + label,
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"] input:checked ~ div {
    background: rgba(45,90,39,0.5) !important;
    color: #a1d494 !important;
}
/* Force radio buttons hidden */
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; }

/* Metric styling */
[data-testid="stMetric"] {
    background: #1a1c1a !important;
    border: 1px solid rgba(66,73,62,0.3) !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
}
[data-testid="stMetricLabel"] { color: #c2c9bb !important; font-size: 10px !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 1.5px !important; }
[data-testid="stMetricValue"] { color: #a1d494 !important; font-family: 'Manrope', sans-serif !important; font-weight: 800 !important; }
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* Chat messaging */
[data-testid="stChatMessage"] {
    background: #1e221e !important;
    border: 1px solid rgba(66,73,62,0.3) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    background: #111411 !important;
    border: 1px solid rgba(66,73,62,0.5) !important;
    color: #e2e3de !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #42493e !important; }

/* Alert boxes */
.alert-critical {
    background: rgba(147,0,10,0.25) !important;
    border-left: 4px solid #ffb4ab !important;
    border-radius: 0 12px 12px 0 !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.75rem !important;
    color: #ffdad6 !important;
}
.alert-warning {
    background: rgba(121,0,11,0.2) !important;
    border-left: 4px solid #ffb3ac !important;
    border-radius: 0 12px 12px 0 !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.75rem !important;
    color: #ffb3ac !important;
}
.alert-ok {
    background: rgba(45,90,39,0.25) !important;
    border-left: 4px solid #a1d494 !important;
    border-radius: 0 12px 12px 0 !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.75rem !important;
    color: #a1d494 !important;
}

/* Plot status cards */
.plot-card {
    background: #111411 !important;
    border: 1px solid rgba(66,73,62,0.25) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    position: relative !important;
    overflow: hidden !important;
    height: 100% !important;
}
.plot-card-critical { border-left: 4px solid #ffb4ab !important; }
.plot-card-warning  { border-left: 4px solid #ffb3ac !important; }
.plot-card-ok       { border-left: 4px solid #a1d494 !important; }
.plot-badge-critical { background: rgba(147,0,10,0.3); color: #ffb4ab; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.plot-badge-warning  { background: rgba(164,2,19,0.3); color: #ffb3ac; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.plot-badge-ok       { background: rgba(45,90,39,0.4);  color: #a1d494; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.plot-metric-val { font-size: 3rem; font-weight: 800; font-family: 'Manrope', sans-serif; color: #a1d494; line-height: 1; }
.plot-metric-unit { font-size: 1rem; font-weight: 400; color: #c2c9bb; margin-left: 4px; }
.plot-metric-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #42493e; margin-bottom: 0.5rem; }

/* Action cards */
.action-card {
    background: #1a1c1a !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    margin-bottom: 1rem !important;
    border: 1px solid rgba(66,73,62,0.3) !important;
}
.action-critical { border-left: 4px solid #ffb4ab !important; }
.action-short    { border-left: 4px solid #a5c8ff !important; }

/* Upgrade locked cards */
.upgrade-card {
    background: #111411;
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(66,73,62,0.3);
    position: relative;
    overflow: hidden;
    filter: brightness(0.7);
}
.lock-overlay {
    position: absolute; inset: 0;
    background: rgba(14,17,14,0.75);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    border-radius: 16px;
}

/* Section headers */
.section-label {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 2px; color: #a1d494; margin-bottom: 4px;
}
.section-title {
    font-size: 2.25rem; font-weight: 800; color: #e2e3de;
    font-family: 'Manrope', sans-serif; margin-bottom: 0.5rem;
}
.section-subtitle { font-size: 1rem; color: #c2c9bb; margin-bottom: 1.5rem; }

/* Divider */
.divider { border: none; border-top: 1px solid rgba(66,73,62,0.3); margin: 1.5rem 0; }

/* Insight callout */
.insight-box {
    background: rgba(29,34,30,0.8);
    border: 1px solid rgba(161,212,148,0.2);
    border-left: 4px solid #a1d494;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem;
}

/* Plotly chart containers */
.stPlotlyChart { border-radius: 16px !important; overflow: hidden !important; }

/* Selectbox */
[data-testid="stSelectbox"] { color: #e2e3de !important; }
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

def generate_csv_report(stats):
    report = []
    for plot in ["Plot1", "Plot2", "Plot3"]:
        if plot in stats:
            row = {"Plot": plot}
            row.update(stats[plot])
            report.append(row)
    
    # Add a system summary row
    report.append({
        "Plot": "SYSTEM TOTAL",
        "moisture": "", "ec": "", "ph": "", "temp": "",
        "min_moisture": f"Rainfall: {stats.get('total_rainfall', 0)}mm",
        "max_ec": f"Irrigation: {stats.get('total_irrigation', 0)}mm",
        "min_ph": "", "status": ""
    })
    
    return pd.DataFrame(report).to_csv(index=False).encode('utf-8')


@st.cache_data
def compute_stats(df_json):
    df = pd.read_json(df_json)
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
    return genai.Client(api_key=GEMINI_API_KEY)


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
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:2rem">
            <div style="width:40px;height:40px;background:rgba(45,90,39,0.5);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:20px">🌱</div>
            <div>
                <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:15px;color:#a1d494">The Precision Earth</div>
                <div style="font-size:10px;text-transform:uppercase;letter-spacing:2px;color:#42493e;font-weight:600">Silty Soil Monitor</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab = st.radio(
            "Navigation",
            ["📊  Executive Overview", "📈  Historical Trends", "⚡  Action Center", "🚀  Future Upgrades"],
            label_visibility="collapsed",
        )
        active_tab = tab.split("  ")[1].strip()

        st.markdown("<hr style='border:none;border-top:1px solid rgba(66,73,62,0.3);margin:1.5rem 0'>", unsafe_allow_html=True)
        st.markdown("""<div style="font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#42493e;font-weight:700;margin-bottom:0.5rem">Data Source</div>""", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload dataset", type=["csv", "xlsx", "xlsm"], label_visibility="collapsed")
        if uploaded_file is None:
            st.markdown("""<div style="font-size:11px;color:#c2c9bb;margin-top:-10px;margin-bottom:1rem">Using default: plantation_soil_data.xlsm</div>""", unsafe_allow_html=True)

    df = load_data(uploaded_file)
    if df.empty:
        st.error("No data loaded. Please upload a dataset or ensure plantation_soil_data.xlsm is in the working directory.")
        return

    stats = compute_stats(df.to_json())

    with st.sidebar:
        st.markdown("<hr style='border:none;border-top:1px solid rgba(66,73,62,0.3);margin:0 0 1.5rem 0'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="padding:0 0.5rem">
            <div style="font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#42493e;font-weight:700;margin-bottom:0.5rem">System Status</div>
            <div style="display:flex;align-items:center;gap:8px;font-size:12px;color:#c2c9bb">
                <div style="width:8px;height:8px;background:#ffb4ab;border-radius:50%;animation:pulse 2s infinite"></div>
                Irrigation: OFFLINE
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:12px;color:#c2c9bb;margin-top:6px">
                <div style="width:8px;height:8px;background:#a1d494;border-radius:50%"></div>
                Sensors: 3/3 Online
            </div>
        </div>
        <style>@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }</style>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        
        csv_data = generate_csv_report(stats)
        st.download_button(
            label="📥  Export Soil Report",
            data=csv_data,
            file_name="soil_health_report.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ── TAB 1: EXECUTIVE OVERVIEW ─────────────────────────────────
def render_overview(df, stats):
    # Header
    st.markdown('<div class="section-label">Live Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Executive Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Non-expert soil health summary — real-time telemetry</div>', unsafe_allow_html=True)

    # ── CRITICAL ALERTS ──
    st.markdown("### 🚨 Active System Alerts")
    if stats["total_irrigation"] == 0:
        st.markdown("""
        <div class="alert-critical">
            <strong>CRITICAL: Irrigation System Offline (0.0mm recorded all week)</strong><br>
            <span style="font-size:13px;opacity:0.85">No water has been delivered via irrigation for 7 consecutive days. Mechanical failure or signal blockage at BMS controller suspected. Manual override required immediately.</span>
        </div>""", unsafe_allow_html=True)

    if stats["Plot1"]["min_moisture"] < WILTING_POINT:
        st.markdown(f"""
        <div class="alert-critical">
            <strong>CRITICAL: Plot 1 Drought & Salinity Stress ({stats['Plot1']['min_moisture']}% Moisture, {stats['Plot1']['max_ec']} dS/m EC)</strong><br>
            <span style="font-size:13px;opacity:0.85">Moisture dropped to wilting point this week. High EC suggests salt accumulation at root zone — crops facing osmotic stress. Immediate action required.</span>
        </div>""", unsafe_allow_html=True)

    if stats["Plot2"]["min_ph"] < PH_ACID:
        st.markdown(f"""
        <div class="alert-warning">
            <strong>WARNING: Plot 2 Soil Acidity Dip (pH {stats['Plot2']['min_ph']})</strong><br>
            <span style="font-size:13px;opacity:0.85">Nitrogen-induced acidification detected. pH dropped below safe threshold. Agricultural liming recommended within 48 hours to restore nutrient availability.</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── PLOT STATUS CARDS ──
    st.markdown("### 🗺️ Plot Status Monitor")
    cols = st.columns(3)

    for i, (plot, label) in enumerate([("Plot1","North Valley"), ("Plot2","Ridge Side"), ("Plot3","River Basin")]):
        s = stats[plot]
        css_cls = {"STRESSED":"critical","WARNING":"warning","OPTIMAL":"ok"}[s["status"]]
        badge_html = f'<span class="plot-badge-{css_cls}">{s["status"]}</span>'
        with cols[i]:
            st.markdown(f"""
            <div class="plot-card plot-card-{css_cls}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem">
                    <div class="plot-metric-label">{plot}: {label}</div>
                    {badge_html}
                </div>
                <div style="margin-bottom:0.75rem">
                    <div class="plot-metric-val">{s['moisture']}<span class="plot-metric-unit">%</span></div>
                    <div style="font-size:11px;color:#42493e;margin-top:2px">Volumetric Water Content</div>
                </div>
                <hr style="border:none;border-top:1px solid rgba(66,73,62,0.2);margin:0.75rem 0">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;font-size:12px">
                    <div><span style="color:#42493e">EC:</span> <span style="color:#c2c9bb;font-weight:600">{s['ec']} dS/m</span></div>
                    <div><span style="color:#42493e">pH:</span> <span style="color:#c2c9bb;font-weight:600">{s['ph']}</span></div>
                    <div><span style="color:#42493e">Temp:</span> <span style="color:#c2c9bb;font-weight:600">{s['temp']}°C</span></div>
                    <div><span style="color:#42493e">Week Min:</span> <span style="color:#ffb4ab;font-weight:600">{s['min_moisture']}%</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

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
            try:
                # Build conversation history for multi-turn chat
                contents = []
                for msg in st.session_state.chat_history:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

                response = st.session_state.gemini_client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=st.session_state.system_prompt,
                        max_output_tokens=400,
                    ),
                )
                reply = response.text
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
            <div style="color:#a1d494;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.5rem">⚠ Critical Insight</div>
            <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:16px;color:#e2e3de;margin-bottom:0.75rem">Irrigation Anomaly Detected</div>
            <div style="font-size:13px;color:#c2c9bb;line-height:1.6">
                Moisture levels <strong style="color:#a1d494">only recover</strong> immediately after rainfall events. During dry intervals, there is <strong style="color:#ffb4ab">zero moisture recovery</strong> despite scheduled irrigation cycles — confirming a mechanical failure in the BMS pump.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#1a1c1a;border:1px solid rgba(66,73,62,0.3);border-radius:12px;padding:1rem">
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#42493e;margin-bottom:0.75rem">Weekly Summary</div>
            <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(66,73,62,0.2);padding-bottom:0.5rem;margin-bottom:0.5rem">
                <span style="font-size:12px;color:#c2c9bb">Total Rainfall</span>
                <span style="font-size:12px;font-weight:700;color:#a5c8ff">555 mm</span>
            </div>
            <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(66,73,62,0.2);padding-bottom:0.5rem;margin-bottom:0.5rem">
                <span style="font-size:12px;color:#c2c9bb">Total Irrigation</span>
                <span style="font-size:12px;font-weight:700;color:#ffb4ab">0.0 mm</span>
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
                title="Moisture %",
                tickvals=[5, 22, 38],
                ticktext=["Drought", "Normal", "Wet"],
                tickfont=dict(color="#c2c9bb", size=10),
                titlefont=dict(color="#c2c9bb", size=11),
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


# ── TAB 3: ACTION CENTER ──────────────────────────────────────
def render_actions(stats):
    st.markdown('<div class="section-label">Technician Dispatch</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Action Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Prioritised operational tasks based on real-time soil telemetry</div>', unsafe_allow_html=True)

    col_badge, _ = st.columns([2, 5])
    with col_badge:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;background:#1a1c1a;padding:0.5rem 1rem;border-radius:20px;width:fit-content">
            <div style="width:8px;height:8px;background:#ffb4ab;border-radius:50%;animation:pulse 2s infinite"></div>
            <span style="font-size:13px;font-weight:600;color:#e2e3de">3 Pending Interventions</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Action 1: BMS Irrigation
    col_main, col_map = st.columns([2, 1])
    with col_main:
        with st.container():
            st.markdown(f"""
            <div class="action-card action-critical">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                        <span style="background:rgba(147,0,10,0.4);color:#ffb4ab;font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;text-transform:uppercase;letter-spacing:1px">⚡ Immediate Action Required</span>
                        <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:1.25rem;color:#e2e3de;margin-top:0.75rem">Inspect BMS Irrigation Controller &amp; Pumps</div>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-top:1rem">
                    <div>
                        <div style="font-size:12px;color:#42493e;margin-bottom:4px">Issue Description</div>
                        <div style="font-size:13px;color:#c2c9bb;line-height:1.6">System has recorded <strong style="color:#ffb4ab">{stats['total_irrigation']}mm</strong> of irrigation for 7 straight days despite scheduled cycles. Potential mechanical failure or signal blockage at the main BMS controller.</div>
                    </div>
                    <div>
                        <div style="font-size:12px;color:#42493e;margin-bottom:4px">System Pressure</div>
                        <div style="background:#1a1c1a;border-radius:8px;padding:0.75rem">
                            <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px"><span style="color:#42493e">Irrigation Pressure</span><span style="color:#ffb4ab;font-weight:700">LOW</span></div>
                            <div style="background:rgba(66,73,62,0.3);border-radius:4px;height:4px;overflow:hidden"><div style="background:#ffb4ab;height:100%;width:8%"></div></div>
                        </div>
                    </div>
                </div>
                <div style="display:flex;gap:1.5rem;margin-top:1rem;padding-top:1rem;border-top:1px solid rgba(66,73,62,0.2);font-size:12px;color:#42493e">
                    <span>📍 Main Hub — Sector Alpha</span>
                    <span>⏰ Due: Immediate</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_map:
        st.markdown("""
        <div style="background:#1a1c1a;border:1px solid rgba(66,73,62,0.3);border-radius:12px;padding:1rem;height:100%">
            <div style="font-weight:700;font-size:14px;color:#e2e3de;margin-bottom:0.75rem">Location Context</div>
            <div style="background:linear-gradient(135deg,#0e110e,#1a1c1a);border-radius:8px;height:120px;display:flex;align-items:center;justify-content:center;font-size:3rem;margin-bottom:0.75rem">🗺️</div>
            <div style="font-size:11px;color:#42493e">Last pulse: 14:02 UTC · Sensor online: 98.2%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Actions 2 & 3
    col_a2, col_a3 = st.columns(2)
    with col_a2:
        st.markdown(f"""
        <div class="action-card action-short">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem">
                <div style="width:48px;height:48px;background:rgba(165,200,255,0.1);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.5rem">💧</div>
            </div>
            <span style="font-size:10px;font-weight:700;color:#a5c8ff;text-transform:uppercase;letter-spacing:1.5px">Short-term Action</span>
            <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:1.1rem;color:#e2e3de;margin:0.5rem 0">Perform Fresh-water Flush on Plot 1</div>
            <div style="font-size:13px;color:#c2c9bb;line-height:1.6;margin-bottom:1rem">
                Wash accumulated surface salts (<strong style="color:#e2e3de">{stats['Plot1']['max_ec']} dS/m</strong>) back below the active root zone to prevent osmotic stress. Target: EC below 2.0 dS/m.
            </div>
            <div style="display:flex;justify-content:space-between;font-size:11px;padding-top:0.75rem;border-top:1px solid rgba(66,73,62,0.2)">
                <span style="color:#42493e">Assigned: Water Team</span>
                <span style="color:#a5c8ff;font-weight:700">Priority: High</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_a3:
        st.markdown(f"""
        <div class="action-card" style="border-left:4px solid #ffb3ac">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem">
                <div style="width:48px;height:48px;background:rgba(255,179,172,0.1);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.5rem">🧪</div>
            </div>
            <span style="font-size:10px;font-weight:700;color:#ffb3ac;text-transform:uppercase;letter-spacing:1.5px">Short-term Action</span>
            <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:1.1rem;color:#e2e3de;margin:0.5rem 0">Apply pH Buffer (Agricultural Lime) to Plot 2</div>
            <div style="font-size:13px;color:#c2c9bb;line-height:1.6;margin-bottom:1rem">
                Neutralise the <strong style="color:#ffb3ac">pH {stats['Plot2']['min_ph']}</strong> acidic dip. Target pH range: 6.2–6.8 for optimal nutrient uptake in silty soil.
            </div>
            <div style="display:flex;justify-content:space-between;font-size:11px;padding-top:0.75rem;border-top:1px solid rgba(66,73,62,0.2)">
                <span style="color:#42493e">Requires: Chem-Group</span>
                <span style="color:#ffb3ac;font-weight:700">Priority: Medium</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Footer stats
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div style="background:#111411;border-radius:12px;padding:1.25rem;border:1px solid rgba(66,73,62,0.25)">
            <div class="plot-metric-label">Completion Rate</div>
            <div style="font-family:Manrope,sans-serif;font-size:2.5rem;font-weight:800;color:#a1d494">82%
            <span style="font-size:13px;font-weight:400;color:#a1d494">+4.2% this week</span></div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div style="background:#111411;border-radius:12px;padding:1.25rem;border:1px solid rgba(66,73,62,0.25)">
            <div class="plot-metric-label">Avg Response Time</div>
            <div style="font-family:Manrope,sans-serif;font-size:2.5rem;font-weight:800;color:#e2e3de">2.4h
            <span style="font-size:13px;font-weight:400;color:#42493e">Standard: &lt;4h</span></div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div style="background:#111411;border-radius:12px;padding:1.25rem;border:1px solid rgba(66,73,62,0.25)">
            <div class="plot-metric-label">Technicians Active</div>
            <div style="font-family:Manrope,sans-serif;font-size:2.5rem;font-weight:800;color:#e2e3de">12/14
            <span style="font-size:13px;font-weight:400;color:#42493e">Fleet status</span></div></div>""", unsafe_allow_html=True)


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
            st.markdown(f"""
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
            """, unsafe_allow_html=True)

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


    if active_tab == "Executive Overview":
        render_overview(df, stats)
    elif active_tab == "Historical Trends":
        render_trends(df, stats)
    elif active_tab == "Action Center":
        render_actions(stats)
    elif active_tab == "Future Upgrades":
        render_upgrades()


if __name__ == "__main__":
    main()
