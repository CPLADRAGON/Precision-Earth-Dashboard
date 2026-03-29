import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import io
import os

# ──────────────────────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bioluminescent Nexus | Soil Health Monitor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# Custom CSS for "Bioluminescent Nexus" Premium Styling
# ──────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">

<style>
    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Manrope', sans-serif;
        color: #E1E2EB;
    }
    h1, h2, h3, h4, .font-headline {
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Glassmorphism Panel */
    .glass-panel {
        background: rgba(50, 53, 60, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 24px;
        margin-bottom: 24px;
    }

    /* KPI Card Styling (Bento Style) */
    .kpi-card {
        position: relative;
        overflow: hidden;
        padding: 24px;
        border-radius: 20px;
        background: #191C22;
        border: 1px solid rgba(255, 255, 255, 0.03);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .kpi-card:hover {
        background: #1D2026;
        transform: translateY(-4px);
        border-color: rgba(120, 220, 119, 0.2);
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 80px; height: 80px;
        background: rgba(120, 220, 119, 0.05);
        border-radius: 50%;
        transform: translate(-30px, -30px);
        filter: blur(20px);
    }
    .kpi-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #78DC77;
        line-height: 1;
        margin: 12px 0;
    }
    .kpi-unit {
        font-size: 1.2rem;
        opacity: 0.6;
        margin-left: 4px;
    }
    .kpi-label {
        font-size: 0.7rem;
        font-weight: 800;
        color: #BECAB9;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .kpi-status-badge {
        font-size: 0.65rem;
        font-weight: 800;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 6px;
        background: rgba(120, 220, 119, 0.1);
        color: #78DC77;
    }
    .status-warn { background: rgba(255, 177, 199, 0.1); color: #FFB1C7; }
    .status-bad { background: rgba(255, 180, 171, 0.1); color: #FFB4AB; }

    /* Animated Pulse */
    .pulse-live {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #78DC77;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(120, 220, 119, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(120, 220, 119, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(120, 220, 119, 0); }
    }

    /* Sidebar Overrides */
    [data-testid="stSidebar"] {
        background-color: #191C22;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Premium Table Styling */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 12px;
        overflow: hidden;
        background: #191C22;
    }
    .custom-table th {
        background: #0B0E14;
        color: #BECAB9;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        padding: 16px 24px;
        text-align: left;
    }
    .custom-table td {
        padding: 18px 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        font-size: 14px;
    }
    .custom-table tr:hover {
        background: rgba(255, 255, 255, 0.02);
    }

    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(90deg, #78DC77, #4CAF50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
    }
    
    /* Header Container */
    .header-container {
        margin-bottom: 40px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# Default Thresholds
# ──────────────────────────────────────────────────────────────
DEFAULT_THRESHOLDS = {
    "soil_moisture_pct": {"min": 15.0, "max": 40.0, "unit": "%", "label": "Soil Moisture"},
    "soil_temp_c":       {"min": 18.0, "max": 32.0, "unit": "°C", "label": "Soil Temperature"},
    "soil_ph":           {"min": 5.5,  "max": 7.5,  "unit": "",   "label": "Soil pH"},
    "soil_ec_ds_m":      {"min": 0.2,  "max": 2.0,  "unit": "dS/m", "label": "Soil EC"},
}

PLOT_COLORS = {"Plot1": "#4CAF50", "Plot2": "#2196F3", "Plot3": "#FF9800"}

# ──────────────────────────────────────────────────────────────
# Data Loading
# ──────────────────────────────────────────────────────────────
@st.cache_data
def load_default_data():
    """Load the bundled plantation dataset."""
    path = os.path.join(os.path.dirname(__file__), "plantation_soil_data.xlsm")
    if os.path.exists(path):
        df = pd.read_excel(path, engine="openpyxl")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    return None

def load_uploaded_data(uploaded_file):
    """Load data from an uploaded file."""
    name = uploaded_file.name.lower()
    if name.endswith((".xlsx", ".xlsm")):
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    elif name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        st.error("Unsupported file format. Please upload .xlsx, .xlsm, or .csv")
        return None
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

# ──────────────────────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────────────────────
def get_health_status(value, low, high):
    """Return status label and CSS class."""
    if low <= value <= high:
        return "Normal", "status-good"
    margin_low = low - (high - low) * 0.2
    margin_high = high + (high - low) * 0.2
    if margin_low <= value <= margin_high:
        return "Warning", "status-warn"
    return "Critical", "status-bad"

def get_status_emoji(status):
    return {"Normal": "🟢", "Warning": "🟡", "Critical": "🔴"}.get(status, "⚪")

def render_premium_table(df):
    """Render a premium HTML table matching the Stitch design."""
    if df.empty:
        return "<p style='text-align:center; padding:20px; color:#BECAB9;'>No data available</p>"
    
    html = '<table class="custom-table"><thead><tr>'
    for col in df.columns:
        html += f'<th>{col.replace("_", " ").upper()}</th>'
    html += '</tr></thead><tbody>'
    
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = row[col]
            # Special styling for status
            if col == "status":
                color = "#FFB4AB" if "Above" in str(val) or "Below" in str(val) or "Critical" in str(val) else "#78DC77"
                bg = "rgba(255, 180, 171, 0.1)" if color == "#FFB4AB" else "rgba(120, 220, 119, 0.1)"
                html += f'<td><span style="background:{bg}; color:{color}; padding:4px 10px; border-radius:6px; font-size:10px; font-weight:800; text-transform:uppercase;">{val}</span></td>'
            elif "timestamp" in col:
                html += f'<td style="font-family:Space Grotesk; font-weight:500;">{pd.to_datetime(val).strftime("%H:%M:%S %p")}</td>'
            else:
                html += f'<td>{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

def detect_anomalies(df, thresholds):
    """Flag rows where any sensor is outside threshold range."""
    anomaly_mask = pd.Series(False, index=df.index)
    anomaly_details = []
    for col, th in thresholds.items():
        if col in df.columns:
            below = df[col] < th["min"]
            above = df[col] > th["max"]
            mask = below | above
            anomaly_mask |= mask
            for idx in df[mask].index:
                anomaly_details.append({
                    "timestamp": df.loc[idx, "timestamp"],
                    "plot": df.loc[idx, "plot_id"],
                    "sensor": th["label"],
                    "value": f"{df.loc[idx, col]:.2f}",
                    "status": "Below Min" if df.loc[idx, col] < th["min"] else "Above Max",
                })
    return anomaly_mask, pd.DataFrame(anomaly_details)

def dark_plotly_layout(fig, title="", height=400):
    """Apply consistent Bioluminescent Nexus theme to plotly figures."""
    fig.update_layout(
        title=dict(text=title, font=dict(family="Space Grotesk", size=18, color="#E1E2EB")),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope", color="#BECAB9", size=12),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E1E2EB"),
            orientation="h",
            yanchor="bottom", y=1.02, xanchor="right", x=1,
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.1)",
            tickfont=dict(size=10, color="#BECAB9"),
            title=dict(font=dict(size=11, color="#BECAB9"))
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.1)",
            tickfont=dict(size=10, color="#BECAB9"),
            title=dict(font=dict(size=11, color="#BECAB9"))
        ),
        height=height,
        margin=dict(l=40, r=20, t=80, b=40),
    )
    return fig

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom: 32px;">
        <div style="font-family: 'Space Grotesk'; font-size: 1.25rem; font-weight: 700; color: #78DC77; letter-spacing: -0.5px;">Bioluminescent Nexus</div>
        <div style="font-family: 'Space Grotesk'; font-size: 10px; text-transform: uppercase; letter-spacing: 0.2em; color: #BECAB9; opacity: 0.6;">Agricultural Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("## 🌱 Controls")

    # File Upload
    st.markdown("### 📂 Data Source")
    uploaded_file = st.file_uploader(
        "Upload dataset", type=["xlsx", "xlsm", "csv"],
        help="Upload a plantation soil dataset or use the bundled default."
    )

    # Load Data
    if uploaded_file is not None:
        df = load_uploaded_data(uploaded_file)
        st.success(f"✅ Loaded: {uploaded_file.name}")
    else:
        df = load_default_data()
        if df is not None:
            st.info("📦 Using bundled dataset")
        else:
            st.error("❌ No dataset found. Please upload one.")
            st.stop()

    if df is None:
        st.stop()

    st.markdown("---")

    # Date Range Filter
    st.markdown("### 📅 Date Range")
    if "timestamp" in df.columns:
        min_date = df["timestamp"].min().date()
        max_date = df["timestamp"].max().date()
        date_range = st.date_input(
            "Select range", value=(min_date, max_date),
            min_value=min_date, max_value=max_date,
        )
        if len(date_range) == 2:
            df = df[(df["timestamp"].dt.date >= date_range[0]) &
                     (df["timestamp"].dt.date <= date_range[1])]

    st.markdown("---")

    # Plot Selector
    st.markdown("### 🌾 Plots")
    all_plots = sorted(df["plot_id"].unique()) if "plot_id" in df.columns else []
    selected_plots = st.multiselect("Select plots", all_plots, default=all_plots)
    if selected_plots:
        df = df[df["plot_id"].isin(selected_plots)]

    st.markdown("---")

    # Threshold Sliders
    st.markdown("### ⚙️ Alert Thresholds")
    st.caption("Adjust safe ranges for anomaly detection")
    thresholds = {}
    for col, defaults in DEFAULT_THRESHOLDS.items():
        if col in df.columns:
            data_min = float(df[col].min())
            data_max = float(df[col].max())
            slider_min = min(data_min, defaults["min"] - 5)
            slider_max = max(data_max, defaults["max"] + 5)
            vals = st.slider(
                f"{defaults['label']} ({defaults['unit']})",
                min_value=slider_min, max_value=slider_max,
                value=(defaults["min"], defaults["max"]),
                key=f"th_{col}",
            )
            thresholds[col] = {"min": vals[0], "max": vals[1],
                               "unit": defaults["unit"], "label": defaults["label"]}

    st.markdown("---")
    st.markdown("""
    <div style="font-family: 'Manrope'; font-size: 10px; color: #BECAB9; opacity: 0.5; padding-top: 20px;">
        EE4409 CA2 • Plantation Monitor<br>
        v2.0.0-PRO-NEXUS
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# Detect Anomalies
# ──────────────────────────────────────────────────────────────
anomaly_mask, anomaly_df = detect_anomalies(df, thresholds)
anomaly_count = anomaly_mask.sum()

# ──────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-container">
    <div style="display: flex; justify-content: space-between; align-items: flex-end;">
        <div>
            <div style="font-family: 'Space Grotesk'; text-transform: uppercase; letter-spacing: 0.3em; font-size: 10px; color: #BECAB9; margin-bottom: 8px;">Live Telemetry System</div>
            <h1 class="font-headline" style="font-size: 2.5rem; font-weight: 800; margin: 0; display: flex; align-items: center; gap: 16px;">
                <span class="gradient-text">SOIL HEALTH MONITOR</span>
                <span style="font-size: 0.6rem; padding: 4px 12px; background: rgba(120, 220, 119, 0.1); border: 1px solid rgba(120, 220, 119, 0.2); border-radius: 100px; color: #78DC77; display: flex; align-items: center;">
                    <span class="pulse-live"></span>
                    LIVE
                </span>
            </h1>
        </div>
        <div style="text-align: right; font-size: 0.8rem; color: #BECAB9;">
            <strong>Sector Alpha-7</strong><br>
            Plantation Intelligence Node
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "📈 Trends", "🌧️ Rainfall & Irrigation",
    "🚨 Anomaly Detection", "🔗 Correlations & Insights"
])

# ══════════════════════════════════════════════════════════════
# TAB 1: OVERVIEW
# ══════════════════════════════════════════════════════════════
with tab1:
    # Alert Banner
    if anomaly_count > 0:
        st.markdown(f"""
        <div class="alert-banner">
            🚨 <strong>{anomaly_count} anomalous readings</strong> detected across {len(anomaly_df['plot'].unique()) if not anomaly_df.empty else 0} plot(s).
            Check the <em>Anomaly Detection</em> tab for details.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-banner-ok">
            ✅ <strong>All readings within safe thresholds.</strong> System operating normally.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📋 Plot Health Summary")

    # KPI Cards per plot
    for plot in selected_plots:
        plot_data = df[df["plot_id"] == plot]
        if plot_data.empty:
            continue

        st.markdown(f"#### {plot}")
        cols = st.columns(4)

        for i, (col_name, th) in enumerate(thresholds.items()):
            if col_name in plot_data.columns:
                avg_val = plot_data[col_name].mean()
                status, css_class = get_health_status(avg_val, th["min"], th["max"])
                emoji = get_status_emoji(status)

                with cols[i]:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;">
                            <div style="padding: 8px; background: rgba(120, 220, 119, 0.1); border-radius: 10px; color: #78DC77;">
                                <span class="material-symbols-outlined" style="font-size: 20px;">{"water_drop" if "moisture" in col_name else "thermostat" if "temp" in col_name else "science"}</span>
                            </div>
                            <span class="kpi-status-badge {css_class}">{status}</span>
                        </div>
                        <div class="kpi-label">{th['label']}</div>
                        <div class="kpi-value">{avg_val:.1f}<span class="kpi-unit">{th['unit']}</span></div>
                        <div style="height: 4px; width: 100%; background: #32353C; border-radius: 2px; margin-top: 16px; overflow: hidden;">
                            <div style="height: 100%; background: {"#78DC77" if status=="Normal" else "#FFB1C7" if status=="Warning" else "#FFB4AB"}; width: {min(100, (avg_val/th['max'])*100) if th['max']!=0 else 0}%"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # Quick stats table
    st.markdown("### 📊 Data Overview")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("📅 Data Points", f"{len(df):,}")
    col_b.metric("🌾 Active Plots", len(selected_plots))
    col_c.metric("🚨 Anomalies", f"{anomaly_count:,}")

# ══════════════════════════════════════════════════════════════
# TAB 2: TRENDS
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### 📈 Sensor Trends Over Time")
    st.caption("Interactive time-series with safe threshold bands. Hover for details, drag to zoom.")

    for col_name, th in thresholds.items():
        if col_name not in df.columns:
            continue

        fig = go.Figure()

        # Threshold band
        fig.add_hrect(
            y0=th["min"], y1=th["max"],
            fillcolor="#78DC77", opacity=0.05,
            line_width=0,
            annotation_text="Safe Range", annotation_position="top left",
            annotation=dict(font_size=10, font_color="#78DC77", font_family="Space Grotesk"),
        )
        fig.add_hline(y=th["min"], line_dash="dash", line_color="#FFB1C7", opacity=0.3)
        fig.add_hline(y=th["max"], line_dash="dash", line_color="#FFB1C7", opacity=0.3)

        # Plot lines
        for plot_id in selected_plots:
            plot_data = df[df["plot_id"] == plot_id].sort_values("timestamp")
            fig.add_trace(go.Scatter(
                x=plot_data["timestamp"], y=plot_data[col_name],
                name=plot_id,
                line=dict(color=PLOT_COLORS.get(plot_id, "#FFFFFF"), width=2),
                mode="lines",
                hovertemplate=f"<b>{plot_id}</b><br>"
                              f"Time: %{{x}}<br>"
                              f"{th['label']}: %{{y:.2f}} {th['unit']}<extra></extra>",
            ))

        dark_plotly_layout(fig, title=f"{th['label']} ({th['unit']})", height=350)
        fig.update_yaxes(title_text=f"{th['label']} ({th['unit']})")
        fig.update_xaxes(title_text="Time")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 3: RAINFALL & IRRIGATION
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### 🌧️ Rainfall & Irrigation Analysis")
    st.caption("Compare natural rainfall with irrigation supply across plots.")

    if "rainfall_mm" in df.columns and "irrigation_mm" in df.columns:
        # Aggregated by date
        df_daily = df.copy()
        df_daily["date"] = df_daily["timestamp"].dt.date
        daily_agg = df_daily.groupby(["date", "plot_id"]).agg(
            rainfall=("rainfall_mm", "sum"),
            irrigation=("irrigation_mm", "sum"),
            avg_moisture=("soil_moisture_pct", "mean"),
        ).reset_index()

        col1, col2 = st.columns(2)

        with col1:
            fig_rain = go.Figure()
            for plot_id in selected_plots:
                pdata = daily_agg[daily_agg["plot_id"] == plot_id]
                fig_rain.add_trace(go.Bar(
                    x=pdata["date"], y=pdata["rainfall"],
                    name=f"{plot_id} Rainfall",
                    marker_color=PLOT_COLORS.get(plot_id, "#FFFFFF"),
                    opacity=0.7,
                ))
            dark_plotly_layout(fig_rain, title="Daily Rainfall (mm)", height=350)
            fig_rain.update_layout(barmode="group")
            fig_rain.update_yaxes(title_text="Rainfall (mm)")
            st.plotly_chart(fig_rain, use_container_width=True)

        with col2:
            fig_irr = go.Figure()
            for plot_id in selected_plots:
                pdata = daily_agg[daily_agg["plot_id"] == plot_id]
                fig_irr.add_trace(go.Bar(
                    x=pdata["date"], y=pdata["irrigation"],
                    name=f"{plot_id} Irrigation",
                    marker_color=PLOT_COLORS.get(plot_id, "#FFFFFF"),
                    opacity=0.7,
                ))
            dark_plotly_layout(fig_irr, title="Daily Irrigation (mm)", height=350)
            fig_irr.update_layout(barmode="group")
            fig_irr.update_yaxes(title_text="Irrigation (mm)")
            st.plotly_chart(fig_irr, use_container_width=True)

        # Moisture response
        st.markdown("#### 💧 Moisture Response to Rainfall")
        fig_resp = go.Figure()
        for plot_id in selected_plots:
            pdata = daily_agg[daily_agg["plot_id"] == plot_id]
            fig_resp.add_trace(go.Scatter(
                x=pdata["rainfall"], y=pdata["avg_moisture"],
                mode="markers",
                name=plot_id,
                marker=dict(
                    color=PLOT_COLORS.get(plot_id, "#FFFFFF"),
                    size=10, opacity=0.7,
                    line=dict(width=1, color="#FAFAFA"),
                ),
                hovertemplate=f"<b>{plot_id}</b><br>"
                              "Rainfall: %{x:.1f} mm<br>"
                              "Avg Moisture: %{y:.1f}%<extra></extra>",
            ))
        dark_plotly_layout(fig_resp, title="Rainfall vs Soil Moisture", height=400)
        fig_resp.update_xaxes(title_text="Daily Rainfall (mm)")
        fig_resp.update_yaxes(title_text="Avg Soil Moisture (%)")
        st.plotly_chart(fig_resp, use_container_width=True)

        # Irrigation Efficiency
        st.markdown("#### 📊 Irrigation Efficiency Summary")
        eff_cols = st.columns(len(selected_plots))
        for i, plot_id in enumerate(selected_plots):
            pdata = daily_agg[daily_agg["plot_id"] == plot_id]
            total_rain = pdata["rainfall"].sum()
            total_irr = pdata["irrigation"].sum()
            avg_moist = pdata["avg_moisture"].mean()
            with eff_cols[i]:
                st.markdown(f"**{plot_id}**")
                st.metric("Total Rainfall", f"{total_rain:.1f} mm")
                st.metric("Total Irrigation", f"{total_irr:.1f} mm")
                st.metric("Avg Moisture", f"{avg_moist:.1f}%")
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 4: ANOMALY DETECTION
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🚨 Anomaly Detection")
    st.caption("Readings outside your configured safe thresholds are flagged below.")

    if anomaly_count > 0:
        st.warning(f"⚠️ {anomaly_count} anomalous readings detected.")

        # Anomaly scatter plots
        for col_name, th in thresholds.items():
            if col_name not in df.columns:
                continue

            fig = go.Figure()

            for plot_id in selected_plots:
                plot_data = df[df["plot_id"] == plot_id].sort_values("timestamp")

                # Normal points
                normal = plot_data[(plot_data[col_name] >= th["min"]) &
                                   (plot_data[col_name] <= th["max"])]
                anomalous = plot_data[(plot_data[col_name] < th["min"]) |
                                      (plot_data[col_name] > th["max"])]

                fig.add_trace(go.Scatter(
                    x=normal["timestamp"], y=normal[col_name],
                    mode="markers", name=f"{plot_id} (Normal)",
                    marker=dict(color=PLOT_COLORS.get(plot_id, "#FFFFFF"),
                                size=5, opacity=0.4),
                    showlegend=False,
                ))
                if not anomalous.empty:
                    fig.add_trace(go.Scatter(
                        x=anomalous["timestamp"], y=anomalous[col_name],
                        mode="markers", name=f"{plot_id} ⚠️",
                        marker=dict(color="#F44336", size=10, symbol="x",
                                    line=dict(width=2, color="#FFFFFF")),
                        hovertemplate=f"<b>ANOMALY - {plot_id}</b><br>"
                                      f"Time: %{{x}}<br>"
                                      f"{th['label']}: %{{y:.2f}} {th['unit']}<extra></extra>",
                    ))

            # Threshold lines
            fig.add_hline(y=th["min"], line_dash="dash", line_color="#FFC107",
                          annotation_text=f"Min: {th['min']}")
            fig.add_hline(y=th["max"], line_dash="dash", line_color="#FFC107",
                          annotation_text=f"Max: {th['max']}")

            dark_plotly_layout(fig, title=f"{th['label']} — Anomaly View", height=300)
            st.plotly_chart(fig, use_container_width=True)

        # Anomaly table
        st.markdown("#### 📋 Anomaly Detail Logs")
        if not anomaly_df.empty:
            display_df = anomaly_df.sort_values("timestamp", ascending=False)
            st.markdown(render_premium_table(display_df), unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)

            # Export
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Anomaly Report (CSV)",
                data=csv,
                file_name="anomaly_report.csv",
                mime="text/csv",
            )
    else:
        st.success("✅ No anomalies detected with current threshold settings.")
        st.info("💡 Try narrowing the threshold ranges in the sidebar to surface more insights.")

# ══════════════════════════════════════════════════════════════
# TAB 5: CORRELATIONS & INSIGHTS
# ══════════════════════════════════════════════════════════════
with tab5:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### 🔗 Sensor Correlations")
    st.caption("Pearson correlation between all soil sensors reveals underlying relationships.")

    sensor_cols = [c for c in ["soil_moisture_pct", "soil_temp_c", "soil_ec_ds_m",
                                "soil_ph", "rainfall_mm", "irrigation_mm"] if c in df.columns]
    if sensor_cols:
        corr = df[sensor_cols].corr()

        # Rename for display
        rename_map = {
            "soil_moisture_pct": "Moisture (%)",
            "soil_temp_c": "Temp (°C)",
            "soil_ec_ds_m": "EC (dS/m)",
            "soil_ph": "pH",
            "rainfall_mm": "Rainfall (mm)",
            "irrigation_mm": "Irrigation (mm)",
        }
        corr_display = corr.rename(index=rename_map, columns=rename_map)

        fig_corr = px.imshow(
            corr_display,
            text_auto=".2f",
            color_continuous_scale=["#FFB4AB", "#1E1E2E", "#78DC77"],
            zmin=-1, zmax=1,
            aspect="auto",
        )
        dark_plotly_layout(fig_corr, title="Sensor Correlation Matrix", height=500)
        fig_corr.update_layout(
            xaxis=dict(side="bottom"),
            coloraxis_colorbar=dict(title="r"),
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        # Key insights
        st.markdown("#### 💡 Key Correlation Insights")
        # Find strongest correlations (excluding self)
        corr_pairs = []
        for i in range(len(sensor_cols)):
            for j in range(i + 1, len(sensor_cols)):
                corr_pairs.append({
                    "Sensor A": rename_map.get(sensor_cols[i], sensor_cols[i]),
                    "Sensor B": rename_map.get(sensor_cols[j], sensor_cols[j]),
                    "Correlation": corr.iloc[i, j],
                })
        corr_pairs_df = pd.DataFrame(corr_pairs).sort_values("Correlation", key=abs, ascending=False)
        
        for _, row in corr_pairs_df.head(3).iterrows():
            r = row["Correlation"]
            strength = "Strong" if abs(r) > 0.6 else "Moderate" if abs(r) > 0.3 else "Weak"
            direction = "positive" if r > 0 else "negative"
            emoji = "📈" if r > 0 else "📉"
            st.markdown(f"{emoji} **{strength} {direction} correlation** ({r:.2f}) between "
                        f"**{row['Sensor A']}** and **{row['Sensor B']}**")
    st.markdown("</div>", unsafe_allow_html=True)

    # Additional Sensor Recommendations
    st.markdown("---")
    st.markdown("### 🔬 Recommended Additional Sensors")
    st.caption("The current dataset captures core soil parameters. "
               "For a more comprehensive monitoring system, consider adding:")

    rec_cols = st.columns(3)
    with rec_cols[0]:
        st.markdown("""
        **🍃 Leaf Wetness Sensor**
        - Measures surface moisture on leaves
        - Helps predict fungal disease risk
        - Complements soil moisture for canopy health
        - Cost: ~$30–$80 per unit
        """)

    with rec_cols[1]:
        st.markdown("""
        **☀️ Pyranometer (Solar Radiation)**
        - Measures incoming solar energy
        - Enables evapotranspiration estimation
        - Helps optimize irrigation scheduling
        - Cost: ~$100–$300 per unit
        """)

    with rec_cols[2]:
        st.markdown("""
        **🧪 NPK Soil Nutrient Sensor**
        - Measures nitrogen, phosphorus, potassium
        - Complements EC readings for fertility
        - Guides precision fertilization
        - Cost: ~$50–$200 per unit
        """)
