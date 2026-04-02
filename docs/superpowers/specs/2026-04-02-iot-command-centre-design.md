# Design Spec: IoT Hardware Hangar (v19.0)

## 1. Overview
The **IoT Hardware Hangar** is a dedicated command terminal designed to simulate the real-world connection and management of agricultural IoT sensors. This feature bridges the gap between raw data analysis and physical field operations, providing a high-immersion "Research Lab" experience for the **EE4409 CA2** project.

## 2. Interaction Design
### 2.1 Navigation
- **Location**: A new 6th tab in the main dashboard workspace labeled **"IoT COMMAND"**.
- **Layout**: A responsive 3-column grid of **Hardware Cards**.

### 2.2 The Hardware Card (Plot Node Unit)
Each card represents a forensic gateway managing a cluster of physical sensors.
- **Visual Identity**: Pierre's Exotic Research Lab style (pixelated glassware/tech).
- **Status LED**: Neon Mint (Online), Red (Signal Lost), Amber (Low Battery).
- **Control Actuators**: 
  - **Manual Irrigation Toggle**: Triggers a simulated override event.
  - **Ping Button**: Refreshes the hardware heartbeat.
  - **Calibration Popover**: Allows tweaking reporting intervals (1s to 60m).

### 2.3 The Provisioning Handshake
A "Secure Link" function to mock the addition of new hardware.
- **Fields**: Communication Protocol (MQTT/LoRaWAN), Target IP Address, Secure Access Token.
- **Animation**: A multi-phase forensic progress bar simulating RSA key exchange and packet syncing.

### 2.4 Data-Hardware Sync
- Each node is mapped to specific data points: `soil_moisture_pct`, `soil_ec_ds_m`, `soil_ph`, and `soil_temp_c`.
- **Hardware Context**: If a node is "Offline" in the Hangar, the AI Advisor will notify the researcher of a "Sensor Data Gap."

## 3. Technical Requirements
- **State Management**: Mock device state initialized in `st.session_state.iot_devices`.
- **UI Logic**: Implementation using `st.columns`, `st_html` with glassmorphism, and pixel-font button styling.

## 4. Design Aesthetics
- **Theme**: Deep Forest / Neon Mint / Stardew Valley 'Pierre's Lab'.
- **Icons**: Pixel-art sensor arrays and lab equipment.
