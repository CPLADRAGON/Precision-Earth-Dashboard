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
import random
import numpy as np
from datetime import datetime
from dashboard_logic import load_data, compute_stats, get_categorical_heatmap_data

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    # If using local .streamlit/secrets.toml or if key is missing
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

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
@st.cache_data
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
    
    /* Absolute Sidebar Persistence & Scroll Fix (Scale for Mobile) */
    [data-testid="stSidebar"] {{
        transform: none !important;
        visibility: visible !important;
        min-width: 350px !important;
        max-width: 350px !important;
    }}
    @media (max-width: 768px) {{
        [data-testid="stSidebar"] {{
            min-width: 100% !important;
            max-width: 100% !important;
        }}
    }}
    section[data-testid="stSidebar"] > div:first-child {{
        min-width: 350px !important;
    }}
    @media (max-width: 768px) {{
        section[data-testid="stSidebar"] > div:first-child {{
            min-width: 100% !important;
        }}
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
    @media (max-width: 768px) {{
        .brand-header {{
            padding: 15px 20px !important;
            min-height: 100px !important;
            gap: 15px !important;
        }}
        .brand-title {{
            font-size: 1.2rem !important;
        }}
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
    }}    /* 1. FORENSIC AI COMMANDER BUTTON (Sidebar Center) */
    button[key="junimo_fab_btn"] {{
        background: linear-gradient(180deg, #1a2a26 0%, #0d1513 100%) !important;
        border: 2px solid var(--primary) !important;
        color: var(--primary) !important;
        font-family: 'Silkscreen' !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        padding: 15px 25px !important;
        border-radius: 4px !important;
        box-shadow: 0 0 15px rgba(78, 222, 163, 0.3) !important;
        width: 100% !important;
        height: auto !important;
        transition: all 0.3s ease !important;
    }}
    button[key="junimo_fab_btn"]:hover {{
        transform: scale(1.02) !important;
        box-shadow: 0 0 25px var(--primary) !important;
        background: var(--primary) !important;
        color: #0d1513 !important;
    }}

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
        background: linear-gradient(180deg, #1a2a26 0%, #0d1513 100%) !important;
        border: 2px solid var(--primary) !important;
        color: var(--primary) !important;
        font-family: 'Silkscreen' !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        padding: 15px 25px !important;
        border-radius: 4px !important;
        box-shadow: 0 0 15px rgba(78, 222, 163, 0.3) !important;
        width: 100% !important;
        height: auto !important;
        transition: all 0.3s ease !important;
    }}
    button[key="junimo_fab_btn"]:hover {{ 
        transform: scale(1.02) !important;
        box-shadow: 0 0 25px var(--primary) !important;
        background: var(--primary) !important;
        color: #0d1513 !important;
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

    /* Tab Forensic Overhaul (v15.5) */
    button[data-baseweb="tab"] {{
        font-size: 1.1rem !important;
        padding: 12px 24px !important;
        font-family: 'Silkscreen', cursive !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        color: rgba(255,255,255,0.6) !important;
        border: none !important;
        background: transparent !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--primary) !important;
        text-shadow: 0 0 10px rgba(78,222,163,0.5) !important;
    }}
    button[data-baseweb="tab"]:hover {{
        color: #FFF !important;
        background: rgba(78,222,163,0.1) !important;
    }}
    div[data-baseweb="tab-highlight"] {{
        background-color: var(--primary) !important;
        height: 6px !important;
        box-shadow: 0 0 20px var(--primary) !important;
        border-radius: 3px !important;
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
        max-width: 92%; /* Increased v17.3 */
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

    /* 4. INDUSTRIAL METRIC FRAMING (v15.5) */
    [data-testid="stMetric"] {{
        background: #0D1513 !important;
        border: 2px solid var(--primary-dim) !important;
        border-radius: 8px !important;
        padding: 15px 20px !important;
        box-shadow: inset 0 0 20px rgba(78,222,163,0.05), 0 4px 15px rgba(0,0,0,0.4) !important;
        transition: all 0.3s ease !important;
    }}
    [data-testid="stMetric"]:hover {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 25px rgba(78,222,163,0.2) !important;
        transform: translateY(-2px);
    }}
    [data-testid="stMetricValue"] div {{
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        color: #FFF !important;
        font-size: 2.2rem !important;
    }}
    [data-testid="stMetricLabel"] p {{
        font-family: 'Silkscreen' !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: var(--primary) !important;
        opacity: 0.8 !important;
    }}

    /* 5. RADIO BUTTON WOODIFICATION (v15.5) */
    div[data-testid="stRadio"] label {{
        font-family: 'Silkscreen' !important;
        color: #FFF !important;
    }}
    div[data-testid="stRadio"] div[role="radiogroup"] > label {{
        background: #7d5233 !important;
        border: 3px solid #3e2723 !important;
        padding: 10px 15px !important;
        margin: 5px 0 !important;
        border-radius: 4px !important;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.5) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        display: block !important;
        width: 100% !important;
    }}
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {{
        background: #8d6e63 !important;
        transform: translateX(4px);
    }}
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {{
        background: #5d4037 !important;
        border-color: var(--primary) !important;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.8) !important;
        transform: translate(2px, 2px);
    }}

    .label-tech {{ 
        font-family: 'Silkscreen', cursive; 
        font-size: 0.9rem; 
        color: var(--primary); 
        letter-spacing: 2px;
        margin-bottom: 8px;
    }}

    /* v15.8 Forensic 'Lens' Polish */
    @keyframes forensic-pulse {{
        0% {{ transform: scale(1); box-shadow: 0 0 10px rgba(78,222,163,0.3); }}
        50% {{ transform: scale(1.05); box-shadow: 0 0 18px rgba(78,222,163,0.6); }}
        100% {{ transform: scale(1); box-shadow: 0 0 10px rgba(78,222,163,0.3); }}
    }}

    div[data-testid="stPopover"] button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        width: 32px !important;
        height: 32px !important;
        min-width: 32px !important;
        max-width: 32px !important;
        padding: 0 !important;
        margin-left: 5px !important; /* Breathing Room: Tight but No Overlap */
        color: var(--primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: bold !important;
        font-size: 2.2rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease;
        overflow: hidden !important; 
        line-height: 1 !important;
    }}
    /* Vaporize the default Streamlit Header Anchors (🔗) */
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a {{
        display: none !important;
    }}
    /* Hard-Center the larger glyph */
    div[data-testid="stPopover"] button > div:nth-child(1) {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 32px !important;
        min-width: 32px !important;
        margin-left: -1px !important;
    }}
    /* Ultimate Nuke for chevron */
    div[data-testid="stPopover"] button svg,
    div[data-testid="stPopover"] button [data-testid="stIcon"],
    div[data-testid="stPopover"] button div:nth-child(2) {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
        position: absolute !important;
        left: -100px !important;
    }}
    div[data-testid="stPopover"] button:hover {{
        background: transparent !important;
        filter: drop-shadow(0 0 15px var(--primary));
        transform: scale(1.1);
    }}
    /* Neutralize the second child (where the arrow lives) */
    div[data-testid="stPopover"] button > div:nth-child(2),
    div[data-testid="stPopover"] button svg,
    div[data-testid="stPopover"] button [data-testid="stIcon"],
    div[data-testid="stPopover"] button span:empty,
    div[data-testid="stPopover"] button i {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        position: absolute !important;
        visibility: hidden !important;
    }}
    div[data-testid="stPopover"] button:hover {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 25px var(--primary) !important;
        animation: none;
        transform: scale(1.1) rotate(10deg);
    }}
    /* The Popover Card Content: Target the baseui portal style */
    div[data-baseweb="popover"] {{
        background-color: #0D1513 !important;
        border: 2px solid var(--primary) !important;
        border-radius: 8px !important;
        box-shadow: 8px 8px 0px rgba(0,0,0,0.5) !important;
    }}
    div[data-baseweb="popover"] p, div[data-baseweb="popover"] span {{
        color: #F8FAFC !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }}
    /* Caption forensic override */
    .stCaption p {{
        font-family: 'Plus Jakarta Sans' !important;
        color: rgba(255,255,255,0.7) !important;
        font-style: italic !important;
        line-height: 1.2 !important;
        margin-top: -5px !important;
        letter-spacing: 0.2px !important;
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
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction="Professional Ag-Forensic Lead. Concise, data-driven. Use the provided FIELD CONTEXT to answer plot-specific questions. Focus on Lagged Rainfall and Health Envelopes."
                )
            )
            return response.text
        except Exception as e:
            err_msg = str(e)
            if "PERMISSION_DENIED" in err_msg or "403" in err_msg:
                return "⚠️ **SECURE ACCESS DENIED**: Your API Key is invalid or has been revoked (possibly due to a leak). Please rotate your key in Streamlit Secrets."
            if "NOT_FOUND" in err_msg or "404" in err_msg:
                return f"⚠️ **MODEL NOT FOUND**: The model `{self.model_id}` is unavailable. Attempting fallback..."
            return f"⚠️ **AI CORE ERROR**: {err_msg}"

# --- CHAT UTILS ---
def generate_farm_context(stats, full_df=None):
    if stats is None or (isinstance(stats, pd.DataFrame) and stats.empty): 
        return "Field status unknown: Awaiting sensor calibration."
    
    # 1. CURRENT SNAPSHOT BRIEFING
    ctx = "--- [FORENSIC DATA LEDGER] ---\n"
    ctx += "1. CURRENT STATUS:\n"
    for _, row in stats.iterrows():
        ctx += f"[{row['plot_id']}: {row['overall_status']}, Moisture {row['soil_moisture_pct']:.1f}%, EC {row['soil_ec_ds_m']:.2f}, pH {row['soil_ph']:.1f}, Temp {row.get('soil_temp_c', 0):.1f}C]\n"
    
    # 2. FULL-SPECTRUM FORENSIC ANALYSIS (v18.5)
    if full_df is not None and not full_df.empty:
        ctx += "\n2. 24H STATISTICAL ENVELOPES:\n"
        # Calculate 24h stats for each plot
        cols = ['soil_moisture_pct', 'soil_ec_ds_m', 'soil_ph', 'soil_temp_c']
        grouped = full_df.groupby('plot_id')[cols].agg(['min', 'max', 'mean'])
        for pid, s in grouped.iterrows():
            ctx += f"- {pid} Envelopes:\n"
            ctx += f"  - Moisture: Range [{s[('soil_moisture_pct', 'min')]:.1f}, {s[('soil_moisture_pct', 'max')]:.1f}] Mean {s[('soil_moisture_pct', 'mean')]:.1f}\n"
            ctx += f"  - EC (Salinity): Range [{s[('soil_ec_ds_m', 'min')]:.2f}, {s[('soil_ec_ds_m', 'max')]:.2f}] Mean {s[('soil_ec_ds_m', 'mean')]:.2f}\n"
            ctx += f"  - pH: Range [{s[('soil_ph', 'min')]:.1f}, {s[('soil_ph', 'max')]:.1f}] Mean {s[('soil_ph', 'mean')]:.1f}\n"

        # 3. FORENSIC LANDMARKS (Recent Rate of Change)
        ctx += "\n3. RECENT RATE OF CHANGE (LAST 2HRS):\n"
        # Simplified trend detection 
        for pid in full_df['plot_id'].unique():
            p_data = full_df[full_df['plot_id'] == pid].tail(10) # Last 10 readings
            if len(p_data) >= 2:
                m_change = p_data['soil_moisture_pct'].iloc[-1] - p_data['soil_moisture_pct'].iloc[0]
                e_change = p_data['soil_ec_ds_m'].iloc[-1] - p_data['soil_ec_ds_m'].iloc[0]
                ctx += f"- {pid}: Moisture {'▲' if m_change > 0 else '▼'} {abs(m_change):.1f}%, EC {'▲' if e_change > 0 else '▼'} {abs(e_change):.2f}\n"

    # 4. HARDWARE STATUS HUB (v19.0)
    if "iot_devices" in st.session_state:
        ctx += "\n4. HARDWARE OPERATING STATUS:\n"
        for d in st.session_state.iot_devices:
            ctx += f"- {d['id']} ({d['type']}): {d['status']} [Signal: {d['signal']}, Battery: {d['battery']}%]\n"
    
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

def render_chat_widget(stats_df, full_df=None, wide_mode=False):
    if "last_processed_mid" not in st.session_state: st.session_state.last_processed_mid = None

    if not wide_mode:
        # --- SIDEBAR BUTTON MODE ---
        c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
        with c2:
            st.button("Consult with AI", key="junimo_fab_btn", width="stretch", help="Switch to AI Advisor Tab")
            st.caption("Select the **'AI ADVISOR'** tab above to begin.")
    else:
        # --- WIDE-SCREEN TAB MODE ---
        st_html(f"<div style='border-bottom: 2px solid var(--primary); padding-bottom:10px; margin-bottom:30px;'><h2 style='font-family:Silkscreen; color:var(--primary); margin:0;'>FORENSIC ADVISOR TERMINAL</h2><p style='color:#ccc; opacity:0.7;'>Large-Scale Strategic Intelligence Hub</p></div>")
        
        # ── LLM MODEL INFORMATION (v18.0) ──
        st.caption("INTELLIGENCE ENGINE: Gemini-3.1-Flash-Lite (ULTRA-LOW LATENCY FORENSIC MODEL)")
        
        # ── AI QUICK-SCAN BUTTONS (NEW) ──
        st_html("<div class='label-tech' style='font-size:0.7rem; margin-bottom:5px;'>Forensic Quick-Actions</div>")
        qa_cols = st.columns(3)
        with qa_cols[0]:
            if st.button("🔍 ANALYZE ANOMALIES", key="qa_anomalies", width="stretch"):
                st.session_state.chat.append({"role": "user", "content": "Analyze the current telemetry for anomalies across all plots.", "mid": f"qa_{time.time()}"})
                st.session_state.ai_thinking = True
                st.rerun()
        with qa_cols[1]:
            if st.button("🌧️ RAINFALL IMPACT", key="qa_rain", width="stretch"):
                st.session_state.chat.append({"role": "user", "content": "Evaluate the impact of recent rainfall on soil moisture and EC levels.", "mid": f"qa_{time.time()}"})
                st.session_state.ai_thinking = True
                st.rerun()
        with qa_cols[2]:
            if st.button("📈 PLOT SUMMARY", key="qa_summary", width="stretch"):
                st.session_state.chat.append({"role": "user", "content": "Provide a high-level summary of all plot health statuses.", "mid": f"qa_{time.time()}"})
                st.session_state.ai_thinking = True
                st.rerun()

        if prompt := st.chat_input("Input forensic query for plot analysis...", key="tab_chat_input"):
            timestamp_id = f"msg_{time.time()}"
            if not st.session_state.get("ai_thinking", False):
                st.session_state.chat.append({"role": "user", "content": prompt, "mid": timestamp_id})
                st.session_state.ai_thinking = True


        chat_container = st.container(height=650) # Taller for the tab
        with chat_container:
            render_chat_messages(thinking=st.session_state.get("ai_thinking", False))
            
            if st.session_state.get("ai_thinking", False):
                try:
                    agro = AIAgronomist(GEMINI_API_KEY)
                    context = generate_farm_context(stats_df, full_df)
                    history = st.session_state.chat[-10:]
                    user_msg = st.session_state.chat[-1]["content"] if st.session_state.chat else ""
                    
                    current_mid = st.session_state.chat[-1].get("mid", "unknown")
                    if st.session_state.chat[-1]["role"] == "user" and current_mid != st.session_state.last_processed_mid:
                        reply = agro.get_response(user_msg, history[:-1], context=context)
                        st.session_state.chat.append({"role": "assistant", "content": reply, "mid": f"ai_{current_mid}"})
                        st.session_state.last_processed_mid = current_mid
                finally:
                    st.session_state.ai_thinking = False
                    st.rerun()

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
    if status == 'Optimal': return "grphics/healthy_crop.jpg", "#4edea3"
    if m_status == 'Critical': return "grphics/dryingtodie_crop.jpg", "#ef4444"
    if ec_status == 'Critical': return "grphics/salty_stressed.jpg", "#ef4444"
    if ph_status == 'Critical': return "grphics/pH Imbalance.jpg", "#ef4444"
    if m_status == 'Warning': return "grphics/dry_corp.jpg", "#fbbf24"
    if ec_status == 'Warning': return "grphics/salty_stressed.jpg", "#fbbf24"
    if ph_status == 'Warning': return "grphics/pH Imbalance.jpg", "#fbbf24"
    return "grphics/dry_corp.jpg", "#fbbf24"

@st.dialog("Digital Twin Audit", width="large")
def render_plot_detail(plot_id, stats_row):
    c_img, c_data = st.columns([1, 2], gap="large")
    with c_img:
        path, _ = get_crop_visual(stats_row)
        st.image(path, caption=f"FIELD NODE: {plot_id}", width="stretch")
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
        
        risk_level = row.get('risk_level', 'Low')
        # Border color synchronized with the OVERALL STATUS of the plot
        border_color = color # From get_crop_visual(row)
        
        # Risk indicators still use risk_level for the internal badge
        risk_badge_color = "#ef4444" if risk_level == "High" else ("#fbbf24" if risk_level == "Medium" else "#4edea3")
        risk_bg = "rgba(239, 68, 68, 0.15)" if risk_level == "High" else ("rgba(251, 191, 36, 0.15)" if risk_level == "Medium" else "rgba(78, 222, 163, 0.15)")
        
        with cols[i % 3]:
            st_html(f"""
                <div class="farm-tile" style="border: 5px solid {border_color}; shadow: 0 0 15px {border_color}33;">
                    <img src="data:image/jpeg;base64,{b64}" class="tile-photo-full">
                    <div class="status-tag" style="background:{color};">{row['overall_status'].upper()}</div>
                    <div class="tile-overlay">
                        <div class="label-tech" style="color:#FFF; background:rgba(0,0,0,0.6); padding:2px 8px; border-radius:4px;">{p_id} FORENSICS</div>
                        <div style="background:{risk_bg}; border-left:4px solid {risk_badge_color}; padding:8px 12px; margin-bottom:10px; border-radius: 0 4px 4px 0; backdrop-filter: blur(2px);">
                            <b style="color:{risk_badge_color}; font-size:0.8rem; letter-spacing:1px;">[{risk_level.upper()} FORENSIC RISK]</b><br>
                            <span style="color:#FFF; font-size:0.7rem; font-weight:600; line-height:1.3;">{row['risk_reason']}</span>
                        </div>
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
        # v16.10 Forensic Alignment
        c_title, c_pop = st.columns([0.8, 0.2], vertical_alignment="center")
        with c_title:
             st.markdown("<p style='margin-bottom:0; font-family:Silkscreen; font-size:0.8rem; color:#4EDEA3; white-space:nowrap;'>Trigger Irrigation</p>", unsafe_allow_html=True)
        with c_pop:
            with st.popover("ⓘ", width="content"):
                st.markdown("**What does this do?**")
                st.write("Ensures steady hydration. Use this if the **Moisture Timeline** shows a steady decline below 30% to prevent root-zone drought stress.")
            
        if st.button(f"INITIALIZE::{p_id}", key=f"irr_{p_id}", width="stretch"):
            with st.status(f"Transmitting to {p_id}...", expanded=True) as s:
                st.write("Establishing Handshake...")
                time.sleep(0.5)
                st.write("Valve Engagement confirmed.")
                s.update(label="Irrigation Pulse Complete!", state="complete")
        st.caption("High-Precision Hydration Pulse.")

    with cb:
        c_title, c_pop = st.columns([0.7, 0.3], vertical_alignment="center")
        with c_title:
            st.markdown("<p style='margin-bottom:0; font-family:Silkscreen; font-size:0.8rem; color:#4EDEA3; white-space:nowrap;'>Flush Soil</p>", unsafe_allow_html=True)
        with c_pop:
            with st.popover("ⓘ", width="content"):
                st.markdown("**What does this do?**")
                st.write("A deep hydraulic purge. Use this if the **Salinity (EC)** levels are too high (indicated by red heatmaps) to wash away excess mineral buildup.")
                

        if st.button(f"EXTRACT::{p_id}", key=f"flush_{p_id}", width="stretch"):
            with st.status(f"Transmitting to {p_id}...", expanded=True) as s:
                st.write("Opening Purge Valves...")
                time.sleep(0.8)
                s.update(label="Soil Flush Cycle Finished.", state="complete")
        st.caption("Intense Hydraulic Purge Cycle.")

    with cc:
        c_title, c_pop = st.columns([0.65, 0.35], vertical_alignment="center")
        with c_title:
            st.markdown("<p style='margin-bottom:0; font-family:Silkscreen; font-size:0.8rem; color:#4EDEA3; white-space:nowrap;'>pH Buffer</p>", unsafe_allow_html=True)
        with c_pop:
            with st.popover("ⓘ", width="content"):
                st.markdown("**What does this do?**")
                st.write("Releases stabilizing agents. Think of this as an **'acid-relief tablet'** for your soil. Use it if your pH probes drop below 6.0.")

        if st.button(f"STABILIZE::{p_id}", key=f"ph_{p_id}", width="stretch"):
            with st.status(f"Transmitting to {p_id}...", expanded=True) as s:
                st.write("Calibrating pH Injectors...")
                time.sleep(0.6)
                s.update(label="Alkaline Pulse Dispatched.", state="complete")
        st.caption("Neutralizes High Soil Acidity.")

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

def render_iot_command():
    st_html("<div style='border-bottom: 2px solid var(--primary); padding-bottom:10px; margin-bottom:30px;'><h2 style='font-family:Silkscreen; color:var(--primary); margin:0;'>IoT COMMAND CENTRE</h2><p style='color:#ccc; opacity:0.7;'>Pierre's Exotic Research Lab Terminal</p></div>")
    
    selected_plot = st.session_state.selected_plot
    
    # Header showing the current focus
    if selected_plot:
        st.markdown(f"**FOCUS:** `FORENSIC_PL_0{selected_plot[-1]}` | showing linked hardware and shared hub.")
    else:
        st.markdown("**FOCUS:** `GLOBAL_NETWORK` | showing all fleet nodes.")

    # ── 1. PROVISIONING HANDSHAKE (MOCKUP) ───────────────────────
    with st.expander("➕ PROVISION NEW HARDWARE LINK", expanded=False):
        c1, c2 = st.columns([2, 1])
        with c1:
            proto = st.selectbox("COMMUNICATION PROTOCOL", ["MQTT (Standard)", "LoRaWAN (Long-Range)", "HTTP POST Gateway"])
            ip_addr = st.text_input("TARGET IP / GATEWAY ADDRESS", placeholder="e.g. 192.168.1.104")
        with c2:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("INITIALIZE LINK", width="stretch"):
                st.session_state.provisioning_step = 1
        
        if st.session_state.provisioning_step > 0:
            steps = ["AUTHENTICATING NODE...", "RSA KEY EXCHANGE...", "SYNCING SENSOR REGISTRY...", "NODE PAIRED"]
            bar = st.progress(0)
            for i, step in enumerate(steps):
                time.sleep(0.4)
                bar.progress((i+1)*25, text=f"FORENSIC STATUS: {step}")
            st.success("HARDWARE LINK ESTABLISHED: Node registered as 'NEW_NODE_X'")
            st.session_state.provisioning_step = 0

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── 2. THE HARDWARE HANGAR (GRID) ───────────────────────────
    # Filtering logic
    all_devices = st.session_state.iot_devices
    if selected_plot:
        # Show linked plot node + global nodes
        devices_to_show = [d for d in all_devices if d['plot'] == selected_plot or d['plot'] == 'GLOBAL']
    else:
        devices_to_show = all_devices

    # Pre-load icons with lru_cache behavior internally
    icons = {
        "Gateway Hub": get_base64_img("grphics/iot_devices/Node Gateway.jpg"),
        "Weather Station": get_base64_img("grphics/iot_devices/Rain Gauge.jpg"),
        "Salinity Node": get_base64_img("grphics/iot_devices/EC Salinity Node.jpg"),
        "Moisture Probe": get_base64_img("grphics/iot_devices/Moisture Probe.jpg"),
        "Thermal Probe": get_base64_img("grphics/iot_devices/Thermal Probe.jpg"),
        "pH Electrode": get_base64_img("grphics/iot_devices/pH Electrode.jpg"),
        "Rain Gauge": get_base64_img("grphics/iot_devices/Rain Gauge.jpg")
    }

    # Use a row-by-row structure to fix visibility issues
    for i in range(0, len(devices_to_show), 2):
        row_cols = st.columns(2)
        for j in range(2):
            if i + j < len(devices_to_show):
                device = devices_to_show[i+j]
                with row_cols[j]:
                    icon_b64 = icons.get(device['type'], icons["Gateway Hub"])
                    
                    is_online = (device["status"] == "Online")
                    status_color = "#4EDEA3" if is_online else "#EF4444"
                    
                    st_html(f"""
                        <div class='iot-card' style='border-color: {status_color if not is_online else "rgba(78, 222, 163, 0.2)"};'>
                            <div style='display:flex; align-items:center; gap:20px;'>
                                <img src='data:image/png;base64,{icon_b64}' style='height:70px; width:70px; image-rendering:pixelated; {"opacity:0.4; grayscale:1;" if not is_online else "filter: drop-shadow(0 0 10px rgba(78,222,163,0.3));"}'>
                                <div style='flex-grow:1;'>
                                    <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                                        <h3 style='margin:0; font-family:Silkscreen; color:{status_color}; font-size:1rem;'>{device['id']}</h3>
                                        <span style='font-size:0.65rem; color:{status_color}; font-weight:bold;'>● {device["status"].upper()}</span>
                                    </div>
                                    <p style='margin:2px 0; font-size:0.75rem; color:#ccc;'>Role: {device['type']}</p>
                                    <p style='margin:2px 0; font-size:0.75rem; color:#888;'>Sector: {device['plot']}</p>
                                    <div style='display:flex; gap:12px; margin-top:5px;'>
                                        <span style='font-size:0.7rem; color:#aaa;'>🔋 {device['battery']}%</span>
                                        <span style='font-size:0.7rem; color:#aaa;'>📶 {device['signal']}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    """)
                    
                    # Tactical Neon Buttons
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if st.button("📡 PING", key=f"ping_{device['id']}", width="stretch"):
                            st.toast(f"PING response from {device['id']}: 24ms", icon="✅")
                    with c2:
                        btn_label = "🔌 SHUTDOWN" if is_online else "⚡ REBOOT"
                        if st.button(btn_label, key=f"tog_{device['id']}", width="stretch"):
                            device['status'] = "OFFLINE" if is_online else "Online"
                            st.rerun()
                    with c3:
                        if st.button("🛠️ CONFIG", key=f"ovr_{device['id']}", width="stretch"):
                            st.sidebar.info(f"Calibration menu for {device['id']} active.")

    st.markdown("""
        <style>
        .iot-card {
            background: rgba(16, 26, 24, 0.7);
            border: 1px solid rgba(78, 222, 163, 0.2);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            transition: all 0.2s ease;
        }
        /* Style Streamlit Buttons to be 'Tactical' */
        div[st-vertical-alignment="center"] > button {
            background-color: transparent !important;
            border: 1px solid rgba(78, 222, 163, 0.3) !important;
            color: #4EDEA3 !important;
            font-family: 'Silkscreen', sans-serif !important;
            font-size: 0.7rem !important;
            text-transform: uppercase !important;
        }
        div[st-vertical-alignment="center"] > button:hover {
            border-color: #4EDEA3 !important;
            background-color: rgba(78, 222, 163, 0.1) !important;
            box-shadow: 0 0 10px rgba(78, 222, 163, 0.2) !important;
        }
        </style>
    """, unsafe_allow_html=True)

def render_themed_ledger(df):
    """Renders data as a Stardew-style wooden journal/ledger."""
    st_html("""
    <style>
        .ledger-container {
            background-color: #f3e5ab; /* Parchment */
            border: 8px solid #5d4037; /* Wooden Border */
            border-radius: 8px;
            padding: 20px;
            box-shadow: 10px 10px 0px rgba(0,0,0,0.3);
            margin-bottom: 20px;
            max-height: 800px;
            overflow-y: auto;
            image-rendering: pixelated;
        }
        .ledger-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #3e2723;
        }
        .ledger-table th {
            background-color: #5d4037;
            color: #fff176;
            font-family: 'Silkscreen', cursive;
            padding: 12px;
            text-align: left;
            position: sticky;
            top: -20px;
            z-index: 10;
        }
        .ledger-table td {
            padding: 10px 12px;
            border-bottom: 1px dashed rgba(62, 39, 35, 0.2);
            font-size: 0.9rem;
        }
        .ledger-table tr:nth-child(even) {
            background-color: rgba(93, 64, 55, 0.05);
        }
        .ledger-table tr:hover {
            background-color: rgba(93, 64, 55, 0.1);
        }
        .status-dot {
            height: 10px;
            width: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }
    </style>
    """)
    
    # Header
    html = '<div class="ledger-container"><table class="ledger-table"><thead><tr>'
    cols = ['timestamp', 'plot_id', 'soil_moisture_pct', 'soil_ec_ds_m', 'soil_ph', 'rainfall_mm']
    for c in cols:
        html += f'<th>{c.replace("_", " ").upper()}</th>'
    html += '</tr></thead><tbody>'
    
    # Rows (Display last 100 for performance)
    for _, row in df.sort_values('timestamp', ascending=False).head(100).iterrows():
        html += '<tr>'
        html += f'<td>{row["timestamp"].strftime("%Y-%m-%d %H:%M")}</td>'
        
        # Color indicator for plot
        p_color = "#4edea3" if row['soil_moisture_pct'] > 20 else "#ef4444"
        html += f'<td><span class="status-dot" style="background-color: {p_color};"></span>{row["plot_id"]}</td>'
        
        html += f'<td>{row["soil_moisture_pct"]:.1f}%</td>'
        html += f'<td>{row["soil_ec_ds_m"]:.2f}</td>'
        html += f'<td>{row["soil_ph"]:.1f}</td>'
        html += f'<td>{row["rainfall_mm"]:.1f} mm</td>'
        html += '</tr>'
        
    html += '</tbody></table></div>'
    st_html(html)

def main():

    if "chat" not in st.session_state: 
        st.session_state.chat = [
            {"role": "assistant", "content": "Greetings, Researcher. I am the **Precision Earth AI Advisor**, powered by **Gemini-3.1-Flash-Lite**. I specialize in real-time sensor telemetry analysis, identifying forensic soil health patterns (pH, EC, Moisture), and recommending automated hardware protocols like **Irrigation pulses** and **pH Neutralization**. I am standing by to assist with your plantation oversight.", "mid": "init_msg"}
        ]
    if "chat_open" not in st.session_state: st.session_state.chat_open = False
    if "last_processed_mid" not in st.session_state: st.session_state.last_processed_mid = None
    if "selected_plot" not in st.session_state: st.session_state.selected_plot = None
    if "bg_mode" not in st.session_state: st.session_state.bg_mode = "day"
    if "hub_mode" not in st.session_state: st.session_state.hub_mode = "Live Readings"
    if "music_on" not in st.session_state: st.session_state.music_on = True
    if "first_visit" not in st.session_state: st.session_state.first_visit = True
    if "researcher_name" not in st.session_state: st.session_state.researcher_name = "Researcher"
    
    # ── IoT DEVICE STATE (v19.6: Full-Spectrum Fleet) ─────────────
    if "iot_devices" not in st.session_state:
        devices = []
        plot_ids = ["PL_01", "PL_02", "PL_03"]
        device_configs = [
            {"type": "Gateway Hub", "id_prefix": "GW"},
            {"type": "Moisture Probe", "id_prefix": "MS"},
            {"type": "pH Electrode", "id_prefix": "PH"},
            {"type": "Salinity Node", "id_prefix": "EC"},
            {"type": "Thermal Probe", "id_prefix": "TH"},
            {"type": "Rain Gauge", "id_prefix": "RG"}
        ]
        
        for p_id in plot_ids:
            for config in device_configs:
                devices.append({
                    "id": f"{config['id_prefix']}-{p_id[-2:]}",
                    "plot": p_id,
                    "status": "Online",
                    "battery": random.randint(75, 100),
                    "signal": random.choice(["Excellent", "Good", "Balanced"]),
                    "type": config['type']
                })
        
        # Add Global Weather Station
        devices.append({"id": "MET-STATION M1", "plot": "GLOBAL", "status": "Online", "battery": 100, "signal": "Satellite", "type": "Weather Station"})
        st.session_state.iot_devices = devices
    
    if "provisioning_step" not in st.session_state: st.session_state.provisioning_step = 0

    # 1. STYLE INJECTION (TOP)
    bg_path = f"grphics/bg_{st.session_state.bg_mode}.jpg"
    bg_b64 = get_base64_img(bg_path)
    overlay_path = "grphics/enter_overlay.jpg"
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
                if st.button("INITIALIZE FORENSIC FEED", key="auth_btn", width="stretch"):
                    if name:
                        st.session_state.researcher_name = name
                        st.session_state.first_visit = False
                        st.rerun()
                    else:
                        st.warning("Identification name is required for access.")
        st.stop()

    # ── 3. Data Ingestion (PRE-SIDEBAR FOR v17.2) ──────────────────
    # Default file path
    default_path = "plantation_soil_data.xlsm"
    
    # Check if we need to load differently cached or uploaded files
    raw_df = load_data(default_path)
    latest_stats_all, workbench_df = compute_stats(raw_df)
    
    # Determine current view stats
    if st.session_state.hub_mode == "Live Readings":
        active_stats = latest_stats_all.copy()
        full_df = workbench_df.copy()
    else:
        avg_raw = workbench_df.groupby('plot_id').mean(numeric_only=True).reset_index()
        avg_raw['timestamp'] = workbench_df['timestamp'].max() 
        active_stats, _ = compute_stats(avg_raw)
        full_df = workbench_df.copy()

    # ── 4. Sidebar ───────────────────────────────────────────────
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
        if uploaded_file:
             # If new samples uploaded, re-initialize data engine
             raw_df = load_data(uploaded_file)
             latest_stats_all, workbench_df = compute_stats(raw_df)
             # Update active stats based on hub mode
             if st.session_state.hub_mode == "Live Readings":
                active_stats = latest_stats_all.copy()
                full_df = workbench_df.copy()
             else:
                avg_raw = workbench_df.groupby('plot_id').mean(numeric_only=True).reset_index()
                avg_raw['timestamp'] = workbench_df['timestamp'].max() 
                active_stats, _ = compute_stats(avg_raw)
                full_df = workbench_df.copy()

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
        st_html("<div class='label-tech' style='text-align:center;'>Digital Intelligence Hub</div>")
        render_chat_widget(stats_df=active_stats, full_df=full_df, wide_mode=False) 

    # ── 5. Main Body ─────────────────────────────────────────────
    render_header()
    stats = active_stats # Already computed above
    
    tabs = st.tabs(["FIELD MAP", "FORENSIC WORKBENCH", "PROTOCOLS", "EVOLUTION", "AI ADVISOR", "IoT COMMAND", "DATA LEDGER", "STRATEGIC OVERLAY"])
    with tabs[0]: render_farm_map(full_df, stats)
    with tabs[1]: 
        st.subheader("Data Science Master Workbench")
        p_id = st.selectbox("Select Target Plot", workbench_df['plot_id'].unique(), key="wb_plot")
        pdf = workbench_df[workbench_df['plot_id'] == p_id].copy()
        t1, t2, t3 = st.tabs(["TELEMETRIC TRENDS", "HEALTH ENVELOPES", "STAT ANALYSIS"])
        with t1:
            pdf['date'] = pdf['timestamp'].dt.date
            daily_rain = pdf.groupby('date')['rainfall_mm'].sum().reset_index()
            
            # --- v16.9 Breathing Room Trailing HEADER ---
            h_title, h_pop = st.columns([0.85, 0.15], vertical_alignment="center")
            with h_title:
                st.markdown("<h3 style='white-space:nowrap; margin-bottom:0;'>Primary Metric Timeline</h3>", unsafe_allow_html=True)
            with h_pop:
                with st.popover("ⓘ", width="content"):
                    st.markdown("**How to Read this Analysis?**")
                    st.write("Shows if your sensor readings are flat and stable. **Spikes or sharp drops** mean the environment changed too quickly for plants to adapt. The blue bars represent rainfall intensity.")
            st.caption("24-Hour Plot Stability Monitoring.")
            
            # (Plot reconstruction logic was moved to a separate function or handled inline in my previous attempt, but I'll make sure it's consistent)
            # Actually, I updated the fig logic in a previous chunk that succeeded. 
            # I need to match the actual content of the file now.
            
            # Wait, I updated lines 1327-1345 in the previous successful call.
            # I should read the file again to be safe.
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            # Rainfall as bars on secondary axis
            fig.add_trace(go.Bar(x=pdf['timestamp'], y=pdf['rainfall_mm'], name="🌧️ Rainfall (mm)", 
                                marker_color="#38bdf8", opacity=0.3), secondary_y=True)
            # Moisture as primary line
            fig.add_trace(go.Scatter(x=pdf['timestamp'], y=pdf['soil_moisture_pct'], name="💧 Moisture (%)", 
                                     mode="lines", line=dict(color="#4EDEA3", width=4)), secondary_y=False)
            
            # Additional metrics
            fig.add_trace(go.Scatter(x=pdf['timestamp'], y=pdf.get('soil_temp_c', 0), name="🌡️ Temp (°C)", 
                                     mode="lines", line=dict(color="#fbbf24", width=2, dash='dot')), secondary_y=False)
            
            fig.update_layout(
                height=450, 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="#FFF",
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode="x unified"
            )
            fig.update_xaxes(showgrid=False, title_text="Telemetric Timeline")
            fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)", title_text="Moisture (%) / Temp (°C)", secondary_y=False)
            fig.update_yaxes(showgrid=False, title_text="Rainfall Intensity (mm)", secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)

            
            st.divider()
            
            # --- v16.9 Breathing Room Trailing HEADER ---
            hb_title, hb_pop = st.columns([0.88, 0.12], vertical_alignment="center")
            with hb_title:
                st.markdown("<h3 style='white-space:nowrap; margin-bottom:0;'>Categorical Status Heatmap</h3>", unsafe_allow_html=True)
            with hb_pop:
                with st.popover("ⓘ", width="content"):
                    st.markdown("**How to Read the Heatmap?**")
                    st.write("This map highlights **'High Stress'** areas in Red. If you see a cluster of red nodes (dry) or dark blue (saturated), the specific zone needs immediate forensic intervention.")
            st.caption("Plot Health Snapshot: Moisture levels over time.")
            
            h_data = get_categorical_heatmap_data(workbench_df, p_id)
            h_data['day'] = h_data['timestamp'].dt.strftime('%b %d')
            h_data['hour'] = h_data['timestamp'].dt.hour
            h_pivot = h_data.pivot(index='day', columns='hour', values='moisture_cat')
            
            fig_h = px.imshow(h_pivot, 
                              aspect="auto",
                              color_continuous_scale=[[0, '#ef4444'], [0.5, '#fbbf24'], [1, '#4edea3']],
                              labels=dict(x="Hour of Day", y="Date", color="Stress Level")
                             )
            fig_h.update_layout(plot_bgcolor='rgba(0,0,0,0)', font_color="#FFF", height=300)
            st.plotly_chart(fig_h, width="stretch")

        with t2:
            # --- v16.9 Breathing Room Trailing HEADER ---
            h_title, h_pop = st.columns([0.86, 0.14], vertical_alignment="center")
            with h_title:
                st.markdown("<h3 style='white-space:nowrap; margin-bottom:0;'>Biological Health Envelopes</h3>", unsafe_allow_html=True)
            with h_pop:
                with st.popover("ⓘ", width="content"):
                    st.write("Identifies critical envelopes for plant health. **Salinity (EC)** correlates to fertilisation, and **Thermal** plots how moisture buffers heat spikes.")
            st.caption("Chemistry Balance Envelopes.")
            
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
            # --- v16.9 Breathing Room Trailing HEADER ---
            h_title, h_pop = st.columns([0.85, 0.15], vertical_alignment="center")
            with h_title:
                st.markdown("<h3 style='white-space:nowrap; margin-bottom:0;'>Forensic Correlation Matrix</h3>", unsafe_allow_html=True)
                st.caption("Variable Synchronization Metrics.")
            with h_pop:
                with st.popover("ⓘ", width="stretch"):
                    st.write("A score of **1.00** means the variables move perfectly together. Negative scores mean they move in opposite directions.")
            
            corr_df = pdf[['soil_moisture_pct', 'soil_ec_ds_m', 'soil_ph', 'soil_temp_c', 'rainfall_mm', 'lagged_rainfall_mm']].corr()
            st.plotly_chart(px.imshow(corr_df, text_auto=".2f", color_continuous_scale="Viridis"), width="stretch")
    with tabs[2]: render_protocols(stats)
    with tabs[3]: render_evolution()
    with tabs[4]: render_chat_widget(stats_df=stats, full_df=full_df, wide_mode=True)
    with tabs[5]: render_iot_command()
    with tabs[6]:
        st_html("<div class='label-tech'>Master Data Ledger</div>")
        st.caption("Viewing raw sensor streams and telemetry logs.")
        render_themed_ledger(full_df)
        st.download_button("EXPORT FORENSIC DATA", data=full_df.to_csv(index=False), file_name="forensic_telemetry.csv", mime="text/csv")

    with tabs[7]:
        st_html("<div class='label-tech'>Strategic Expansion Roadmap</div>")
        st.markdown("""
        ### Phase 2: Biological Integration
        - **NPK Inline Probes**: Real-time mapping of Nitrogen, Phosphorus, and Potassium gradients.
        - **Root-Zone O2 Sensors**: Monitoring soil aeration to prevent root rot in saturated zones.
        
        ### Phase 3: Satellite Correlation
        - **NDVI Vegetation Index Overlay**: Correlating soil health with actual plant vigor from orbital data.
        - **Evapotranspiration Tracking**: Modeling water loss to predict irrigation needs 48 hours in advance.
        
        ### Phase 4: Autonomous Closed-Loop
        - **AI-Managed Irrigation**: Removing manual intervention by allowing Gemini to trigger protocols based on risk forecasts.
        """)

    
    if st.session_state.selected_plot:
        p_id = st.session_state.selected_plot
        try:
            s_row = stats[stats['plot_id'] == p_id].iloc[0]
            st.session_state.selected_plot = None
            render_plot_detail(p_id, s_row)
        except:
            st.session_state.selected_plot = None

    # (Chat widget button now handled in sidebar)

    # ── 6. Audio Injection ───────────────────────────────────────
    music_file = "music/MP3Now.com_YouTube_Stardew-Valley-OST-Fall-The-Smell-of-Mus_Media_omVFjGHx0FQ_009_128k.mp3"
    render_bgm(music_file, play=st.session_state.music_on)

if __name__ == "__main__":
    main()
