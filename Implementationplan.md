This is an excellent strategy. Using Streamlit is a perfect choice for CA2 because it allows you to build clean, interactive web applications using Python, and integrating an AI chatbot natively into Streamlit is highly impressive for demonstrating "non-expert usability."

Here is a comprehensive, CA2-optimized implementation plan for your Streamlit dashboard. This structure is designed to directly hit the requirements for both the **dashboard (7%)** and the **written project report (14%)** by focusing on system-level justification and non-expert accessibility.

### Overall Streamlit Dashboard Architecture
To keep it user-friendly, use Streamlit's sidebar (`st.sidebar`) to create four distinct tabs. 

#### Tab 1: Executive Overview & AI Assistant (The "Non-Expert" View)
*This tab satisfies the rubric requirement to "help a non-expert user monitor the system".*
*   **Traffic Light Warning System:** Use Streamlit's `st.metric` or `st.error`/`st.warning` boxes to display the current state of the 3 plots.
    *   🚨 **CRITICAL:** Irrigation System Offline (0mm recorded across all plots).
    *   🚨 **CRITICAL:** Plot 1 Drought & Salinity Stress (Moisture at 1.0%, EC at 4.8 dS/m).
    *   ⚠️ **WARNING:** Plot 2 Acidity Dip (pH at 4.92).
*   **The "AI Farm Assistant" Chatbot:** Since you want to integrate an AI API, use `st.chat_input` and `st.chat_message`. A farm manager can type, *"What is wrong with Plot 1?"* and your prompt-engineered AI can explain in plain English: *"Plot 1 is suffering from a lack of irrigation. Because the soil is drying out, salt is being pulled to the surface (capillary rise), which is why Salinity (EC) is spiking without any rainfall."* 

#### Tab 2: Historical Trends & Telemetry 
*This tab satisfies the requirement to "analyze the dataset to understand typical behavior and trends".*
*   Rather than showing all 504 rows of raw data, show the clean, aggregated visualizations you made in CA1.
*   Include the **Dual-Axis Moisture vs. Rainfall Chart** to visually prove to the user that moisture only increases during rain events and that the irrigation lines are dead.
*   Include the **Soil Status Timeline Heatmap** (Drought/Normal/Wet) so the farm manager can easily see the cyclical patterns of drought stress.

#### Tab 3: Action Center (Interventions)
*This tab satisfies the requirement to "provide clear, practical recommendations based on your analysis".*
*   Create a clean, actionable checklist for the farm technicians based on your CA1 forensics:
    *   **Action 1 (Immediate):** Inspect the main BMS irrigation controller and water pumps. The system has recorded 0.0mm of irrigation for 7 straight days.
    *   **Action 2 (Short-term):** Perform a fresh-water flush on Plot 1 to wash the accumulated surface salts (4.8 dS/m) back down below the root zone.
    *   **Action 3 (Short-term):** Apply a pH buffer (like agricultural lime) to Plot 2 to neutralize the 4.92 acidic dip and restore nutrient absorption.

#### Tab 4: System Upgrades (Alternative Sensing)
*This tab satisfies the requirement to "propose alternative or additional sensing modalities and justify them".*
*   This is where you showcase your engineering system knowledge. Create a layout of "Locked" or "Greyed Out" premium dashboard features, explaining what the dashboard *could* do if the farm invested in new sensors:
    *   **Deep Root Moisture:** Propose **Multi-depth Tensiometers (15cm, 30cm, 60cm)** to see if drought is just at the surface or killing the deep roots.
    *   **Salt Flux Tracking:** Propose **Drainage Lysimeters** to definitively prove your capillary rise hypothesis by tracking salt moving upward vs downward.
    *   **Pipe Flow Diagnostics:** Propose **Automated Flow Totalizers** on the water mains. This explains *why* irrigation is zero (e.g., did the software fail to send the signal, or is the physical pipe broken?).

### How to Maximize your CA2 Written Report (14%)
While the dashboard itself is worth 7%, the written report (8-10 pages) is worth 14% and the presentation is worth 21%. To max out your grade, ensure your written report explicitly includes:
1.  **Sensor Physics Summary:** Explain what sensors are currently being used (e.g., how soil EC sensors work, what units they use, and why 4.8 dS/m is bad). 
2.  **The "Non-Expert" Justification:** Explicitly state in your report *why* you built the AI chatbot. Explain that raw data like "EC = 4.8" means nothing to a layman, so the AI API bridges the gap between raw data and actionable human intelligence.
3.  **Cost vs. Information Justification:** When writing about your alternative sensors (Tensiometers and Lysimeters), create a small table comparing the cost of installing them versus the financial crop loss prevented by stopping the salt accumulation. 

Since you are using AI to help build the Streamlit prototype, **remember to fully document your prompts and the tools you used in the report**, and ensure you completely understand the Python code it generates.