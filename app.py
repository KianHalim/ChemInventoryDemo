import streamlit as st
import pandas as pd

st.title("Chemical Inventory Reporting Demo")

# Dropdown for report type
report_type = st.selectbox("Select Reporting Type", ["Tier II", "SARA 313", "VOC/HAP"])

# User inputs for multiple materials
num_materials = st.number_input("How many materials do you want to enter?", min_value=1, step=1)

materials = []  # List to store material data
sds_numbers = set()  # Track unique SDS numbers

for i in range(num_materials):
    st.subheader(f"Material {i+1}")

    sds_number = st.text_input(f"Enter SDS # for Material {i+1}", key=f"sds_{i}")

    # Check if SDS # is already entered
    if sds_number in sds_numbers:
        st.error(f"SDS # {sds_number} is already used. Each material must have a unique SDS #.")
    else:
        sds_numbers.add(sds_number)

    material_name = st.text_input(f"Enter Material Name for Material {i+1}", key=f"material_{i}")
    order_quantity = st.number_input(f"Enter Order Quantity (lbs) for {material_name}", min_value=0, key=f"qty_{i}")

    num_cas = st.number_input(f"How many CAS numbers for {material_name}?", min_value=2, step=1, key=f"cas_count_{i}")

    cas_data = []
    cas_numbers = set()
    total_percent = 0  # Tracks total CAS % ONLY

    for j in range(num_cas):
        cas_number = st.text_input(f"CAS # {j+1} for {material_name}", key=f"cas_{i}_{j}")

        if cas_number in cas_numbers:
            st.error(f"Duplicate CAS # {cas_number} is not allowed for {material_name}. Please enter a unique CAS #.")
        else:
            cas_numbers.add(cas_number)

        cas_percent = st.number_input(f"% CAS {cas_number} in {material_name}", min_value=0.0, max_value=100.0, key=f"percent_{i}_{j}")

        cas_data.append({"CAS Number": cas_number, "CAS %": cas_percent})
        total_percent += cas_percent  # Only sum CAS %, not order quantity

    # Validate CAS % sum
    if total_percent != 100:
        st.error(f"Total CAS % for {material_name} must sum to 100%. Currently: {total_percent}%")

    materials.append({"SDS #": sds_number, "Material": material_name, "Quantity": order_quantity, "CAS Data": cas_data})

# Calculate estimated CAS usage
if st.button("Calculate Usage"):
    for material in materials:
        st.subheader(f"Results for {material['Material']} (SDS # {material['SDS #']})")
        for cas in material["CAS Data"]:
            cas_usage = (material["Quantity"] * cas["CAS %"]) / 100
            st.write(f"CAS {cas['CAS Number']}: Estimated Usage = {cas_usage:.2f} lbs")

# File upload for CSV data
st.subheader("Upload Order Data (CSV)")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    csv_sds_numbers = set()

    for index, row in df.iterrows():
        sds_number = row["SDS #"]
        material_name = row["Material Name"]
        order_quantity = row["Order Quantity (lbs)"]

        if sds_number in csv_sds_numbers:
            st.error(f"Duplicate SDS # {sds_number} in CSV file. Each SDS # must be unique.")
            continue
        else:
            csv_sds_numbers.add(sds_number)

        cas_data = []
        total_percent = 0
        cas_numbers = set()

        for i in range(3, len(row) - 1, 2):  # Start from CAS #1, step by 2 (CAS % follows)
            cas_number = row[i]
            cas_percent = row[i + 1]

            if pd.notna(cas_number) and pd.notna(cas_percent):
                if cas_number in cas_numbers:
                    st.error(f"Duplicate CAS # {cas_number} in {material_name} (SDS {sds_number}). Please correct the CSV.")
                else:
                    cas_numbers.add(cas_number)
                    cas_usage = (order_quantity * cas_percent) / 100  # Calculate CAS usage in lbs
                    cas_data.append({"CAS Number": cas_number, "CAS %": cas_percent, "CAS Usage (lbs)": cas_usage})
                    total_percent += cas_percent

        if total_percent != 100:
            st.error(f"Total CAS % for {material_name} (SDS {sds_number}) must be 100%. Current total: {total_percent}%")

        # Display processed data
        st.subheader(f"Processed: {material_name} (SDS {sds_number}) - Quantity: {order_quantity} lbs")
        for cas in cas_data:
            st.write(f"CAS {cas['CAS Number']}: {cas['CAS Usage (lbs)']:.2f} lbs")




