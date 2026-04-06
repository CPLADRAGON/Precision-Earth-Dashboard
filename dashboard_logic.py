import pandas as pd
import streamlit as st

@st.cache_data
def load_data(file_input):
    """
    Loads soil data from a file path or UploadedFile buffer.
    Validates structure for EE4409 CA2.
    """
    try:
        if hasattr(file_input, "read"): # Buffer check
            if file_input.name.endswith('.csv'):
                df = pd.read_csv(file_input)
            else:
                df = pd.read_excel(file_input)
        else:
            df = pd.read_excel(file_input)
            
        required_cols = ['plot_id', 'soil_moisture_pct', 'soil_ec_ds_m', 'soil_ph', 'timestamp']
        if not all(col in df.columns for col in required_cols):
            missing = [c for c in required_cols if c not in df.columns]
            raise ValueError(f"Missing columns: {', '.join(missing)}")
            
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        raise ValueError(f"Format Error: {str(e)}")

@st.cache_data
def compute_stats(df):
    """Computes basic soil health stats and alerts."""
    # Ensure dataframe is sorted for lagging
    df = df.sort_values(['plot_id', 'timestamp'])
    
    # Lagged Rainfall (1 Hour) - demonstrating absorption delay
    df['lagged_rainfall_mm'] = df.groupby('plot_id')['rainfall_mm'].shift(1)
    
    latest = df.sort_values('timestamp').groupby('plot_id').tail(1).copy()
    
    def moisture_level(pct):
        if pct < 12: return 'Critical'
        if pct < 20: return 'Warning'
        if pct > 35: return 'Saturated' # Field capacity
        return 'Optimal'

    def ec_level(ec):
        if ec > 2.0: return 'Critical'
        if ec > 1.2: return 'Warning'
        return 'Optimal'

    def ph_level(ph):
        if ph < 5.0 or ph > 8.5: return 'Critical'
        if ph < 6.0 or ph > 7.5: return 'Warning'
        return 'Optimal'

    latest['moisture_status'] = latest['soil_moisture_pct'].apply(moisture_level)
    latest['ec_status'] = latest['soil_ec_ds_m'].apply(ec_level)
    latest['ph_status'] = latest['soil_ph'].apply(ph_level)
    
    def compute_risk(row, df):
        # Calculate moisture trend to determine risk
        plot_data = df[df['plot_id'] == row['plot_id']].tail(10)
        
        # Check for immediate critical sensor states (EC/pH/Moisture)
        if row['ec_status'] == 'Critical':
            return "High", f"Forensic Alert: Salinity ({row['soil_ec_ds_m']:.2f} EC) is at toxic levels."
        if row['ph_status'] == 'Critical':
            return "High", f"Forensic Alert: pH ({row['soil_ph']:.1f}) is outside biological safety envelope."
        
        if len(plot_data) < 2: return "Low", "Initializing trend analysis..."
        
        m_start = plot_data['soil_moisture_pct'].iloc[0]
        m_end = plot_data['soil_moisture_pct'].iloc[-1]
        m_delta = m_end - m_start
        
        if m_end < 15 and m_delta < 0:
            return "High", f"Drought Risk: Moisture dropping ({m_delta:+.1f}% recently)."
        if m_end < 20: 
            return "Medium", "Watch Level: Soil moisture approaching dry threshold."
        if m_end > 35:
            return "Medium", "Waterlogging Alert: Risk of root-zone anoxia."
            
        # Warning checks
        if row['ec_status'] == 'Warning' or row['ph_status'] == 'Warning':
            return "Medium", "Watch Level: Chemistry indicators are deviating from optimal."
            
        return "Low", "Stable Telemetry: No immediate forensic threats detected."


    latest[['risk_level', 'risk_reason']] = latest.apply(lambda r: pd.Series(compute_risk(r, df)), axis=1)
    
    def overall_status(row):
        statuses = [row['moisture_status'], row['ec_status'], row['ph_status']]
        if 'Critical' in statuses: return 'Critical'
        if 'Warning' in statuses: return 'Warning'
        return 'Optimal'
    
    latest['overall_status'] = latest.apply(overall_status, axis=1)
    
    return latest, df


def get_categorical_heatmap_data(df, plot_id):
    """Translates raw moisture into Drought/Normal/Saturated categories."""
    pdf = df[df['plot_id'] == plot_id].copy()
    def categorize(m):
        if m < 10: return 0 # Drought (Red)
        if m > 35: return 2 # Saturated (Green)
        return 1 # Normal (Yellow)
    
    pdf['moisture_cat'] = pdf['soil_moisture_pct'].apply(categorize)
    return pdf
