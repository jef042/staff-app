import streamlit as st
import pandas as pd
import re

st.title("Clinician Assignment Summary")

uploaded_file = st.file_uploader("Upload Monthly Schedule Export", type=["xlsx"])

def is_valid_assignment(assignment):
    if isinstance(assignment, str):
        if re.search(r'\b(?:OR|AC|SCCA|VAC|Call|OnDeck|NORA|TX|RAD|FETAL|PAIN|SDU|CNSLT|F/U)\b', assignment):
            return True
        if re.search(r'\d{2}:\d{2}', assignment):  # time indicator
            return True
        if assignment.strip() in {"VAC", "LOA", "CON", "OR", "AC", "PC", "LATE", "NoCall"}:
            return True
    return False

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    df_data = xls.parse(xls.sheet_names[0], skiprows=6)
    df_data.iloc[:, 0] = df_data.iloc[:, 0].ffill()
    df_data = df_data.rename(columns={df_data.columns[0]: "Clinician"})

    melted_df = df_data.melt(id_vars=["Clinician"], var_name="Day", value_name="Assignment")
    melted_df = melted_df.dropna(subset=["Assignment"])
    melted_df = melted_df[melted_df["Assignment"].astype(str).str.strip() != ""]

    filtered_df = melted_df[melted_df["Assignment"].apply(is_valid_assignment)]

    cleaned_counts = filtered_df.groupby(["Clinician", "Assignment"]).size().reset_index(name="Count")
    summary = cleaned_counts.pivot(index="Clinician", columns="Assignment", values="Count").fillna(0).astype(int)

    st.subheader("Assignment Counts by Clinician")
    st.dataframe(summary)

    csv = summary.reset_index().to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Summary as CSV",
        data=csv,
        file_name='clinician_assignment_summary.csv',
        mime='text/csv',
    )
