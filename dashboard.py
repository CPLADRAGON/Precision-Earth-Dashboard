import streamlit as st
import pandas as pd
import numpy as np
import os
import re

# ──────────────────────────────────────────────────────────────
# CONFIG & HEADLESS THEME
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bioluminescent Nexus | Soil Health Monitor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide all Streamlit default UI
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    [data-testid="stSidebar"] {display: none;}
    iframe {border: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;}
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# DATA ENGINE
# ──────────────────────────────────────────────────────────────
def load_data():
    file_path = "plantation_soil_data.xlsm"
    try:
        df = pd.read_excel(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True)
    except:
        times = pd.date_range(end=pd.Timestamp.now(), periods=50, freq='H')
        df = pd.DataFrame({
            "timestamp": times,
            "plot_id": ["Sector Alpha-7"] * 50,
            "soil_moisture_pct": np.random.uniform(20, 30, 50),
            "soil_temp_c": np.random.uniform(25, 33, 50),
            "soil_ec_ds_m": np.random.uniform(1.0, 1.5, 50),
            "soil_ph": np.random.uniform(6.0, 7.0, 50),
            "rainfall_mm": np.random.choice([0, 0, 5, 0], 50),
            "irrigation_mm": np.random.choice([0, 10, 0, 0], 50),
        })
    return df

def get_live_metrics(df, plot_id="Sector Alpha-7"):
    plot_df = df[df['plot_id'].str.contains(plot_id, case=False, na=False)].sort_values('timestamp')
    latest = plot_df.iloc[-1] if not plot_df.empty else df.iloc[-1]
    
    anomalies = 0
    if latest['soil_moisture_pct'] < 15 or latest['soil_moisture_pct'] > 45: anomalies += 1
    if latest['soil_temp_c'] > 35: anomalies += 1

    return {
        "moisture": f"{latest['soil_moisture_pct']:.1f}",
        "temp": f"{latest['soil_temp_c']:.1f}",
        "ec": f"{latest['soil_ec_ds_m']:.2f}",
        "ph": f"{latest['soil_ph']:.1f}",
        "alerts": f"{anomalies:02}",
        "rainfall": f"{df['rainfall_mm'].sum():.1f}",
        "plot": plot_id
    }

