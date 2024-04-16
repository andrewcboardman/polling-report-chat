import streamlit as st
import pandas as pd


st.title('Chat with polling data')

st.write('Please upload a csv or excel file containing a Santava polling data table.')

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "xls", "xlsx"],
    accept_multiple_files=True,
    )

# if uploaded_file is not None:
#     if uploaded_file.type.isin(["xls","xlsx"]):
#         dfs = parse_santava_excel(uploaded_file)
#     elif uploaded_file.type.isin(["csv"]):
#         dfs = parse_santava_csv(uploaded_file)

    
