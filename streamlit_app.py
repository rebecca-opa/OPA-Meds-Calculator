import streamlit as st
import pandas as pd
import numpy as np

# --- 1. PROTOCOL DEFINITIONS ---
# Central dictionary for easy maintenance of all medication protocols
PROTOCOLS = {
    "Panacur (General Parasites)": {"rate": 50.0, "conc": 100.0, "freq": "SID (Once Daily)", "duration": 5, "notes": "Fenbendazole. Give SID for 5 days.", "force_liquid": True},
    "Toltrazuril (Coccidia)": {"rate": 30.0, "conc": 50.0, "freq": "SID (Once Daily)", "duration": 3, "notes": "Give SID for 3 days. Needs to be compounded or sourced.", "force_liquid": True},
    "Doxycycline (URI)": {"rate": 5.0, "conc": 50.0, "freq": "BID (Twice Daily)", "duration": 10, "notes": "Give BID for 10 days."},
    "Doxycycline (Heartworm)": {"rate": 10.0, "conc": 50.0, "freq": "SID (Once Daily)", "duration": 30, "notes": "Give SID for 30 days as part of heartworm treatment."},
    "Metronidazole (Diarrhea)": {"rate": 15.0, "conc": 50.0, "freq": "BID (Twice Daily)", "duration": 5, "notes": "Give BID for 5 days. Use for non-specific diarrhea."},
    "Metronidazole (Giardia)": {"rate": 25.0, "conc": 50.0, "freq": "BID (Twice Daily)", "duration": 5, "notes": "Give BID for 5 days. For confirmed Giardia infection."},
}

# --- 2. HELPER FUNCTIONS ---

