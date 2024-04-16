import streamlit as st
import pandas as pd
from parse_excel import parse_santava_excel
from csv_to_json import compile_json

dfs = []


def import_data():
    st.write('Please upload a csv or excel file containing a Santava polling data table.')
    uploaded_files = st.file_uploader(
        "Choose a file",
        type=["csv", "xls", "xlsx"],
        accept_multiple_files=True,
        )

    file_format = st.selectbox(
        'File format',
        ("csv", "xls", "xlsx"),
    )

    if st.button('Process incoming file(s)'):
        st.session_state['dfs'] = []
        for uploaded_file in uploaded_files:
            dfs_ = parse_santava_excel(uploaded_file)
            for df in dfs_:
                st.session_state['dfs'].append(df)
        
        st.session_state['jsons'] = []
        for df in st.session_state['dfs']:
            st.session_state['jsons'].append(compile_json(df))

        st.write(f"{len(st.session_state['dfs'])} questions were successfully processed.")


def debug():
    
    st.dataframe(pd.concat(st.session_state['dfs']).head())

    st.write(st.session_state['jsons'][0])

def main():
    st.title('Chat with polling data')
    import_data()
    if st.button('Debug'):
        if len(st.session_state['dfs']) > 0:
            debug()
        else:
            st.write('Please process input data before debugging.')


if __name__ == '__main__':
    main()



# if uploaded_file is not None:
#     if uploaded_file.type.isin(["xls","xlsx"]):
#         dfs = parse_santava_excel(uploaded_file)
#     elif uploaded_file.type.isin(["csv"]):
#         dfs = parse_santava_csv(uploaded_file)

    
