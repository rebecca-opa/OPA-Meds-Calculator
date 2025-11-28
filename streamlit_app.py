import streamlit as st

def calculate_meds():
    # Page setup
    st.set_page_config(page_title="OPA Meds Calculator", page_icon="🐾")
    
    st.title("🐾 OPA Meds Calculator")
    st.markdown("### Enter the weight in **lbs** to see the protocol.")

    # 1. Input: Weight
    # We use step=0.1 so you can enter decimal weights (e.g. 10.5 lbs)
    weight_lbs = st.number_input("Animal Weight (lbs)", min_value=0.0, step=0.1, format="%.1f")

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

    # 3. Logic & Calculations
    if weight_lbs > 0 and selection != "Select a medication...":
        
        # Calculate Weight in KG for meds that use it
        weight_kg = weight_lbs / 2.20462
        
        st.divider()
        st.subheader(f"Results for {weight_lbs} lbs ({weight_kg:.2f} kg)")

        # --- PROTOCOLS ---

        # 1. Panacur
        # Dose: 1ml per 4lbs | Frequency: Once a day | Duration: 5 days
        if selection == "Panacur (General Parasites)":
            daily_dose_ml = weight_lbs / 4
            duration = 5
            total_needed = daily_dose_ml * duration
            
            st.info(f"**Medication:** Panacur (Fenbendazole)")
            st.success(f"**Daily Dose:** Give {daily_dose_ml:.2f} ml once a day")
            st.warning(f"**Duration:** {duration} days")
            st.write(f"**Total Volume Needed:** {total_needed:.2f} ml")

        # 2. Toltrazuril
        # Dose: 1ml per 10lbs | Frequency: Once a day | Duration: 3 days
        elif selection == "Toltrazuril (Coccidia)":
            daily_dose_ml = weight_lbs / 10
            duration = 3
            total_needed = daily_dose_ml * duration
            
            st.info(f"**Medication:** Toltrazuril")
            st.success(f"**Daily Dose:** Give {daily_dose_ml:.2f} ml once a day")
            st.warning(f"**Duration:** {duration} days")
            st.write(f"**Total Volume Needed:** {total_needed:.2f} ml")

        # 3. Doxycycline (URI)
        # Dose: 2.5mg per 1lb | Frequency: 2x a day | Duration: 10 days
        elif selection == "Doxycycline (URI)":
            dose_mg = 2.5 * weight_lbs
            duration = 10
            frequency = 2
            total_mg = dose_mg * frequency * duration
            
            st.info(f"**Medication:** Doxycycline (URI Protocol)")
            st.success(f"**Per Dose:** Give {dose_mg:.0f} mg")
            st.write(f"*Frequency: {frequency} times a day (BID)*")
            st.warning(f"**Duration:** {duration} days")
            st.write(f"**Total Meds Needed:** {total_mg:.0f} mg total")

        # 4. Doxycycline (Heartworm)
        # Dose: 10mg per kg | Frequency: 2x a day | Duration: 30 days
        elif selection == "Doxycycline (Heartworm)":
            dose_mg = 10 * weight_kg
            duration = 30
            frequency = 2
            total_mg = dose_mg * frequency * duration
            
            st.info(f"**Medication:** Doxycycline (Heartworm Protocol)")
            st.success(f"**Per Dose:** Give {dose_mg:.0f} mg")
            st.write(f"*Frequency: {frequency} times a day (BID)*")
            st.warning(f"**Duration:** {duration} days")
            st.write(f"**Total Meds Needed:** {total_mg:.0f} mg total")

        # 5. Metronidazole (Diarrhea)
        # Dose: 10mg per kg | Frequency: 2x a day | Duration: 5 days
        elif selection == "Metronidazole (Diarrhea)":
            dose_mg = 10 * weight_kg
            duration = 5
            frequency = 2
            total_mg = dose_mg * frequency * duration
            
            st.info(f"**Medication:** Metronidazole (General Diarrhea)")
            st.success(f"**Per Dose:** Give {dose_mg:.0f} mg")
            st.write(f"*Frequency: {frequency} times a day (BID)*")
            st.warning(f"**Duration:** {duration} days")
            st.write(f"**Total Meds Needed:** {total_mg:.0f} mg total")

        # 6. Metronidazole (Giardia)
        # Dose: 25mg per kg | Frequency: 2x a day | Duration: 5 days
        elif selection == "Metronidazole (Giardia)":
            dose_mg = 25 * weight_kg
            duration = 5
            frequency = 2
            total_mg = dose_mg * frequency * duration
            
            st.info(f"**Medication:** Metronidazole (Giardia Protocol)")
            st.success(f"**Per Dose:** Give {dose_mg:.0f} mg")
            st.write(f"*Frequency: {frequency} times a day (BID)*")
            st.warning(f"**Duration:** {duration} days")
            st.write(f"**Total Meds Needed:** {total_mg:.0f} mg total")

if __name__ == "__main__":
    calculate_meds()