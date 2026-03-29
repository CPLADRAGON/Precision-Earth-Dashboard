import streamlit as st
import pandas as pd
import numpy as np
import os
import re
import plotly.graph_objects as go

# ──────────────────────────────────────────────────────────────
# CONFIG & HEADLESS THEME
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bioluminescent Nexus | Soil Health Monitor",
    page_icon="🌱", layout="wide", initial_sidebar_state="collapsed",
)

# Read query params
params = st.query_params
selected_plot = params.get("plot", "Sector Alpha-7")
moisture_max = float(params.get("m_max", 45))
active_tab = params.get("tab", "Overview")

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
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True)
            if 'plot_id' not in df.columns: df['plot_id'] = "Sector Alpha-7"
        else: raise Exception("No timestamp")
    except:
        times = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='H')
        plots = ["Sector Alpha-7", "Sector Beta-2", "Sector Gamma-3"]
        data = []
        for p in plots:
          for t in times:
            data.append({"timestamp": t, "plot_id": p, "soil_moisture_pct": np.random.uniform(10, 50), "soil_temp_c": np.random.uniform(20, 40)})
        df = pd.DataFrame(data)
    return df

def get_charts(df, m_min, m_max):
    # Trends
    fig_tr = go.Figure()
    fig_tr.add_trace(go.Scatter(x=df['timestamp'], y=df['soil_moisture_pct'], name='Moisture', line=dict(color='#78DC77', width=3), fill='tozeroy', fillcolor='rgba(120, 220, 119, 0.1)'))
    fig_tr.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=20, t=10, b=20), height=350,
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color='#BECAB9')),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False, tickfont=dict(color='#BECAB9')), showlegend=False)
    
    # Anomaly
    fig_an = go.Figure()
    anom = df[(df['soil_moisture_pct'] < m_min) | (df['soil_moisture_pct'] > m_max)]
    norm = df[~df.index.isin(anom.index)]
    fig_an.add_trace(go.Scatter(x=norm['timestamp'], y=norm['soil_moisture_pct'], mode='markers', name='Ok', marker=dict(color='rgba(120, 220, 119, 0.4)', size=7)))
    fig_an.add_trace(go.Scatter(x=anom['timestamp'], y=anom['soil_moisture_pct'], mode='markers', name='Anomaly', marker=dict(color='#FFB4AB', size=12, symbol='x')))
    fig_an.add_hline(y=m_min, line_dash="dash", line_color="#FFB4AB", opacity=0.3)
    fig_an.add_hline(y=m_max, line_dash="dash", line_color="#FFB4AB", opacity=0.3)
    fig_an.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=20, t=30, b=40), height=450,
        xaxis=dict(showgrid=False, gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#BECAB9')),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#BECAB9')),
        legend=dict(font=dict(color='#BECAB9'), orientation="h", y=1.05, x=1, xanchor="right"))
    
    return fig_tr.to_html(include_plotlyjs='cdn', full_html=False), fig_an.to_html(include_plotlyjs='cdn', full_html=False)

