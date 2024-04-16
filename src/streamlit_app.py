import streamlit as st
import pandas as pd
from parse_excel import parse_santava_excel
from csv_to_json import compile_json

dfs = []

def rag_search(topic):
    return pd.DataFrame(dict(
        question = ['Not implemented yet'],
        group = ['Not implemented yet'],
        result = ['Not implemented yet'],
    ))

def run_query(question, csv):
    return 'Not implemented yet'

def import_data_tab():
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
                st.session_state['csv_strings'].append(df.to_csv(index=False))
        
        st.session_state['summaries'] = []
        for csv_string in st.session_state['csv_strings']:
            st.session_state['summaries'].append(compile_json(df))

        st.write(f"{len(st.session_state['csv_strings'])} questions were successfully summarised.")


def rag_search_tab():
    search_topic = st.text_input(
                'Enter a topic to identify relevant polling data.'
                )
    search = st.button('Search')
    if search:
        # Placeholder for search functionality
        results = rag_search(search_topic)
        st.dataframe(results)
        st.session_state['previous_results'].append(results)
        st.session_state['previous_searches'].append(
            {
                'Search topic': search_topic,
                'Number of polls searched': len(st.session_state['summaries']),
                'Number of results': len(results)
            }
        )

def poll_query_tab():
    st.selectbox(st.session_state['csv_strings'][0])
    select('Select a poll to query')
    st.text_input('Enter query text')
    if st.button('Run query'):
        run_query(csv, query_text)


def main():
    st.title('Chat with polling data')
    if 'previous_searches' not in st.session_state.keys():
        st.session_state['previous_searches'] = []
    if 'previous_results' not in st.session_state.keys():
        st.session_state['previous_results'] = []
    tabs = [
        'Upload polling data', 
        'Browse poll summaries',
        'Semantic poll summary search',
        'Search history',
        'Query poll data'
    ]
    tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs)

    with tab1:
        import_data_tab()
    with tab2:
        if len(st.session_state['summaries']) > 0:
            st.dataframe(st.session_state['summaries'])
        else:
            st.write('No poll summaries have been uploaded yet.')
    with tab3:
        rag_search_tab()
    with tab4:
        if len(st.session_state['previous_searches']) > 0:
            st.dataframe(st.session_state['previous_searches'])
        else:
            st.write('No searches have been made yet.')
    with tab5:
        poll_query_tab()




if __name__ == '__main__':
    main()



# if uploaded_file is not None:
#     if uploaded_file.type.isin(["xls","xlsx"]):
#         dfs = parse_santava_excel(uploaded_file)
#     elif uploaded_file.type.isin(["csv"]):
#         dfs = parse_santava_csv(uploaded_file)

    
