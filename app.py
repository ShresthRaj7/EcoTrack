import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import datetime
from database import Session, UserData

st.set_page_config(page_title="Carbon Footprint Estimator", layout="centered")

st.title("Carbon Footprint Estimator")
st.markdown("Estimate your yearly carbon footprint and learn how to reduce it!")

st.sidebar.header("📊 Enter Your Details")

# Emission Factors (kg CO2 per unit)
emission_factors = {
    "car_km": 0.192,
    "bike_km": 0.021,
    "bus_km": 0.105,
    "flight_km": 0.255,
    "electricity_kwh": 0.85,
    "lpg_kg": 2.983,
    "diet": {
        "Vegetarian": 1500,
        "Mixed": 2500,
        "Non-Vegetarian": 3300
    },
    "clothing_item": 25,
    "gadgets": 100
}

# Inputs
car_km = st.sidebar.number_input("Car travel (km/year)", min_value=0, value=8000)
bike_km = st.sidebar.number_input("Bike travel (km/year)", min_value=0, value=2000)
bus_km = st.sidebar.number_input("Bus travel (km/year)", min_value=0, value=1500)
flight_km = st.sidebar.number_input("Flights (km/year)", min_value=0, value=2500)

electricity_kwh = st.sidebar.number_input("Electricity usage (kWh/year)", min_value=0, value=1200)
lpg_kg = st.sidebar.number_input("LPG usage (kg/year)", min_value=0, value=180)

diet_type = st.sidebar.selectbox("Your diet type", ["Vegetarian", "Mixed", "Non-Vegetarian"])
clothes = st.sidebar.number_input("Clothes bought per year", min_value=0, value=15)
gadgets = st.sidebar.number_input("Gadgets bought per year", min_value=0, value=2)

# Calculations
transport_emission = (
    car_km * emission_factors["car_km"] +
    bike_km * emission_factors["bike_km"] +
    bus_km * emission_factors["bus_km"] +
    flight_km * emission_factors["flight_km"]
)

energy_emission = (
    electricity_kwh * emission_factors["electricity_kwh"] +
    lpg_kg * emission_factors["lpg_kg"]
)

lifestyle_emission = (
    emission_factors["diet"].get(diet_type, 0) +
    clothes * emission_factors["clothing_item"] +
    gadgets * emission_factors["gadgets"]
)

total_emission = transport_emission + energy_emission + lifestyle_emission
total_emission = max(total_emission, 0)  # no negatives

trees_needed = total_emission / 22  # kg CO2 per tree per year
trees_needed = max(trees_needed, 0)

# Display results
st.subheader("Your Estimated Annual Emissions")
st.success(f"Total CO₂ Emissions: {total_emission:.2f} kg/year")
st.info(f"Trees needed to offset this: {trees_needed:.0f} trees/year")

emission_data = {
    "Transportation": transport_emission,
    "Energy": energy_emission,
    "Lifestyle": lifestyle_emission
}

# Visualization
st.subheader("Emission Breakdown")
fig, ax = plt.subplots()
ax.bar(emission_data.keys(), emission_data.values(), color=["#4CAF50", "#FF9800", "#2196F3"])
ax.set_ylabel("kg CO₂/year")
ax.set_title("Your Carbon Footprint Breakdown")
st.pyplot(fig)

# Report generation and download
st.subheader("Generate Report")

if st.button("Generate and Download PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Carbon Footprint Report", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Date: {datetime.date.today()}", ln=True, align="C")
    pdf.ln(10)

    for k, v in emission_data.items():
        pdf.cell(200, 10, txt=f"{k} Emission: {v:.2f} kg CO2/year", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Total Emissions: {total_emission:.2f} kg CO2/year", ln=True)
    pdf.cell(200, 10, txt=f"Trees Required to Offset: {trees_needed:.0f}", ln=True)

    pdf_output = BytesIO()
    # Use 'latin-1' encoding but ensure no emojis in strings
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)

    st.download_button(
        label="Download PDF Report",
        data=pdf_output,
        file_name="carbon_footprint_report.pdf",
        mime="application/pdf"
    )

    # Save to database
    try:
        session = Session()
        data = UserData(
            car_km=car_km,
            bike_km=bike_km,
            bus_km=bus_km,
            flight_km=flight_km,
            electricity_kwh=electricity_kwh,
            lpg_kg=lpg_kg,
            diet_type=diet_type,
            clothes=clothes,
            gadgets=gadgets,
            total_emission=total_emission,
            trees_needed=trees_needed
        )
        session.add(data)
        session.commit()
        session.close()
        st.success("Data saved to the database successfully!")
    except Exception as e:
        st.error(f"Failed to save data: {e}")

st.markdown("---")
st.caption("All values are approximations. For educational use only.")
