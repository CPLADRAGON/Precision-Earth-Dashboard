# Dashboard Rebuild Complete ✅

## What Was Built

A complete replacement of [dashboard.py](file:///c:/Users/wangbo/Desktop/Work/EE4409/CA2/dashboard.py) with a new 4-tab **Precision Earth** IoT soil health dashboard using the `stitch_new` design system.

**Running at:** `http://localhost:8503`  
**Launch command:** `& "C:\Users\wangbo\AppData\Local\Programs\Python\Python313\python.exe" -m streamlit run dashboard.py`

---

## Tab 1 — Executive Overview (Non-Expert View)

Real-time alerts from actual sensor data:
- 🚨 **Irrigation System OFFLINE** — 0mm all week
- 🚨 **Plot 1 Drought** — hit 1.0% moisture, 4.8 dS/m salt peak
- ⚠️ **Plot 2 Acidity** — pH hit 4.92

3 per-plot status cards showing current readings with STRESSED/WARNING/OPTIMAL badge.

**AI Farm Assistant** (Google Gemini) — responds in plain English to farm questions with full farm data as context.

![Executive Overview + Chatbot](C:\Users\wangbo\.gemini\antigravity\brain\c39c6129-4e76-422f-bfe3-b555e51fd268\chatbot_full_response_1774948540198.png)

---

## Tab 2 — Historical Trends

- **Dual-Axis Plotly chart**: Rainfall bars + 3-plot moisture lines with Wilting Point threshold line
- **Soil Status Heatmap**: Daily moisture status per plot (Drought/Normal/Wet)
- **Critical Insight panel**: Explains that moisture only recovered after rain events — confirms irrigation failure
- **Plot selector dropdown** to view individual plot vs. all plots

![Historical Trends with Real Plotly Chart](C:\Users\wangbo\.gemini\antigravity\brain\c39c6129-4e76-422f-bfe3-b555e51fd268\historical_trends_tab_1774948512069.png)

---

## Tab 3 — Action Center

3 data-driven intervention cards for technicians, all triggered by real anomalies in the data:
1. **Inspect BMS Irrigation Controller** (Immediate) — 0mm irrigation confirmed
2. **Fresh-water Flush on Plot 1** (High Priority) — EC 4.8 dS/m confirmed  
3. **pH Buffer on Plot 2** (Medium Priority) — pH 4.92 confirmed

---

## Tab 4 — Future Upgrades

3 "locked" premium sensor proposals with cost vs. crop loss comparison chart:
1. Multi-depth Tensiometers ($1,240 vs $18,500 crop loss risk)
2. Drainage Lysimeters ($4,800 vs $32,000 risk avoidance)
3. Automated Flow Totalizers ($2,100 vs $24,500 financial risk)

---

## Technical Summary

| Component | Technology |
|---|---|
| Backend | Streamlit (native components, no iframe issues) |
| AI Chatbot | Google Gemini (`gemini-3-flash-preview`) via `google-genai` SDK |
| Charts | Plotly with real data from [plantation_soil_data.xlsm](file:///c:/Users/wangbo/Desktop/Work/EE4409/CA2/plantation_soil_data.xlsm) |
| CSS | Custom dark theme matching stitch_new Precision Earth palette |
| Navigation | Native `st.radio` in sidebar — fully clickable, no iframe sandbox issues |
| Data Ingestion | `st.file_uploader` for custom datasets (.csv, .xlsm, .xlsx) |
| Data Export | `st.download_button` for exporting current soil diagnostics as CSV |

---

## Data Control (Enhancements)

The dashboard now includes native data ingestion and export controls in the sidebar:
- **Data Source Upload**: A custom file uploader allowing you to replace the default [plantation_soil_data.xlsm](file:///c:/Users/wangbo/Desktop/Work/EE4409/CA2/plantation_soil_data.xlsm) with new `.csv` or `.xlsx` datasets. The dashboard instantly re-renders all charts and AI context based on the new data.
- **Export Soil Report**: Generates a downloadable CSV containing the latest diagnostic snapshot for all 3 plots, including maximum stress metrics and system totals (rainfall/irrigation).

![Data Upload and Export Functional Demo](C:\Users\wangbo\.gemini\antigravity\brain\c39c6129-4e76-422f-bfe3-b555e51fd268\dashboard_sidebar_verify_1774949207227.png)

