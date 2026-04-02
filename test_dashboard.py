import pytest
import pandas as pd
import os
from dashboard_logic import load_data, compute_stats

def test_load_data():
    # Setup: Create a dummy Excel file
    df_dummy = pd.DataFrame({
        'timestamp': pd.to_datetime(['2025-01-01 00:00:00', '2025-01-01 01:00:00']),
        'plot_id': ['Plot1', 'Plot1'],
        'soil_moisture_pct': [25.0, 24.0],
        'soil_temp_c': [22.0, 21.0],
        'soil_ec_ds_m': [0.5, 0.6],
        'soil_ph': [6.5, 6.4],
        'rainfall_mm': [0.0, 0.0],
        'irrigation_mm': [0.0, 0.0]
    })
    dummy_path = 'dummy_data.xlsx'
    df_dummy.to_excel(dummy_path, index=False)
    
    try:
        df = load_data(dummy_path)
        assert not df.empty
        assert 'soil_moisture_pct' in df.columns
        assert len(df) == 2
    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)

def test_compute_stats():
    df = pd.DataFrame({
        'timestamp': pd.to_datetime(['2025-01-01 00:00:00', '2025-01-01 01:00:00', '2025-01-01 00:00:00']),
        'plot_id': ['Plot1', 'Plot1', 'Plot2'],
        'soil_moisture_pct': [5.0, 25.0, 40.0], # 5.0 is critical
        'soil_ec_ds_m': [5.0, 0.5, 0.5], # 5.0 is critical
        'soil_ph': [4.0, 6.5, 6.5], # 4.0 is critical
        'rainfall_mm': [0.0, 1.0, 0.0]
    })
    
    stats, _ = compute_stats(df)
    
    # Check if Plot1 has alerts (Latest is 25.0, so Optimal)
    plot1_stats = stats[stats['plot_id'] == 'Plot1'].iloc[0]
    assert plot1_stats['moisture_status'] == 'Optimal'
    assert plot1_stats['ec_status'] == 'Optimal' # Latest is 0.5
    assert plot1_stats['ph_status'] == 'Optimal' # Latest is 6.5
    
    # Let's add a Plot3 that is actually critical in its latest record
    df_critical = pd.concat([df, pd.DataFrame({
        'timestamp': [pd.to_datetime('2025-01-01 02:00:00')],
        'plot_id': ['Plot3'],
        'soil_moisture_pct': [5.0],
        'soil_ec_ds_m': [5.0],
        'soil_ph': [4.0],
        'rainfall_mm': [0.0]
    })])
    
    stats_critical, _ = compute_stats(df_critical)
    plot3_stats = stats_critical[stats_critical['plot_id'] == 'Plot3'].iloc[0]
    assert plot3_stats['moisture_status'] == 'Critical'
    assert plot3_stats['ec_status'] == 'Critical'
    assert plot3_stats['ph_status'] == 'Critical'
    
    # Check Plot2
    plot2_stats = stats[stats['plot_id'] == 'Plot2'].iloc[0]
    assert plot2_stats['moisture_status'] == 'Saturated' # >35
