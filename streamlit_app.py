import streamlit as st
import pandas as pd
import numpy as np

def calculate_meds():
    st.set_page_config(page_title="OPA Meds Calculator", page_icon="🐾")
    
    st.title("🐾 OPA Meds Calculator")
    st.markdown("### Protocol & Litter Calculator")
    st.info("Enter weights in **lbs**. For a litter, separate weights with commas (e.g., `2.5, 3.0, 4.2`) or list them on separate lines.")

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

    # --- NEW: Conditional Inputs for Metronidazole and Doxycycline Tablets ---
    calc_type = 'Liquid (mL)'
    tablet_strength_mg = 0

    if selection.startswith("Metronidazole"):
        st.sidebar.markdown("---")
        st.sidebar.subheader("Metronidazole Options")
        
        # Input: Calculation Type (Liquid vs Tablet)
        calc_type = st.sidebar.radio(
            "Target Dosage Form:",
            ['Liquid (mL)', 'Tablet (mg)'],
            index=0,
            key='metro_form',
            help="Choose 'Liquid (mL)' if administering suspension (50 mg/mL), or 'Tablet (mg)' if using a compounded tablet form."
        )
        
        if calc_type == 'Tablet (mg)':
            tablet_strength_mg = st.sidebar.selectbox(
                "Available Tablet Strength (mg):",
                [0, 250, 500],
                index=1,
                key='metro_strength',
                help="Select the strength of the tablet you will be cutting to achieve the required dose."
            )

    elif selection.startswith("Doxycycline"):
        st.sidebar.markdown("---")
        st.sidebar.subheader("Doxycycline Options")

        # Input: Calculation Type (Liquid vs Tablet)
        calc_type = st.sidebar.radio(
            "Target Dosage Form:",
            ['Liquid (mL)', 'Tablet (mg)'],
            index=1, # Default to Tablet (mg) as requested by user
            key='doxy_form',
            help="Choose 'Liquid (mL)' if administering suspension (50 mg/mL), or 'Tablet (mg)' if using a tablet form."
        )

        if calc_type == 'Tablet (mg)':
            # Doxycycline tablets are 100 mg based on user input
            tablet_strength_mg = st.sidebar.selectbox(
                "Available Tablet Strength (mg):",
                [0, 100],
                index=1,
                key='doxy_strength',
                help="Select the strength of the tablet you will be cutting (100mg)."
            )
            
    # Add warning if tablet strength is not selected for a drug requiring it
    if (selection.startswith("Metronidazole") or selection.startswith("Doxycycline")) and calc_type == 'Tablet (mg)' and tablet_strength_mg == 0:
        st.warning(f"Please select a valid Available Tablet Strength for {selection.split(' ')[0]} to perform tablet calculations.")

    # Helper function to clean and parse weights
    def parse_weights(input_str):
        weights = []
        if input_str:
            # Replace newlines with commas, split by comma, and remove extra whitespace
            raw_list = input_str.replace('\n', ',').split(',')
            for w in raw_list:
                # Use strip() to handle spaces around numbers
                clean_w = w.strip()
                if clean_w: # Check if string is not empty
                    try:
                        val = float(clean_w)
                        if val > 0:
                            weights.append(val)
                    except ValueError:
                        # Ignore any text or non-numeric entries
                        pass
        return weights

    # 3. Logic & Calculations
    weights_list = parse_weights(weights_input)
    
    # Guard clause for invalid tablet selection
    if (selection.startswith("Metronidazole") or selection.startswith("Doxycycline")) and calc_type == 'Tablet (mg)' and tablet_strength_mg == 0:
         weights_list = [] # Stop calculation if required inputs are missing
    
    if len(weights_list) > 0 and selection != "Select a medication...":
        
        st.divider()
        st.subheader(f"Protocol: {selection}")
        
        results_data = []
        grand_total_volume = 0 # Will hold total mL or total mg based on calc_type

        # --- Define Constants (Dosage Rate and Concentration) ---
        rate_mg_per_kg = 0 # Dose rate (mg/kg)
        concentration_mg_per_mL = 1 # Concentration (mg/mL) - default
        frequency_str = ""
        duration_days = 0
        notes = ""
        drug_name = selection.split(" ")[0]
        liquid_conc = 50.0 # Default liquid concentration for Doxy and Metro

        # --- MEDICATION PROTOCOLS ---
        if selection == "Panacur (General Parasites)":
            rate_mg_per_kg = 50.0  
            concentration_mg_per_mL = 100.0 # 100 mg/mL suspension
            frequency_str = "SID (Once Daily)"
            duration_days = 5 # 5 days per OPA Protocol
            notes = "Commonly called Fenbendazole. Give SID for 5 days per OPA Protocol. (Liquid calculation only)"
            calc_type = 'Liquid (mL)' # Force liquid for Panacur

        elif selection == "Toltrazuril (Coccidia)":
            rate_mg_per_kg = 30.0  
            concentration_mg_per_mL = 50.0 # 50 mg/mL (5% solution)
            frequency_str = "SID (Once Daily)"
            duration_days = 3 # 3 days per OPA Protocol
            notes = "Give SID for 3 days. Needs to be compounded or sourced. (Liquid calculation only)"
            calc_type = 'Liquid (mL)' # Force liquid for Toltrazuril
            
        elif selection == "Doxycycline (URI)":
            rate_mg_per_kg = 5.0
            concentration_mg_per_mL = liquid_conc
            frequency_str = "BID (Twice Daily)"
            duration_days = 10
            notes = "Give BID for 10 days."
            
        elif selection == "Doxycycline (Heartworm)":
            rate_mg_per_kg = 10.0 # Higher dose for HW protocol
            concentration_mg_per_mL = liquid_conc
            frequency_str = "SID (Once Daily)"
            duration_days = 30
            notes = "Give SID for 30 days as part of heartworm treatment."
            
        elif selection == "Metronidazole (Diarrhea)":
            rate_mg_per_kg = 15.0
            concentration_mg_per_mL = liquid_conc
            frequency_str = "BID (Twice Daily)"
            duration_days = 5
            notes = "Give BID for 5 days. Use for non-specific diarrhea."
            
        elif selection == "Metronidazole (Giardia)":
            rate_mg_per_kg = 25.0 # Higher dose for Giardia
            concentration_mg_per_mL = liquid_conc
            frequency_str = "BID (Twice Daily)"
            duration_days = 5
            notes = "Give BID for 5 days. For confirmed Giardia infection."

        # Add notes about the concentration/strength used in calculation
        if calc_type == 'Tablet (mg)' and tablet_strength_mg > 0:
            conc_display = f"**Tablet Strength:** {tablet_strength_mg:.0f} mg/tablet"
            notes += f" Calculation based on {tablet_strength_mg} mg tablets."
        else:
            conc_display = f"**Conc:** {concentration_mg_per_mL:.1f} mg/mL"
            if selection.startswith("Doxycycline") or selection.startswith("Metronidazole"):
                notes += f" Calculation based on {concentration_mg_per_mL} mg/mL liquid."
            
        st.markdown(f"**Drug:** {drug_name} | **Rate:** {rate_mg_per_kg:.1f} mg/kg | {conc_display} | **Freq:** {frequency_str} | **Duration:** {duration_days} days")
        st.caption(f"*{notes}*")

        # Determine doses per day based on frequency
        doses_per_day = 1
        if "BID" in frequency_str:
            doses_per_day = 2
        elif "TID" in frequency_str:
            doses_per_day = 3

        total_doses = doses_per_day * duration_days
        
        # --- PROCESS EACH ANIMAL ---
        for i, weight_lbs in enumerate(weights_list):
            
            # --- CONVERSIONS & CALCULATIONS ---
            weight_kg = weight_lbs / 2.20462
            
            # 1. Dose needed in mg per administration (Common to both)
            # Dose (mg) = Rate (mg/kg) * Weight (kg)
            dose_mg_per_admin = rate_mg_per_kg * weight_kg
            
            # Placeholder for dynamic output variables
            dose_unit_label = ""
            dose_unit_value = 0.0
            total_protocol_unit = 0.0
            
            if calc_type == 'Liquid (mL)':
                # 2. Volume to Administer in mL per administration
                # Volume (mL) = Dose (mg) / Concentration (mg/mL)
                dose_mL_per_admin = dose_mg_per_admin / concentration_mg_per_mL
                
                # 3. Total volume needed for the entire protocol for this animal
                total_protocol_unit = dose_mL_per_admin * total_doses
                grand_total_volume += total_protocol_unit
                
                dose_unit_label = "**mL per Dose**"
                dose_unit_value = dose_mL_per_admin
                
                results_data.append({
                    "Animal #": i + 1,
                    "Weight (lbs)": f"{weight_lbs:.1f}",
                    "Weight (kg)": f"{weight_kg:.2f}",
                    "Dose (mg)": f"{dose_mg_per_admin:.1f}",
                    dose_unit_label: f"**{dose_unit_value:.3f}**",
                    "Total mL (Protocol)": f"{total_protocol_unit:.2f}",
                })

            elif calc_type == 'Tablet (mg)' and tablet_strength_mg > 0:
                # 2. Number of tablets/fraction of tablet needed per administration
                # Tablets = Dose (mg) / Tablet Strength (mg/tablet)
                dose_tablets_per_admin = dose_mg_per_admin / tablet_strength_mg
                
                # 3. Total number of tablets needed for the entire protocol for this animal
                total_protocol_unit = dose_tablets_per_admin * total_doses
                
                # Grand total sums the total MG needed for the whole protocol/group
                total_mg_for_protocol = dose_mg_per_admin * total_doses
                grand_total_volume += total_mg_for_protocol
                
                dose_unit_label = "**Tablets per Dose**"
                dose_unit_value = dose_tablets_per_admin

                results_data.append({
                    "Animal #": i + 1,
                    "Weight (lbs)": f"{weight_lbs:.1f}",
                    "Weight (kg)": f"{weight_kg:.2f}",
                    "Dose (mg)": f"{dose_mg_per_admin:.1f}",
                    dose_unit_label: f"**{dose_unit_value:.3f}**",
                    "Total Tablets (Protocol)": f"{total_protocol_unit:.2f}",
                })

        # --- DISPLAY RESULTS ---
        results_df = pd.DataFrame(results_data)
        
        st.subheader("Dosage Results")
        
        # Drop irrelevant total columns and reorder for better visibility
        if calc_type == 'Tablet (mg)':
            results_df = results_df.drop(columns=['Total mL (Protocol)'], errors='ignore')
            result_col_name = '**Tablets per Dose**'
            total_col_name = 'Total Tablets (Protocol)'
        else:
            results_df = results_df.drop(columns=['Total Tablets (Protocol)'], errors='ignore')
            result_col_name = '**mL per Dose**'
            total_col_name = 'Total mL (Protocol)'

        # Reorder columns to put the main dose result and the total upfront
        if result_col_name in results_df.columns:
            cols = results_df.columns.tolist()
            
            # Move the main dose column (e.g., **mL per Dose**)
            cols.insert(1, cols.pop(cols.index(result_col_name)))
            # Move the total column (e.g., Total mL (Protocol))
            cols.insert(2, cols.pop(cols.index(total_col_name)))
            
            results_df = results_df[cols]
        
        st.dataframe(
            results_df,
            hide_index=True,
            use_container_width=True
        )

        st.markdown("---")
        
        # --- GRAND TOTAL SUMMARY ---
        if calc_type == 'Liquid (mL)':
            total_label = f"**Grand Total Protocol Volume (for {len(weights_list)} animals)**" if len(weights_list) > 1 else "**Total Protocol Volume Needed**"
            total_value = f"{grand_total_volume:.2f} mL"
            caption_text = f"This is the total volume of medication ({drug_name}) needed to treat all animals for the full {duration_days}-day protocol (Based on {concentration_mg_per_mL} mg/mL concentration)."
            
        elif calc_type == 'Tablet (mg)':
            # grand_total_volume holds the total MG needed for the whole group/protocol
            total_mg_needed = grand_total_volume
            total_tablets_needed = total_mg_needed / tablet_strength_mg
            
            total_label = f"**Total Tablets of {tablet_strength_mg}mg Needed (for {len(weights_list)} animals)**" if len(weights_list) > 1 else f"**Total Tablets of {tablet_strength_mg}mg Needed**"
            total_value = f"{total_tablets_needed:.2f} Tablets"
            caption_text = f"This is the total number of {tablet_strength_mg}mg tablets required to treat all animals for the full {duration_days}-day protocol."
            
        st.metric(
            label=total_label, 
            value=total_value
        )
        st.caption(caption_text)
            
    # --- ERROR HANDLING ---
    elif len(weights_list) == 0 and weights_input and selection != "Select a medication...":
        st.warning("Please ensure weights are entered correctly (positive numbers separated by commas).")
            
    elif len(weights_list) > 0 and selection == "Select a medication...":
        st.warning("Please select a medication from the dropdown menu.")
        
    # Run the app function if the file is executed directly
if __name__ == "__main__":
    calculate_meds()
