import streamlit as st
import pandas as pd
import numpy as np

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
        grand_total_mL_needed = 0

        # --- Define Constants (Dosage Rate and Concentration) ---
        rate_mg_per_kg = 0 # Dose rate (mg/kg)
        concentration_mg_per_mL = 1 # Concentration (mg/mL) - set to 1 to prevent division by zero
        frequency_str = ""
        duration_days = 0
        notes = ""
        drug_name = selection.split(" ")[0]

        # --- MEDICATION PROTOCOLS ---
        if selection == "Panacur (General Parasites)":
            rate_mg_per_kg = 50.0 
            concentration_mg_per_mL = 100.0 # 100 mg/mL suspension
            frequency_str = "SID (Once Daily)"
            duration_days = 5 # Corrected to 5 days
            notes = "Commonly called Fenbendazole. Give SID for 5 days per OPA Protocol."
        
        elif selection == "Toltrazuril (Coccidia)":
            rate_mg_per_kg = 30.0 
            concentration_mg_per_mL = 50.0 # 50 mg/mL (5% solution)
            frequency_str = "One time dose"
            duration_days = 1 
            notes = "One-time dose only. Needs to be compounded or sourced."
            
        elif selection == "Doxycycline (URI)":
            rate_mg_per_kg = 5.0
            concentration_mg_per_mL = 50.0 # 50 mg/mL liquid
            frequency_str = "BID (Twice Daily)"
            duration_days = 10
            notes = "Give BID for 10 days."
            
        elif selection == "Doxycycline (Heartworm)":
            rate_mg_per_kg = 10.0 # Higher dose for HW protocol
            concentration_mg_per_mL = 50.0 
            frequency_str = "SID (Once Daily)"
            duration_days = 30
            notes = "Give SID for 30 days as part of heartworm treatment."
            
        elif selection == "Metronidazole (Diarrhea)":
            rate_mg_per_kg = 15.0
            concentration_mg_per_mL = 50.0 # 50 mg/mL liquid
            frequency_str = "BID (Twice Daily)"
            duration_days = 5
            notes = "Give BID for 5 days. Use for non-specific diarrhea."
            
        elif selection == "Metronidazole (Giardia)":
            rate_mg_per_kg = 25.0 # Higher dose for Giardia
            concentration_mg_per_mL = 50.0
            frequency_str = "BID (Twice Daily)"
            duration_days = 5
            notes = "Give BID for 5 days. For confirmed Giardia infection."
        
        # Display the protocol details used for calculations
        st.markdown(f"**Drug:** {drug_name} | **Rate:** {rate_mg_per_kg:.1f} mg/kg | **Conc:** {concentration_mg_per_mL:.1f} mg/mL | **Freq:** {frequency_str} | **Duration:** {duration_days} days")
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
            
            # 1. Dose needed in mg per administration
            # Dose (mg) = Rate (mg/kg) * Weight (kg)
            dose_mg_per_admin = rate_mg_per_kg * weight_kg
            
            # 2. Volume to Administer in mL per administration
            # Volume (mL) = Dose (mg) / Concentration (mg/mL)
            dose_mL_per_admin = dose_mg_per_admin / concentration_mg_per_mL
            
            # 3. Total volume needed for the entire protocol for this animal
            total_mL_per_animal = dose_mL_per_admin * total_doses
            
            # 4. Summing totals for all animals
            grand_total_mL_needed += total_mL_per_animal

            # --- PREPARE RESULTS ROW ---
            results_data.append({
                "Animal #": i + 1,
                "Weight (lbs)": f"{weight_lbs:.1f}",
                "Weight (kg)": f"{weight_kg:.2f}",
                "Dose (mg)": f"{dose_mg_per_admin:.1f}",
                "**mL per Dose**": f"**{dose_mL_per_admin:.3f}**",
                "Total mL (Protocol)": f"{total_mL_per_animal:.2f}",
            })

        # --- DISPLAY RESULTS ---
        results_df = pd.DataFrame(results_data)
        
        st.subheader("Dosage Results")
        # Format the table for better display
        st.dataframe(
            results_df,
            hide_index=True,
            use_container_width=True
        )

        st.markdown("---")
        
        # --- GRAND TOTAL SUMMARY ---
        if len(weights_list) > 1:
            st.metric(
                label=f"**Grand Total Protocol Volume (for {len(weights_list)} animals)**", 
                value=f"{grand_total_mL_needed:.2f} mL"
            )
            st.caption(f"This is the total volume of medication ({drug_name}) needed to treat all animals for the full {duration_days}-day protocol.")
            
        else:
             st.metric(
                label=f"**Total Protocol Volume Needed**", 
                value=f"{grand_total_mL_needed:.2f} mL"
            )
            
    elif len(weights_list) == 0 and weights_input and selection != "Select a medication...":
         st.warning("Please ensure weights are entered correctly (positive numbers separated by commas).")
         
    elif len(weights_list) > 0 and selection == "Select a medication...":
        st.warning("Please select a medication from the dropdown menu.")
        
    # Run the app function if the file is executed directly
if __name__ == "__main__":
    calculate_meds()