# ──────────────────────────────────────────────────────────────
# DASHBOARD GENERATOR
# ──────────────────────────────────────────────────────────────
def build_dashboard_html(df, plot_id, m_max, tab):
    base_path = "stitch ui/stitch"
    m_min = 15
    available_plots = df['plot_id'].unique()
    if plot_id not in available_plots: plot_id = available_plots[0]
    plot_df = df[df['plot_id'] == plot_id].sort_values('timestamp')
    latest = plot_df.iloc[-1] if not plot_df.empty else {"soil_moisture_pct": 24.8, "soil_temp_c": 32.5}

    # Template Logic
    tab_map = {"Overview": "overview_dashboard", "Trends": "trends_analysis", "Anomaly": "anomaly_detection"}
    folder = tab_map.get(tab, "overview_dashboard")
    raw = open(os.path.join(base_path, folder, "code.html"), "r", encoding="utf-8").read()

    # Extraction
    head = re.search(r'<head>(.*?)</head>', raw, re.DOTALL).group(1)
    sidebar = re.search(r'<aside[^>]*>(.*?)</aside>', raw, re.DOTALL).group(1)
    header = re.search(r'<header[^>]*>(.*?)</header>', raw, re.DOTALL).group(1)
    main = re.search(r'<main[^>]*>(.*?)</main>', raw, re.DOTALL).group(1)
    main = re.sub(r'<header.*?</header>', '', main, flags=re.DOTALL) # Clean duplicate

    # Sidebar Injection
    plots_html = "".join([f'<option value="{p}" {"selected" if p == plot_id else ""}>{p}</option>' for p in available_plots])
    sidebar = re.sub(r'<select[^>]*>.*?</select>', f'<select id="plot-master" class="w-full bg-surface-container border-none text-sm rounded-lg text-on-surface py-2">{plots_html}</select>', sidebar, flags=re.DOTALL)
    sidebar = re.sub(r'<input[^>]*type="range"[^>]*>', f'<input id="m-max-slider" type="range" min="0" max="100" value="{m_max}" class="w-full accent-primary h-1 bg-surface-container rounded-lg appearance-none cursor-pointer">', sidebar)

    # Content Injection
    if tab == "Overview":
        main = re.sub(r'24\.8<span[^>]*>\%</span>', f'{latest["soil_moisture_pct"]:.1f}<span class="text-lg opacity-60 ml-1">%</span>', main)
        main = re.sub(r'32\.5<span[^>]*>°C</span>', f'{latest["soil_temp_c"]:.1f}<span class="text-lg opacity-60 ml-1">°C</span>', main)
        main = main.replace('Sector Alpha-7 Overview', f'{plot_id} Overview').replace('Sector Alpha-7 Monitoring', f'{plot_id} Monitoring')
    
    tr_html, an_html = get_charts(plot_df, m_min, m_max)
    chart_html = tr_html if tab == "Trends" else (an_html if tab == "Anomaly" else "")
    if chart_html:
        main += f'<div id="chart-mount" style="width:100%; min-height:450px; margin-top:20px;">{chart_html}</div>'

    html = f"""
    <!DOCTYPE html>
    <html class="dark" lang="en">
    <head>{head}<style>main{{padding-top:80px; height:100vh; overflow-y:auto;}} nav a.active-link{{background:rgba(50,53,60,0.6); color:#78DC77; border-left:2px solid #78DC77; font-weight:bold;}}</style></head>
    <body class="bg-background text-on-surface font-body overflow-hidden">
        <aside class="bg-[#191C22] h-screen w-64 fixed left-0 top-0 overflow-y-auto z-50 flex flex-col py-6">{sidebar}</aside>
        <header class="fixed top-0 right-0 w-[calc(100%-16rem)] z-40 bg-[#101319]/90 backdrop-blur-xl flex justify-between items-center h-20 px-8 border-b border-white/5">{header}</header>
        <main class="ml-64">{main}</main>
        <script>
            window.onload = () => {{
                const nav = document.querySelectorAll('nav a');
                const t = "{tab}"; const p = "{plot_id}"; const m = "{m_max}";
                const go = (target) => window.top.location.href = `?tab=${{target}}&plot=${{p}}&m_max=${{m}}`;
                
                if (nav[0]) {{ nav[0].onclick = () => go('Overview'); if (t=='Overview') nav[0].classList.add('active-link'); }}
                if (nav[1]) {{ nav[1].onclick = () => go('Trends'); if (t=='Trends') nav[1].classList.add('active-link'); }}
                if (nav[3]) {{ nav[3].onclick = () => go('Anomaly'); if (t=='Anomaly') nav[3].classList.add('active-link'); }}
                
                const sel = document.getElementById('plot-master');
                const sli = document.getElementById('m-max-slider');
                const update = () => window.top.location.href = `?tab=${{t}}&plot=${{sel.value}}&m_max=${{sli.value}}`;
                if (sel) sel.onchange = update;
                if (sli) sli.onchange = update;
            }};
        </script>
    </body>
    </html>
    """
    return html

df = load_data()
st.components.v1.html(build_dashboard_html(df, selected_plot, moisture_max, active_tab), height=1200, scrolling=False)