def get_practical_tablet_fraction(decimal_dose):
    """
    Converts a decimal dose (in tablets) to the nearest practical fraction (1/2, 1/4, 1/8)
    for easy cutting, and returns a display string.
    """
    if decimal_dose <= 0:
        return "0"

    # Round to the nearest 1/8th increment (0.125)
    eights = round(decimal_dose * 8)
    
    # If eights is 0 (due to rounding down), but the original dose was positive, return the lowest practical cut.
    if eights == 0 and decimal_dose > 0.001:
        eights = 1 # Smallest dose is often rounded up to 1/8th

    # Handle whole numbers and simplify fractions
    if eights >= 8:
        whole = int(eights // 8)
        remainder_eights = eights % 8
        
        # Recalculate fraction string for the remainder
        fraction_str = get_practical_tablet_fraction(remainder_eights / 8)
        
        if fraction_str == "0":
             return f"{whole}"
        else:
             # If whole is 0, just return the fraction string (already handled below)
             # If whole is > 0, return "1 + 1/2" format
             return f"{whole} + {fraction_str}" if whole > 0 else fraction_str

    # Process fractions less than 1
    if eights == 1:
        return "1/8"
    elif eights == 2:
        return "1/4"
    elif eights == 3:
        return "3/8"
    elif eights == 4:
        return "1/2"
    elif eights == 5:
        return "5/8"
    elif eights == 6:
        return "3/4"
    elif eights == 7:
        return "7/8"
    elif eights == 8:
        return "1"
        
    return "0" # Should only happen if eights is 0

def parse_weights(input_str):
    """Cleans and parses a string of comma or newline separated weights into a list of floats."""
    weights = []
    if input_str:
        raw_list = input_str.replace('\n', ',').split(',')
        for w in raw_list:
            clean_w = w.strip()
            if clean_w:
                try:
                    val = float(clean_w)
                    if val > 0:
                        weights.append(val)
                except ValueError:
                    pass
    return weights

# --- 3. MAIN APPLICATION FUNCTION ---

def calculate_meds():
    st.set_page_config(page_title="OPA Meds Calculator", page_icon="🐾", layout="wide")
    
    st.title("🐾 OPA Meds Calculator")
    st.markdown("### Protocol & Litter Calculator")
    st.info("Enter weights in **lbs**. For a litter, separate weights with commas (e.g., `2.5, 3.0, 4.2`) or list them on separate lines.")

    # Input: Weights 
    weights_input = st.text_area("Enter Animal Weight(s) in lbs:", placeholder="e.g. 10.5 or 2.5, 3.0, 2.8")

    # Input: Medication Options
    med_options = ["Select a medication..."] + list(PROTOCOLS.keys())
    selection = st.selectbox("Select Medication & Indication", med_options)

    # --- Conditional Sidebar Inputs ---
    calc_type = 'Liquid (mL)'
    tablet_strength_mg = 0
    protocol_data = PROTOCOLS.get(selection)
    
    if protocol_data:
        drug_name = selection.split(" ")[0]
        
        # Determine if we should show dosage form options
        is_tablet_eligible = drug_name in ["Doxycycline", "Metronidazole"]
        
        if is_tablet_eligible:
            st.sidebar.markdown("---")
            st.sidebar.subheader(f"{drug_name} Options")

            # Set calculation type to Tablet as requested by the user to remove liquid option
            calc_type = 'Tablet (mg)'
            st.sidebar.caption(f"Dosage Form is fixed to: **Tablet (mg)**")

            # Set options based on drug type
            options = [0]
            default_index = 0
            if drug_name == "Doxycycline":
                options = [0, 100] # Fixed to 100mg
                default_index = 1
            elif drug_name == "Metronidazole":
                options = [0, 250, 500]
                default_index = 1 # Defaulting to 250mg 
                
            tablet_strength_mg = st.sidebar.selectbox(
                "Available Tablet Strength (mg):",
                options,
                index=default_index,
                key=f'{drug_name}_strength',
                help=f"Select the strength of the {drug_name} tablet you will be cutting."
            )

        # Force liquid for Panacur/Toltrazuril
        if protocol_data.get("force_liquid"):
             calc_type = 'Liquid (mL)'
             st.sidebar.caption(f"*{drug_name} is only calculated in liquid form.*")


    # 4. Logic & Calculations
    weights_list = parse_weights(weights_input)
    
    # Guard clauses
    if not protocol_data or not weights_list:
        if weights_input and not weights_list:
             st.warning("Please ensure weights are entered correctly (positive numbers separated by commas).")
        return
        
    if calc_type == 'Tablet (mg)' and tablet_strength_mg == 0:
        st.warning(f"Please select a valid Available Tablet Strength for {drug_name} to perform tablet calculations.")
        return

    st.divider()
    st.subheader(f"Protocol: {selection}")
    
    # Extract protocol details
    rate_mg_per_kg = protocol_data["rate"]
    concentration_mg_per_mL = protocol_data["conc"]
    frequency_str = protocol_data["freq"]
    duration_days = protocol_data["duration"]
    notes = protocol_data["notes"]
    drug_name = selection.split(" ")[0]

    # Calculate doses per day
    doses_per_day = 1
    if "BID" in frequency_str: doses_per_day = 2
    if "TID" in frequency_str: doses_per_day = 3
    total_doses = doses_per_day * duration_days

    # Display Protocol Header
    if calc_type == 'Tablet (mg)':
        conc_display = f"**Tablet Strength:** {tablet_strength_mg:.0f} mg/tablet"
        notes += f" Calculation based on {tablet_strength_mg} mg tablets."
    else:
        conc_display = f"**Conc:** {concentration_mg_per_mL:.1f} mg/mL"
        if is_tablet_eligible:
             notes += f" Calculation based on {concentration_mg_per_mL} mg/mL liquid."
        
    st.markdown(f"**Drug:** {drug_name} | **Rate:** {rate_mg_per_kg:.1f} mg/kg | {conc_display} | **Freq:** {frequency_str} | **Duration:** {duration_days} days")
    st.caption(f"*{notes}*")
    
    results_data = []
    grand_total_mg = 0 
    grand_total_mL_sum = 0.0 # Numeric accumulator for total liquid volume

    # --- PROCESS EACH ANIMAL ---
    for i, weight_lbs in enumerate(weights_list):
        weight_kg = weight_lbs / 2.20462
        dose_mg_per_admin = rate_mg_per_kg * weight_kg
        grand_total_mg += dose_mg_per_admin * total_doses # Accumulate total mg needed

        if calc_type == 'Liquid (mL)':
            dose_mL_per_admin = dose_mg_per_admin / concentration_mg_per_mL
            total_mL_protocol = dose_mL_per_admin * total_doses
            
            grand_total_mL_sum += total_mL_protocol # Accumulate the numeric total
            
            results_data.append({
                "Animal #": i + 1,
                "Weight (lbs)": f"{weight_lbs:.1f}",
                "Dose (mg)": f"{dose_mg_per_admin:.1f}",
                "**mL per Dose**": f"**{dose_mL_per_admin:.3f}**",
                "Total mL (Protocol)": f"{total_mL_protocol:.2f}",
            })

        elif calc_type == 'Tablet (mg)':
            dose_tablets_raw = dose_mg_per_admin / tablet_strength_mg
            total_tablets_protocol = dose_tablets_raw * total_doses
            
            fractional_dose_display = get_practical_tablet_fraction(dose_tablets_raw)
            
            results_data.append({
                "Animal #": i + 1,
                "Weight (lbs)": f"{weight_lbs:.1f}",
                "Dose (mg)": f"{dose_mg_per_admin:.1f}",
                "**Practical Tablets/Dose**": f"**{fractional_dose_display}**",
                "Raw Decimal Dose": f"{dose_tablets_raw:.3f}",
                "Total Tablets (Protocol)": f"{total_tablets_protocol:.2f}",
            })

    # --- DISPLAY RESULTS ---
    results_df = pd.DataFrame(results_data)
    st.subheader("Dosage Results")
    
    # Reorder columns for optimal display
    if calc_type == 'Tablet (mg)':
        result_col = '**Practical Tablets/Dose**'
        total_col = 'Total Tablets (Protocol)'
        cols = ['Animal #', 'Weight (lbs)', result_col, total_col, 'Dose (mg)', 'Raw Decimal Dose']
    else:
        result_col = '**mL per Dose**'
        total_col = 'Total mL (Protocol)'
        cols = ['Animal #', 'Weight (lbs)', result_col, total_col, 'Dose (mg)']

    results_df = results_df[cols]
    
    st.dataframe(results_df, hide_index=True, use_container_width=True)
    
    if calc_type == 'Tablet (mg)':
        st.caption("The 'Practical Tablets/Dose' is rounded to the nearest 1/8th for easy tablet cutting. The 'Total Tablets (Protocol)' shows the exact decimal amount needed for inventory.")

    st.markdown("---")
    
    # --- GRAND TOTAL SUMMARY ---
    if calc_type == 'Liquid (mL)':
        # FIX: Use the numeric accumulator instead of summing formatted strings
        grand_total_volume = grand_total_mL_sum 
        total_label = f"**Grand Total Protocol Volume ({len(weights_list)} animals)**"
        total_value = f"{grand_total_volume:.2f} mL"
        caption_text = f"Total volume of medication needed for the full {duration_days}-day protocol."
        
    elif calc_type == 'Tablet (mg)':
        total_tablets_needed = grand_total_mg / tablet_strength_mg
        total_label = f"**Total Tablets of {tablet_strength_mg}mg Needed ({len(weights_list)} animals)**"
        total_value = f"{total_tablets_needed:.2f} Tablets"
        caption_text = f"Total tablets required for the full {duration_days}-day protocol."
        
    st.metric(label=total_label, value=total_value)
    st.caption(caption_text)
        

if __name__ == "__main__":
    calculate_meds()
