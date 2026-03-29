# 🌿 Bioluminescent Nexus | Plantation Soil Health Monitor

A premium, interactive IoT monitoring dashboard for plantation soil health. Designed for the **EE4409 CA2** project, this dashboard provides real-time insights into soil moisture, temperature, pH, and electrical conductivity across multiple plantation plots.

![Dashboard Preview](https://via.placeholder.com/800x400?text=Bioluminescent+Nexus+Dashboard) 

## ✨ Key Features
- **Bioluminescent UI**: A high-fidelity "dark mode" design with glassmorphism and premium typography (**Space Grotesk**).
- **Multi-Plot Monitoring**: Track metrics for Plot 1, Plot 2, and Plot 3 simultaneously.
- **Anomaly Detection Engine**: Real-time flagging of out-of-range sensor data with adjustable sensitivity sliders.
- **Hydrological Balance**: Integrated analysis of Rainfall vs. Irrigation supply.
- **Correlation Analytics**: Pearson correlation matrix and automated signal insights.

## 🛠️ Tech Stack
- **Frontend/Backend**: [Streamlit](https://streamlit.io/)
- **Visualizations**: [Plotly Graph Objects & Express](https://plotly.com/python/)
- **Data Processing**: Pandas, NumPy, OpenPyXL

## 🚀 Getting Started

### Local Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/CPLADRAGON/plantation-soil-monitor.git
   cd plantation-soil-monitor
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

### ☁️ Online Deployment (Streamlit Cloud)
To make this dashboard live online:
1. Log in to [Streamlit Cloud](https://share.streamlit.io/).
2. Connect your GitHub account.
3. Select this repository (`plantation-soil-monitor`).
4. Set the main file path to `dashboard.py`.
5. Click **Deploy**!

## 📡 Data Connectivity
- **Current Development**: The dashboard reads from `plantation_soil_data.xlsm`.
- **Production Roadmap**: The backend is designed to be easily swapped for a live **PostgreSQL** database or **AWS IoT Core** API endpoint for real-time sensor streaming.

---
**Author**: WANG BOYU (CPLADRAGON)  
**Project**: EE4409 CA2 - Plantation Soil Analytics  
**Version**: 2.0.0-PRO-NEXUS