# ──────────────────────────────────────────────────────────────
# SPA TEMPLATE GENERATOR
# ──────────────────────────────────────────────────────────────
def build_spa_html(metrics):
    base_path = "stitch ui/stitch"
    
    # Read the 3 core templates
    overview_raw = open(os.path.join(base_path, "overview_dashboard", "code.html"), "r", encoding="utf-8").read()
    trends_raw = open(os.path.join(base_path, "trends_analysis", "code.html"), "r", encoding="utf-8").read()
    anomaly_raw = open(os.path.join(base_path, "anomaly_detection", "code.html"), "r", encoding="utf-8").read()
    
    # Extract the common <head> and <body> structure from Overview
    # We'll use Overview as the master frame
    head = re.search(r'<head>(.*?)</head>', overview_raw, re.DOTALL).group(1)
    sidebar = re.search(r'<aside[^>]*>(.*?)</aside>', overview_raw, re.DOTALL).group(1)
    header = re.search(r'<header[^>]*>(.*?)</header>', overview_raw, re.DOTALL).group(1)
    
    # Extract the <main> content for each tab
    overview_content = re.search(r'<main[^>]*>(.*?)</main>', overview_raw, re.DOTALL).group(1)
    # Remove the header from the content as we have a shared one
    overview_content = re.sub(r'<header.*?</header>', '', overview_content, flags=re.DOTALL)
    
    trends_content = re.search(r'<main[^>]*>(.*?)</main>', trends_raw, re.DOTALL).group(1)
    trends_content = re.sub(r'<header.*?</header>', '', trends_content, flags=re.DOTALL)
    
    anomaly_content = re.search(r'<main[^>]*>(.*?)</main>', anomaly_raw, re.DOTALL).group(1)
    anomaly_content = re.sub(r'<header.*?</header>', '', anomaly_content, flags=re.DOTALL)

    # Inject Live Data into Overview
    overview_content = re.sub(r'24\.8<span class="text-lg opacity-60 ml-1">\%</span>', f'{metrics["moisture"]}<span class="text-lg opacity-60 ml-1">%</span>', overview_content)
    overview_content = re.sub(r'32\.5<span class="text-lg opacity-60 ml-1">°C</span>', f'{metrics["temp"]}<span class="text-lg opacity-60 ml-1">°C</span>', overview_content)
    overview_content = overview_content.replace('Sector Alpha-7 Overview', f'{metrics["plot"]} Overview')

    # Construct SPA
    spa_html = f"""
    <!DOCTYPE html>
    <html class="dark" lang="en">
    <head>
        {head}
        <style>
            .tab-content {{ display: none; }}
            .tab-content.active {{ display: block; }}
            .nav-item.active {{ background: rgba(50, 53, 60, 0.6); color: #78DC77; border-left: 2px solid #78DC77; font-weight: bold; }}
        </style>
    </head>
    <body class="bg-background text-on-surface font-body overflow-hidden">
        <aside class="bg-[#191C22] h-screen w-64 fixed left-0 top-0 overflow-y-auto z-50 flex flex-col py-6 font-['Space_Grotesk'] shadow-none">
            {sidebar}
        </aside>
        <main class="ml-64 min-h-screen">
            <header class="fixed top-0 right-0 w-[calc(100%-16rem)] z-40 bg-[#101319]/80 backdrop-blur-xl flex justify-between items-center h-20 px-8 border-b border-white/5 shadow-2xl shadow-black/40">
                {header}
            </header>
            <div id="tab-Overview" class="tab-content active pt-20">{overview_content}</div>
            <div id="tab-Trends" class="tab-content pt-20">{trends_content}</div>
            <div id="tab-Rainfall" class="tab-content pt-20">{trends_content}</div>
            <div id="tab-Anomaly" class="tab-content pt-20">{anomaly_content}</div>
            <div id="tab-Correlations" class="tab-content pt-20">{overview_content}</div>
        </main>

        <script>
            function showTab(tabName) {{
                // Hide all
                document.querySelectorAll('.tab-content').forEach(d => d.classList.remove('active'));
                document.querySelectorAll('nav a').forEach(a => a.classList.remove('active', 'bg-[#32353C]/60', 'text-[#78DC77]', 'border-l-2', 'border-[#78DC77]', 'font-bold'));
                
                // Show selected
                const target = document.getElementById('tab-' + tabName);
                if (target) target.classList.add('active');
                
                // Update Sidebar
                const links = document.querySelectorAll('nav a');
                links.forEach(a => {{
                    if (a.innerText.includes(tabName) || (tabName === "Rainfall" && a.innerText.includes("Rainfall"))) {{
                        a.classList.add('bg-[#32353C]/60', 'text-[#78DC77]', 'border-l-2', 'border-[#78DC77]', 'font-bold');
                    }}
                }});
            }}

            // Setup Click Listeners
            document.addEventListener('DOMContentLoaded', () => {{
                const navMap = {{
                    "Overview": "Overview",
                    "Trends": "Trends",
                    "Rainfall": "Rainfall",
                    "Anomaly": "Anomaly",
                    "Correlations": "Correlations"
                }};
                
                document.querySelectorAll('nav a').forEach(a => {{
                    a.href = "javascript:void(0)";
                    a.onclick = (e) => {{
                        const text = a.innerText.trim();
                        if (text.includes("Overview")) showTab("Overview");
                        if (text.includes("Trends")) showTab("Trends");
                        if (text.includes("Rainfall")) showTab("Rainfall");
                        if (text.includes("Anomaly")) showTab("Anomaly");
                        if (text.includes("Correlations")) showTab("Correlations");
                    }};
                }});
            }});
        </script>
    </body>
    </html>
    """
    return spa_html

# ──────────────────────────────────────────────────────────────
# MAIN APP
# ──────────────────────────────────────────────────────────────
df = load_data()
metrics = get_live_metrics(df)
final_html = build_spa_html(metrics)

st.components.v1.html(final_html, height=1200, scrolling=False)
