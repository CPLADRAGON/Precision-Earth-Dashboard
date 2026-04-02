import streamlit as st
st.set_page_config(
    page_title="Precision Earth | Smart Agri-Monitor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from google import genai
from google.genai import types
import base64
import os
import time
import numpy as np
from datetime import datetime
from dashboard_logic import load_data, compute_stats, get_categorical_heatmap_data

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = "AIzaSyBXQZwWuXX0vf6HQBTBXoFcCs3ZkGux23M"

# --- HELPER UTILS ---
@st.cache_data
def get_audio_base64(file_path):
    if not os.path.exists(file_path): return ""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render_bgm(file_path, play=True):
    audio_b64 = get_audio_base64(file_path)
    if not audio_b64: return
    if play:
        st.markdown("<style>#bgm-player-wrapper { display: none; }</style>", unsafe_allow_html=True)
        st.markdown('<div id="bgm-player-wrapper">', unsafe_allow_html=True)
        st.audio(data=f"data:audio/mp3;base64,{audio_b64}", autoplay=True, loop=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- BRANDING UTILS ---
def get_base64_img(path):
    if not os.path.exists(path): return ""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

# (Dynamic background handled in main)
LOGO_B64 = get_base64_img("grphics/logo.png")
AI_ICON_B64 = get_base64_img("grphics/AI.png")

# --- DESIGN SYSTEM ---
def get_style(bg_b64, ai_b64, overlay_b64):
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Epilogue:wght@800&family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@700&family=Silkscreen&display=swap');

    /* --- GLOBAL UI FIXES (v15 STABILITY) --- */
    /* Absolute Immersion: Hide Streamlit Controls */
    [data-testid="stHeader"], .stDeployButton, #MainMenu, footer, [data-testid="stSidebarCollapseButton"] {{ 
        visibility: hidden !important; 
        display: none !important; 
    }}
    
    /* Absolute Audio Stealth (Reinforced) */
    div[data-testid="stAudio"], audio, #bgm-player-wrapper {{ 
        display: none !important; 
        height: 0 !important; 
        width: 0 !important; 
        visibility: hidden !important; 
        position: absolute !important;
        pointer-events: none !important;
    }}
    
    /* Absolute Sidebar Persistence & Scroll Fix */
    [data-testid="stSidebar"] {{
        transform: none !important;
        visibility: visible !important;
        min-width: 350px !important;
        max-width: 350px !important;
    }}
    section[data-testid="stSidebar"] > div:first-child {{
        min-width: 350px !important;
    }}
    [data-testid="stSidebarContent"] {{
        overflow-y: auto !important;
        height: 100vh !important;
    }}
    
    /* 2. REFINED HEADER - Robust Restoration */
    .brand-header {{
        background: #0D1513 !important;
        background: linear-gradient(180deg, #0D1513 0%, #1a2a26 100%) !important;
        border-bottom: 3px solid #4EDEA3;
        padding: 25px 50px !important;
        display: flex !important;
        align-items: center !important;
        gap: 30px !important;
        width: 100% !important;
        min-height: 140px !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 99 !important;
    }}
    
    /* STATION AUTHORIZATION: Bulletproof Solid Wrapper */
    [data-testid="stVerticalBlockBorderWrapper"]:has(#auth-gate) {{
        background: #0D1513 !important;
        border: 2px solid #4EDEA3 !important;
        border-radius: 16px !important;
        padding: 3rem !important;
        box-shadow: 0 50px 150px rgba(0,0,0,1) !important;
    }}
    [data-testid="stVerticalBlockBorderWrapper"]:has(#auth-gate) > div {{
        background: #0D1513 !important;
    }}
    
    .brand-title {{
        font-family: 'Silkscreen', cursive !important;
        font-size: 2.0rem !important;
        color: #4EDEA3 !important;
        text-shadow: 2px 2px 0px rgba(0,0,0,0.5);
        letter-spacing: 2px;
        font-weight: 800;
    }}

    /* 1. FLOATING FAB & CHAT (Bottom Right) */
    div[data-testid="stVerticalBlock"]:has(> div > div > [id="fab-anchor-id"]) {{
        position: fixed !important; bottom: 32px; right: 32px;
        z-index: 1000000; width: 100px; height: 100px;
    }}
    div:has(> #fab-anchor-id) button, button[key="junimo_fab_btn"] {{
        width: 100px !important; height: 100px !important;
        background: transparent url(data:image/png;base64,{ai_b64}) no-repeat center !important;
        background-size: 80px !important; color: transparent !important;
        image-rendering: pixelated !important; border-radius: 0 !important;
        border: none !important; box-shadow: 
            0 0 0 4px #3e2723, 0 0 0 8px #7d5233, 0 0 0 12px #a1887f,
            8px 8px 0px rgba(0,0,0,0.4) !important;
        transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }}
    button[key="junimo_fab_btn"]:hover {{ transform: scale(1.1) !important; }}

    /* 3. WOODEN BUTTON TAGS (Sidebar & Panels) */
    div[data-testid="stColumn"]:has(> div > div > button[key="music_toggle_btn"]) button,
    button[key="music_toggle_btn"],
    section[data-testid="stSidebar"] .stButton > button,
    .stApp [data-testid="stVerticalBlock"] .stButton > button {{
        background: #7d5233 !important; border: 4px solid #3e2723 !important;
        color: #fff !important; font-family: 'Silkscreen' !important;
        border-radius: 0 !important; image-rendering: pixelated !important;
        box-shadow: inset -6px -6px 0px #3e2723, inset 6px 6px 0px #a1887f, 6px 6px 0px rgba(0,0,0,0.5) !important;
    }}
    button[key="music_toggle_btn"] {{ 
        width: 64px !important; height: 64px !important; 
        font-size: 1.8rem !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-family: 'Silkscreen' !important;
    }}
    
    /* Reveal the actual button label but style it as a wooden sign */
    button[key="junimo_fab_btn"] div[data-testid="stMarkdownContainer"] p {{
        font-size: 0 !important; /* Hide original */
    }}

    /* Target the Chat Panel container (FIX 4) */
    div[data-testid="stVerticalBlock"]:has(> div > div > [id="chat-panel-anchor-id"]) {{
        position: fixed !important;
        bottom: 120px !important;
        right: 32px !important;
        width: 420px !important;
        z-index: 99999 !important;
        background: #0D1513 !important;
        border: 4px solid var(--primary) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 50px rgba(0,0,0,0.9) !important;
        overflow: hidden !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown h3, 
    section[data-testid="stSidebar"] .stMarkdown p {{
        font-family: 'Silkscreen' !important;
        color: var(--primary) !important;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        width: 100% !important;
    }}
    
    :root {{
        --base: #0D1513;
        --surface-low: rgba(21, 29, 27, 0.85);
        --surface-mid: rgba(30, 38, 35, 0.9);
        --surface-high: rgba(35, 44, 41, 0.95);
        --primary: #4EDEA3;
        --primary-dim: #10B981;
    }}

    /* Keyframes */
    @keyframes pixel-pulse {{
      0%   {{ box-shadow: 4px 4px 0px rgba(0,0,0,0.5); }}
      50%  {{ box-shadow: 6px 6px 0px rgba(93,64,55,0.8); }}
      100% {{ box-shadow: 4px 4px 0px rgba(0,0,0,0.5); }}
    }}

    @keyframes float-up {{
      0%   {{ transform: translateY(0px); }}
      50%  {{ transform: translateY(-8px); }}
      100% {{ transform: translateY(0px); }}
    }}

    .stApp {{ 
        background: url(data:image/png;base64,{bg_b64}) no-repeat center center fixed;
        background-size: cover;
        background-color: var(--base);
        color: #F8FAFC;
    }}

    /* ── CHAT SYSTEM REFACTOR (FIX 3) ────────────────────────── */
    /* FAB Mascot Styling */
    button[key="junimo_fab_btn"] {{
        width: 80px !important;
        height: 80px !important;
        border-radius: 50% !important;
        border: 4px solid var(--primary) !important;
        background: #0D1513 url(data:image/png;base64,{ai_b64}) no-repeat center !important;
        background-size: 56px !important;
        color: transparent !important;
        font-size: 0 !important;
        animation: junimo-glow 2s ease-in-out infinite !important;
        box-shadow: 0 0 30px rgba(78,222,163,0.4) !important;
        transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        padding: 0 !important;
    }}
    button[key="junimo_fab_btn"]:hover {{ 
        transform: scale(1.15) rotate(10deg) !important;
        border-color: #ffffff !important;
    }}

    .chat-panel-frame {{
        background: #0D1513 !important;
        display: flex !important;
        flex-direction: column !important;
    }}

    .chat-header-bar {{
        padding: 16px 20px !important;
        background: rgba(78,222,163,0.15) !important;
        border-bottom: 2px solid rgba(78,222,163,0.3) !important;
        display: flex !important;
        align-items: center !important;
        gap: 14px !important;
        font-family: 'Silkscreen' !important;
        font-size: 1.1rem !important; /* Upscaled */
        font-weight: bold !important;
        color: var(--primary) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }}

    /* Tab Upscaling (FIX 4) */
    button[data-baseweb="tab"] {{
        font-size: 1.2rem !important;
        padding: 15px 30px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }}
    button[data-baseweb="tab"]:hover {{
        color: var(--primary) !important;
        background: rgba(78,222,163,0.05) !important;
    }}
    div[data-baseweb="tab-highlight"] {{
        background-color: var(--primary) !important;
        height: 4px !important;
    }}

    /* Chat Bubbles with Profiles */
    .profile-img {{
        width: 64px !important;
        height: 64px !important;
        border-radius: 8px !important;
        border: 3px solid #5d4037;
        background: #0D1513;
        image-rendering: pixelated;
        flex-shrink: 0;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.3);
    }}
    .user-msg-container {{ display: flex; align-items: flex-start; gap: 15px; margin: 20px 0; flex-direction: row-reverse; }}
    .ai-msg-container   {{ display: flex; align-items: flex-start; gap: 15px; margin: 20px 0; }}
    
    .msg-bubble {{
        padding: 15px 20px;
        border-radius: 4px;
        font-size: 0.95rem;
        font-family: 'Plus Jakarta Sans', sans-serif;
        line-height: 1.6;
        max-width: 80%;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.5);
        border: 3px solid #3e2723;
    }}
    .user-bubble {{ background: #4EDEA3; color: #0D1513; font-weight: 600; }}
    .ai-bubble   {{ background: #0D1513 !important; color: #FFF; border: 3px solid var(--primary); }}

    /* Forensic Scanner Animation */
    @keyframes forensic-scan {{
        0% {{ transform: rotate(0deg); border-top-color: var(--primary); }}
        50% {{ transform: rotate(180deg); border-top-color: #FFF; }}
        100% {{ transform: rotate(360deg); border-top-color: var(--primary); }}
    }}
    .forensic-spinner {{
        width: 30px;
        height: 30px;
        border: 4px solid rgba(78,222,163,0.1);
        border-top: 4px solid var(--primary);
        border-radius: 50%;
        animation: forensic-scan 1s linear infinite;
    }}
    .thinking-bubble {{
        background: #0D1513 !important;
        border: 3px solid var(--primary-dim) !important;
        color: var(--primary) !important;
        font-family: 'Silkscreen' !important;
        font-size: 0.8rem !important;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 18px;
    }}

    /* Stardew Style FAB with Tag */
    button[key="junimo_fab_btn"] {{
        width: 90px !important;
        height: 90px !important;
        border-radius: 0% !important; /* Pixelated square look */
        border: none !important;
        background: transparent url(data:image/png;base64,{ai_b64}) no-repeat center !important;
        background-size: 70px !important;
        color: transparent !important;
        font-size: 0 !important;
        z-index: 100001 !important;
        box-shadow: none !important;
        image-rendering: pixelated !important;
        position: relative !important;
    }}
    
    /* The Wooden Tag */
    div[data-testid="stVerticalBlock"]:has(> div > div > [id="fab-anchor-id"]):after {{
        content: "CONSULT WITH AI";
        position: absolute;
        bottom: -25px;
        left: 50%;
        transform: translateX(-50%);
        background: #7d5233;
        color: #fff176;
        font-family: 'Silkscreen';
        font-size: 0.7rem;
        padding: 4px 8px;
        border: 3px solid #3e2723;
        box-shadow: 3px 3px 0px rgba(0,0,0,0.4);
        white-space: nowrap;
        pointer-events: none;
    }}

    .brand-header {{
        background: linear-gradient(90deg, rgba(0,0,0,0.95), rgba(13,21,19,0.98));
        height: 110px;
        display: flex;
        align-items: center;
        padding: 0 40px;
        border-bottom: 3px solid var(--primary-dim);
        margin-bottom: 20px;
    }}
    
    .farm-tile {{
        height: 350px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        border: 4px solid var(--surface-low);
        transition: all 0.3s ease;
        position: relative;
        background: var(--surface-low);
    }}
    .farm-tile:hover {{ 
        border-color: var(--primary); 
        animation: float-up 0.8s ease-in-out infinite;
        z-index: 10;
    }}
    
    .tile-photo-full {{
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        object-fit: cover;
        opacity: 0.8;
    }}

    .status-tag {{
        position:absolute; top:20px; left:20px; z-index:4; 
        padding:8px 16px; font-family:'Silkscreen'; 
        font-size:1rem; font-weight:700; color:#000;
        border-radius: 2px;
        box-shadow: 3px 3px 0px rgba(0,0,0,0.5);
    }}

    .tile-overlay {{
        position: relative;
        z-index: 2;
        background: linear-gradient(to top, rgba(0,0,0,0.98), transparent);
        padding: 30px;
        width: 100%;
    }}

    .metric-line {{
        display: flex;
        justify-content: space-between;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 4px;
        font-size: 0.9rem;
    }}
    .badge-warn {{ background: #fbbf24; color: #000; padding: 0 5px; border-radius: 2px; font-weight: 700; }}
    .badge-crit {{ background: #ef4444; color: #000; padding: 0 5px; border-radius: 2px; font-weight: 700; }}

    .label-tech {{ 
        font-family: 'Silkscreen', cursive; 
        font-size: 0.9rem; 
        color: var(--primary); 
        letter-spacing: 0.2em; 
        margin-bottom: 10px;
    }}

    /* RPG Buttons: Clean Integration */
    div.stButton > button {{
        background-color: #5d4037 !important;
        border: 4px solid #3e2723 !important;
        color: #fff176 !important;
        font-family: 'Silkscreen', cursive !important;
        image-rendering: pixelated;
        text-transform: uppercase;
        letter-spacing: 1px;
        animation: pixel-pulse 3s infinite;
        padding: 0.5rem 1rem !important;
    }}
    
    /* Force Transparent Internals to prevent "boxy" artifacts */
    div.stButton > button p, 
    div.stButton > button div,
    div.stButton > button span {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: inherit !important;
        font-family: inherit !important;
    }}
    div.stButton > button:hover {{
        background-color: #795548 !important;
        border-color: #5d4037 !important;
        color: #ffffff !important;
        transform: translateY(2px);
    }}

    h3, .stSubheader, label p {{ font-family: 'Silkscreen', cursive !important; color: var(--primary) !important; }}
</style>
"""

# --- AI CORE ---
class AIAgronomist:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-3.1-flash-lite-preview" 

    def get_response(self, prompt, history=[], context=""):
        contents = []
        # Prepend context as a system-like message if provided
        if context:
            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=f"CRITICAL FIELD CONTEXT: {context}. Always reference these plots if asked.")]))
            contents.append(types.Content(role="assistant", parts=[types.Part.from_text(text="I have ingested the telemetry. Standing by for specific forensic requests.")]))
            
        for msg in history:
            contents.append(types.Content(role="user" if msg["role"]=="user" else "assistant", 
                                       parts=[types.Part.from_text(text=msg["msg"] if "msg" in msg else msg["content"])]))
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="Professional Ag-Forensic Lead. Concise, data-driven. Use the provided FIELD CONTEXT to answer plot-specific questions. Focus on Lagged Rainfall and Health Envelopes."
            )
        )
        return response.text

# --- CHAT UTILS ---
def generate_farm_context(stats):
    ctx = "Current Farm Status: "
    for _, row in stats.iterrows():
        ctx += f"[{row['plot_id']}: {row['overall_status']}, Moisture {row['soil_moisture_pct']:.1f}%, EC {row['soil_ec_ds_m']:.2f}, pH {row['soil_ph']:.1f}, Temp {row.get('soil_temp_c', 0):.1f}C] "
    return ctx
# --- CHAT UTILS ---
USER_ICON_SVG = '<svg viewBox="0 0 24 24" fill="%234EDEA3" xmlns="http://www.w3.org/2000/svg"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>'

def format_ag_markdown(text):
    """Refined Forensic Markdown-to-HTML Parser: Handles Tables, Headers, Bold, and Bullets."""
    import re
    # 1. Headers (### or ##) -> Silkscreen Titles
    text = re.sub(r'###\s+(.*)', r'<div style="font-family:Silkscreen; font-size:1.1rem; color:var(--primary); margin: 15px 0 10px 0;">\1</div>', text)
    text = re.sub(r'##\s+(.*)', r'<div style="font-family:Silkscreen; font-size:1.3rem; color:var(--primary); margin: 20px 0 12px 0;">\1</div>', text)
    
    # 2. Markdown Tables (| cell | cell |)
    lines = text.split('\n')
    in_table = False
    table_rows = []
    final_lines = []
    
    for line in lines:
        if '|' in line and line.count('|') >= 2:
            if not in_table:
                in_table = True
                table_rows = []
            # Clean up the row
            cells = [c.strip() for c in line.split('|') if c.strip() or line.split('|').index(c) not in [0, len(line.split('|'))-1]]
            if cells and not all(set(c) <= set('-:| ') for c in cells): # Ignore separator lines
                table_rows.append(cells)
        else:
            if in_table:
                # Flush the table
                html_table = "<div style='overflow-x:auto; margin:10px 0; border:2px solid #3e2723; border-radius:4px;'>"
                html_table += "<table style='width:100%; border-collapse:collapse; background:rgba(0,0,0,0.4); font-size:0.85rem;'>"
                for i, row in enumerate(table_rows):
                    bg = "rgba(78,222,163,0.1)" if i == 0 else "transparent"
                    weight = "bold" if i == 0 else "normal"
                    color = "#4EDEA3" if i == 0 else "#F8FAFC"
                    html_table += f"<tr style='background:{bg}; border-bottom:1px solid #3e2723;'>"
                    for cell in row:
                        html_table += f"<td style='padding:8px; border-right:1px solid #3e2723; color:{color}; font-weight:{weight};'>{cell}</td>"
                    html_table += "</tr>"
                html_table += "</table></div>"
                final_lines.append(html_table)
                in_table = False
            final_lines.append(line)
    
    if in_table: # Handle trailing table
        # (Same flush logic)
        html_table = "<div style='overflow-x:auto; margin:10px 0; border:2px solid #3e2723; border-radius:4px;'><table style='width:100%; border-collapse:collapse; background:rgba(0,0,0,0.4); font-size:0.85rem;'>"
        for i, row in enumerate(table_rows):
            bg = "rgba(78,222,163,0.1)" if i == 0 else "transparent"
            weight = "bold" if i == 0 else "normal"
            html_table += f"<tr style='background:{bg}; border-bottom:1px solid #3e2723;'>"
            for cell in row: html_table += f"<td style='padding:8px; border-right:1px solid #3e2723;'>{cell}</td>"
            html_table += "</tr>"
        html_table += "</table></div>"
        final_lines.append(html_table)
        
    text = '\n'.join(final_lines)
    
    # 3. Bold (**text**)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # 4. Bullets
    text = re.sub(r'^\s*[\-\*]\s+(.*)', r'• \1', text, flags=re.MULTILINE)
    # 5. Final Newlines
    text = text.replace('\n', '<br>')
    return text

def render_chat_messages(thinking=False):
    chat_data = st.session_state.get("chat", [])
    last_content = None
    last_role = None
    
    for m in chat_data:
        role = m.get("role", "user")
        content = m.get("content") or ""
        
        # Visual Deduplicator: Don't render identical consecutive messages from the same role
        if role == last_role and content == last_content:
            continue
        
        last_role = role
        last_content = content
        formatted = format_ag_markdown(content)
        if role == "user":
            st_html(f"<div class='user-msg-container'><img src='data:image/svg+xml,{USER_ICON_SVG}' class='profile-img'><div class='msg-bubble user-bubble'>{formatted}</div></div>")
        else:
            st_html(f"<div class='ai-msg-container'><img src='data:image/png;base64,{AI_ICON_B64}' class='profile-img'><div class='msg-bubble ai-bubble'>{formatted}</div></div>")
    
    if thinking:
        st_html(f"<div class='ai-msg-container'><img src='data:image/png;base64,{AI_ICON_B64}' class='profile-img'><div class='msg-bubble thinking-bubble'><div class='forensic-spinner'></div> ANALYZING SENSOR STREAMS...</div></div>")

def render_chat_widget(stats_df):
    # Establish State Guards (MID = Message ID)
    if "last_processed_mid" not in st.session_state: st.session_state.last_processed_mid = None

    # 1. Floating Mascot (FAB)
    st.markdown("<div id='fab-anchor-id'></div>", unsafe_allow_html=True)
    if st.button("Consult with AI", key="junimo_fab_btn", help="Engage Farm Intelligence"):
        st.session_state.chat_open = not st.session_state.get("chat_open", False)
        st.rerun()

    # 2. Chat Panel
    if st.session_state.get("chat_open", False):
        with st.container():
            st.markdown("<div id='chat-panel-anchor-id'></div>", unsafe_allow_html=True)
            st_html(f"<div class='chat-header-bar'><img src='data:image/png;base64,{AI_ICON_B64}' style='width:48px;height:48px;image-rendering:pixelated;'><span>FIELD AI ADVISOR</span></div>")
            
            # --- INSTANT PROMPT PROCESSING (TOP) ---
            if prompt := st.chat_input("Input forensic query...", key="chat_widget_input"):
                timestamp_id = f"msg_{time.time()}"
                if not st.session_state.get("ai_thinking", False):
                    st.session_state.chat.append({"role": "user", "content": prompt, "mid": timestamp_id})
                    st.session_state.ai_thinking = True
                    # NO RERUN HERE: Let the same run display the message below

            with st.container(height=420):
                # Now render messages (including any new prompt from above)
                render_chat_messages(thinking=st.session_state.get("ai_thinking", False))
                
                # If thinking, execute the AI forensic fetch
                if st.session_state.get("ai_thinking", False):
                    try:
                        agro = AIAgronomist(GEMINI_API_KEY)
                        context = generate_farm_context(stats_df)
                        history = st.session_state.chat[-8:]
                        user_msg = st.session_state.chat[-1]["content"] if st.session_state.chat else ""
                        
                        # Guard: Prevent double-processing same ID
                        current_mid = st.session_state.chat[-1].get("mid", "unknown")
                        if st.session_state.chat[-1]["role"] == "user" and current_mid != st.session_state.last_processed_mid:
                            reply = agro.get_response(user_msg, history[:-1], context=context)
                            st.session_state.chat.append({"role": "assistant", "content": reply, "mid": f"ai_{current_mid}"})
                            st.session_state.last_processed_mid = current_mid
                    finally:
                        st.session_state.ai_thinking = False
                        st.rerun() # Refresh to show AI response


# --- COMPONENTS ---
def st_html(html_str):
    """Utility to inject raw HTML or Style into the app."""
    st.markdown(html_str, unsafe_allow_html=True)

def render_header():
    logo_part = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:100px;">' if LOGO_B64 else ""
    st_html(f"""
        <div class="brand-header">
            {logo_part}
            <div class="brand-title" style="margin:0 !important; line-height:1.2 !important;">PRECISION EARTH MONITOR</div>
        </div>
    """)

def get_crop_visual(row):
    status = row['overall_status']
    m_status = row['moisture_status']
    ec_status = row['ec_status']
    ph_status = row['ph_status']
    if status == 'Optimal': return "grphics/healthy_crop.png", "#4edea3"
    if m_status == 'Critical': return "grphics/dryingtodie_crop.png", "#ef4444"
    if ec_status == 'Critical': return "grphics/salty_stressed.png", "#ef4444"
    if ph_status == 'Critical': return "grphics/pH Imbalance.png", "#ef4444"
    if m_status == 'Warning': return "grphics/dry_corp.png", "#fbbf24"
    if ec_status == 'Warning': return "grphics/salty_stressed.png", "#fbbf24"
    if ph_status == 'Warning': return "grphics/pH Imbalance.png", "#fbbf24"
    return "grphics/dry_corp.png", "#fbbf24"

@st.dialog("Digital Twin Audit", width="large")
def render_plot_detail(plot_id, stats_row):
    c_img, c_data = st.columns([1, 2], gap="large")
    with c_img:
        path, _ = get_crop_visual(stats_row)
        st.image(path, caption=f"FIELD NODE: {plot_id}", use_container_width=True)
        st_html(f"<div style='text-align:center; font-family:Silkscreen; color:var(--primary); font-size:1.2rem;'>STATUS: {stats_row['overall_status']}</div>")
    with c_data:
        st.subheader(f"Sensor Streams: {plot_id}")
        st.caption("Fulfilling Forensic Telemetry Standards")
        m_col, s_col = st.columns(2)
        p_col, t_col = st.columns(2)
        m_col.metric("Moisture", f"{stats_row['soil_moisture_pct']:.1f}%", stats_row['moisture_status'])
        s_col.metric("Salinity", f"{stats_row['soil_ec_ds_m']:.2f}", stats_row['ec_status'], delta_color="inverse")
        p_col.metric("Acidity", f"{stats_row['soil_ph']:.2f}", stats_row['ph_status'])
        t_col.metric("Thermal", f"{stats_row.get('soil_temp_c', 0):.1f} °C")
        st.divider()
        if st.button("EXECUTE AI FORENSIC SCAN", type="primary", width="stretch"):
            with st.spinner("Decoding sensor streams..."):
                agro = AIAgronomist(GEMINI_API_KEY)
                res = agro.get_response(f"Audit {plot_id}. Moisture: {stats_row['soil_moisture_pct']:.1f}%, EC: {stats_row['soil_ec_ds_m']:.2f}, pH: {stats_row['soil_ph']:.1f}, Temp: {stats_row.get('soil_temp_c',0):.1f}C.")
                formatted_res = format_ag_markdown(res)
                st_html(f"""
                <div style='background:rgba(78,222,163,0.05); border:3px solid var(--primary-dim); border-radius:4px; padding:20px; box-shadow:6px 6px 0px rgba(0,0,0,0.3);'>
                    <h4 style='font-family:Silkscreen; color:var(--primary); margin-top:0; letter-spacing:1px;'>NODE {plot_id} - FORENSIC NOTE</h4>
                    <div style='color:#F8FAFC; line-height:1.7; font-size:0.95rem;'>{formatted_res}</div>
                </div>
                """)

def render_farm_map(df, stats):
    st.subheader("Field Asset Repository")
    cols = st.columns(3)
    for i, (_, row) in enumerate(stats.iterrows()):
        p_id = row['plot_id']
        path, color = get_crop_visual(row)
        b64 = get_base64_img(path)
        
        m_badge = "badge-crit" if row['moisture_status']=='Critical' else ("badge-warn" if row['moisture_status']=='Warning' else "")
        ec_badge = "badge-crit" if row['ec_status']=='Critical' else ("badge-warn" if row['ec_status']=='Warning' else "")
        ph_badge = "badge-crit" if row['ph_status']=='Critical' else ("badge-warn" if row['ph_status']=='Warning' else "")
        
        with cols[i % 3]:
            st_html(f"""
                <div class="farm-tile">
                    <img src="data:image/png;base64,{b64}" class="tile-photo-full">
                    <div class="status-tag" style="background:{color};">{row['overall_status'].upper()}</div>
                    <div class="tile-overlay">
                        <div class="label-tech">{p_id} FORENSICS</div>
                        <div class="metric-line"><span>Moisture</span><span class="{m_badge}">{row['soil_moisture_pct']:.1f}%</span></div>
                        <div class="metric-line"><span>Salinity</span><span class="{ec_badge}">{row['soil_ec_ds_m']:.2f} EC</span></div>
                        <div class="metric-line"><span>Chemistry</span><span class="{ph_badge}">{row['soil_ph']:.2f} pH</span></div>
                        <div class="metric-line"><span>Thermal</span><span>{row.get('soil_temp_c', 0):.1f}°C</span></div>
                    </div>
                </div>
            """)
            if st.button(f"SENSOR HUB | {p_id}", key=f"osh_{p_id}", width="stretch"):
                st.session_state.selected_plot = p_id
                st.rerun()

def render_protocols(stats):
    st_html("<div class='label-tech'>Manual Hardware Callbacks</div>")
    p_id = st.selectbox("Select Target Field Node", stats['plot_id'].unique())
    
    ca, cb, cc = st.columns(3)
    with ca:
        if st.button(f"Trigger Irrigation::{p_id}", use_container_width=True):
            with st.status(f"Transmitting to {p_id}...", expanded=True) as s:
                st.write("Initializing Solenoid Valve...")
                time.sleep(0.5)
                st.write("Confirming Water Pressure...")
                time.sleep(0.5)
                st.write("Pulsing Hydraulic Lines...")
                time.sleep(0.5)
                s.update(label="Action Complete: Irrigation Pulse Successful", state="complete")
    with cb:
        if st.button(f"Flush Soil::{p_id}", use_container_width=True):
            with st.status(f"Transmitting to {p_id}...", expanded=True) as s:
                st.write("Injecting Desalination Wash...")
                time.sleep(0.5)
                st.write("Extracting Brine Samples...")
                time.sleep(0.5)
                s.update(label="Action Complete: EC Drift Corrected", state="complete")
    with cc:
        if st.button(f"Inject pH Buffer::{p_id}", use_container_width=True):
            with st.status(f"Transmitting to {p_id}...", expanded=True) as s:
                st.write("Calibrating pH Regulator...")
                time.sleep(0.5)
                st.write("Dispensing Carbonate Buffer...")
                time.sleep(0.5)
                s.update(label="Action Complete: Soil Chemistry Balanced", state="complete")

def render_evolution():
    st_html("<div class='label-tech'>Pierre's Exotic Research Lab</div>")
    items = [
        {"name": "Iridium pH Probe", "price": "5000G", "effect": "Ultra-low drift diagnostic probe for high-alkalinity environments. Increases sampling resolution by 40%.", "img": "grphics/ph_probe.png"},
        {"name": "Glow-Silt EC Probe", "price": "3500G", "effect": "Enhanced ionic mobility detection. Capable of mapping salinity gradients in hyper-compact soil.", "img": "grphics/ec_flask.png"},
        {"name": "Ancient Seed Matrix", "price": "9000G", "effect": "Neural-net botanical synchronization. Bridges all field nodes into a single autonomous forensic hive.", "img": "grphics/seed_matrix.png"}
    ]
    for item in items:
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 4, 1])
            c1.image(item['img'], width=80)
            c2.markdown(f"**{item['name']}**  \n*{item['effect']}*")
            c3.button("PURCHASE", key=item['name']+"_shop", width="stretch")

def main():
    if "chat" not in st.session_state: st.session_state.chat = []
    if "chat_open" not in st.session_state: st.session_state.chat_open = False
    if "last_processed_mid" not in st.session_state: st.session_state.last_processed_mid = None
    if "selected_plot" not in st.session_state: st.session_state.selected_plot = None
    if "bg_mode" not in st.session_state: st.session_state.bg_mode = "day"
    if "hub_mode" not in st.session_state: st.session_state.hub_mode = "Live Readings"
    if "music_on" not in st.session_state: st.session_state.music_on = True
    if "first_visit" not in st.session_state: st.session_state.first_visit = True
    if "researcher_name" not in st.session_state: st.session_state.researcher_name = "Researcher"

    # 1. STYLE INJECTION (TOP)
    bg_path = f"grphics/bg_{st.session_state.bg_mode}.png"
    bg_b64 = get_base64_img(bg_path)
    overlay_path = "grphics/enter_overlay.png"
    overlay_b64 = get_base64_img(overlay_path)
    st_html(get_style(bg_b64, AI_ICON_B64, overlay_b64))

    # ── 2. STATION AUTHORIZATION (Native Input) ────────────────────
    if st.session_state.first_visit:
        st.markdown("<div style='height:15vh;'></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            auth_cont = st.container(border=True)
            with auth_cont:
                # The Secure Anchor
                st.markdown('<div id="auth-gate"></div>', unsafe_allow_html=True)
                
                st.markdown(f"<div style='text-align:center; padding:10px;'><img src='data:image/png;base64,{LOGO_B64}' style='height:120px;'></div>", unsafe_allow_html=True)
                st.markdown("<h1 style='text-align:center; font-family:Silkscreen; color:#4EDEA3; margin-top:20px; font-size:2.5rem;'>STATION AUTH</h1>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#ccc; margin-bottom:40px; font-size:1.1rem;'>Please verify your researcher credentials.</p>", unsafe_allow_html=True)
                
                # Use a specific div for the input to ensure it's themed correctly
                st.markdown("<div style='margin-bottom:10px;'>", unsafe_allow_html=True)
                name = st.text_input("IDENTIFICATION NAME", placeholder="Type Designation...", key="name_input")
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
                if st.button("INITIALIZE FORENSIC FEED", key="auth_btn", use_container_width=True):
                    if name:
                        st.session_state.researcher_name = name
                        st.session_state.first_visit = False
                        st.rerun()
                    else:
                        st.warning("Identification name is required for access.")
        st.stop()

    # ── 3. Sidebar (Simplified) ──────────────────────────────────
    with st.sidebar:
        if LOGO_B64:
            st.markdown(f"<div style='text-align:center; padding:30px;'><img src='data:image/png;base64,{LOGO_B64}' style='height:200px;'></div>", unsafe_allow_html=True)
        
        # MEANINGFUL NAME DISPLAY
        name = st.session_state.get("researcher_name", "Researcher").upper()
        st.markdown(f"""
            <div style="background:rgba(78, 222, 163, 0.05); border:1px solid rgba(78, 222, 163, 0.2); border-radius:4px; padding:15px; margin-bottom:20px;">
                <div style="font-family:'Silkscreen'; color:#4EDEA3; font-size:0.8rem; opacity:0.6;">IDENTIFIED AS</div>
                <div style="font-family:'Silkscreen'; color:#fff; font-size:1.1rem; letter-spacing:1px; margin-top:5px;">{name}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### LAB MONITOR v15")

        uploaded_file = st.file_uploader("📂 Ingest Core Samples", type=["csv", "xlsx", "xlsm"])
        raw_df = load_data(uploaded_file if uploaded_file else "plantation_soil_data.xlsm")

        st.divider()
        st.markdown("**Field Music**")
        music_icon = "🎵" if st.session_state.music_on else "🔇"
        m_cols = st.columns([1, 2, 1])
        with m_cols[1]:
            if st.button(music_icon, key="music_toggle_btn", help="Field Background Music"):
                st.session_state.music_on = not st.session_state.music_on
                st.rerun()

        st.divider()
        st.markdown("**Environment & Ambience**")
        if st.button("CYCLE AMBIENCE ☀️/🌙", width="stretch", key="ambience_btn"):
            st.session_state.bg_mode = "night" if st.session_state.bg_mode == "day" else "day"
            st.rerun()

        st.divider()
        st.markdown("**Sensor Hub Configuration**")
        hub_mode = st.radio("Field Status View", ["Live Readings", "Field Average"], 
                           index=(0 if st.session_state.hub_mode == "Live Readings" else 1),
                           key="hub_mode_radio")
        
        if hub_mode != st.session_state.hub_mode:
            st.session_state.hub_mode = hub_mode
            st.rerun()

        st.divider()
        # st.caption("💬 Use the 🌱 button (bottom-right) to open your AI Soil Advisor.")

    # ── 4. Main Body ─────────────────────────────────────────────
    latest_stats_all, workbench_df = compute_stats(raw_df)
    render_header()
    if st.session_state.hub_mode == "Live Readings":
        stats = latest_stats_all.copy()
        full_df = workbench_df.copy()
    else:
        # Calculate Field Average for the map status indicators
        avg_raw = workbench_df.groupby('plot_id').mean(numeric_only=True).reset_index()
        avg_raw['timestamp'] = workbench_df['timestamp'].max() 
        # Re-run compute_stats on the averaged data to get status categories
        stats, _ = compute_stats(avg_raw)
        full_df = workbench_df.copy()
    
    tabs = st.tabs(["FIELD MAP", "FORENSIC WORKBENCH", "PROTOCOLS", "EVOLUTION"])
    with tabs[0]: render_farm_map(full_df, stats)
    with tabs[1]: 
        st.subheader("Data Science Master Workbench")
        p_id = st.selectbox("Select Target Plot", workbench_df['plot_id'].unique(), key="wb_plot")
        pdf = workbench_df[workbench_df['plot_id'] == p_id].copy()
        t1, t2, t3 = st.tabs(["TELEMETRIC TRENDS", "HEALTH ENVELOPES", "STAT ANALYSIS"])
        with t1:
            pdf['date'] = pdf['timestamp'].dt.date
            daily_rain = pdf.groupby('date')['rainfall_mm'].sum().reset_index()
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=daily_rain['date'], y=daily_rain['rainfall_mm'], name="Daily Rainfall", 
                                marker_color="#38bdf8", opacity=0.4), secondary_y=True)
            fig.add_trace(go.Scatter(x=pdf['timestamp'], y=pdf['soil_moisture_pct'], name="💧 Moisture (%)", 
                                     mode="lines", fill="none", line=dict(color="#4EDEA3", width=3)), secondary_y=False)
            fig.add_trace(go.Scatter(x=pdf['timestamp'], y=pdf.get('soil_temp_c', 0), name="🌡️ Temp (°C)", 
                                     mode="lines", line=dict(color="#fbbf24", width=3, dash='dot')), secondary_y=False)
            
            fig.update_layout(
                height=400, 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_color="#FFF",
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig.update_xaxes(title_text="Telemetric Timeline")
            fig.update_yaxes(title_text="Primary Metrics (Moisture/Temp)", secondary_y=False)
            fig.update_yaxes(title_text="Rainfall Intensity (mm)", secondary_y=True)
            st.plotly_chart(fig, width="stretch")
            st.subheader("Categorical Heatmap")
            h_data = get_categorical_heatmap_data(workbench_df, p_id)
            h_data['day'] = h_data['timestamp'].dt.strftime('%b %d')
            h_data['hour'] = h_data['timestamp'].dt.hour
            h_pivot = h_data.pivot(index='day', columns='hour', values='moisture_cat')
            st.plotly_chart(px.imshow(h_pivot, color_continuous_scale=[[0, '#ef4444'], [0.5, '#fbbf24'], [1, '#4edea3']]), width="stretch")
        with t2:
            st.subheader("Biological Health Envelopes")
            c1, c2 = st.columns(2)
            with c1:
                fig2 = px.scatter(pdf, x='soil_ph', y='soil_ec_ds_m', trendline="ols", trendline_color_override="#4EDEA3", title="Salinity vs pH Envelope")
                fig2.add_hline(y=3.73, line_dash="dash", line_color="#ef4444")
                fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', font_color="#FFF")
                st.plotly_chart(fig2, width="stretch")
            with c2:
                fig_t = px.scatter(pdf, x='soil_moisture_pct', y='soil_temp_c', trendline="lowess", trendline_color_override="#fbbf24", title="Thermal vs Moisture Envelope")
                fig_t.update_layout(plot_bgcolor='rgba(0,0,0,0)', font_color="#FFF")
                st.plotly_chart(fig_t, width="stretch")
        with t3:
            corr_df = pdf[['soil_moisture_pct', 'soil_ec_ds_m', 'soil_ph', 'soil_temp_c', 'rainfall_mm', 'lagged_rainfall_mm']].corr()
            st.plotly_chart(px.imshow(corr_df, text_auto=".2f", color_continuous_scale="Viridis"), width="stretch")
    with tabs[2]: render_protocols(stats)
    with tabs[3]: render_evolution()
    
    if st.session_state.selected_plot:
        p_id = st.session_state.selected_plot
        try:
            s_row = stats[stats['plot_id'] == p_id].iloc[0]
            st.session_state.selected_plot = None
            render_plot_detail(p_id, s_row)
        except:
            st.session_state.selected_plot = None

    # Floating Chat Widget
    render_chat_widget(stats)

    # ── 6. Audio Injection ───────────────────────────────────────
    music_file = "music/MP3Now.com_YouTube_Stardew-Valley-OST-Fall-The-Smell-of-Mus_Media_omVFjGHx0FQ_009_128k.mp3"
    render_bgm(music_file, play=st.session_state.music_on)

if __name__ == "__main__":
    main()
