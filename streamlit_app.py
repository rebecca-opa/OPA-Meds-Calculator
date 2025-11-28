import streamlit as st
import pandas as pd

def calculate_meds():
    st.set_page_config(page_title="OPA Meds Calculator", page_icon="🐾")
    
    st.title("🐾 OPA Meds Calculator")
    st.markdown("### Protocol & Litter Calculator")
    st.info("Enter weights in **lbs**. For a litter, separate weights with commas (e.g., `2.5, 3.0, 4.2`).")

    # 1. Input: Weights (Text Area to allow multiple)
    weights_input = st.text_area("Enter Animal Weight(s) in lbs:", placeholder="e.g. 10.5 or 2.5, 3.0, 2.8")

    # 2. Input: Medication Options
    med_options = [
        "Select a medication...",
        "Panacur (General Parasites)",
        "Toltrazuril (Coccidia)",
        "Doxycycline (URI)",
        "Doxycycline (Heartworm)",
        "Metronidazole (Diarrhea)",
        "Metronidazole (Giardia)"
    ]
    
    selection = st.selectbox("Select Medication & Indication", med_options)

    # Helper function to clean and parse weights
    def parse_weights(input_str):
        weights = []
        if input_str:
            # Replace newlines with commas, split by comma
            raw_list = input_str.replace('\n', ',').split(',')
            for w in raw_list:
                try:
                    val = float(w.strip())
                    if val > 0:
                        weights.append(val)
                except ValueError:
                    pass
        return weights

    # 3. Logic & Calculations
    weights_list = parse_weights(weights_input)

    if len(weights_list) > 0 and selection != "Select a medication...":
        
        st.divider()
        st.subheader(f"Protocol: {selection}")
        
        results_data = []
        grand_total_needed = 0
        unit = "mg" # Default unit

        # --- PROCESS EACH ANIMAL ---
        for weight_lbs in weights_list:
            weight_kg = weight_lbs / 2.20462
            
            dose_per_admin = 0
            frequency_str = ""
            duration_days = 0
            total_per_animal = 0
