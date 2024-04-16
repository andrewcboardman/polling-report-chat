import streamlit as st
import pandas as pd
import os
from pathlib import Path
from parse_excel import parse_santava_excel
from llm_handler import LLMHandler, prompt


def V_SPACE(lines): 
    for _ in range(lines):
        st.write("&nbsp;")

def rag_search(topic):
    return "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna"

def run_query():
    return 'Not implemented yet'

def import_data_tab():
    st.write('Please upload a csv or excel file containing a Santava polling data table.')
    uploaded_files = st.file_uploader(
        "Choose a file",
        type=["csv", "xls", "xlsx"],
        accept_multiple_files=True,
        )
    for uploaded_file in uploaded_files:
        st.session_state['filenames'] = uploaded_file.name

    if 'csv_strings' not in st.session_state:
        st.session_state['csv_strings'] = {}
    if 'summaries' not in st.session_state:
        st.session_state['summaries'] = {}

    if st.button('Process incoming file(s)'):
        # Parse the uploaded files
        for uploaded_file in uploaded_files:
            dfs_ = parse_santava_excel(uploaded_file)
            for df in dfs_:
                st.session_state['csv_strings'][uploaded_file.name] = df.to_csv(index=False)
        
        # Summarise the data using calls to Amazon Bedrock
        for filename, df in st.session_state['csv_strings'].items():
            st.session_state['summaries'][filename] = 'Lorem ipsum'

        st.write(f"{len(st.session_state['csv_strings'])} questions were successfully summarised.")
    
    if len(st.session_state['summaries']) > 0:
        st.dataframe(st.session_state['summaries'])
    else:
        st.write('No poll summaries have been uploaded yet.')

def rag_search_tab():
    search_topic = st.text_input(
                'Enter a topic to identify relevant polling data.'
                )
    search = st.button('Search')
    if search:
        # Placeholder for search functionality
        results = rag_search(search_topic)
        st.write(results)
        st.session_state['previous_results'].append(results)
        st.session_state['previous_searches'].append(
            {
                'Search topic': search_topic,
                'Number of polls searched': len(st.session_state['summaries']),
                'Number of results': len(results)
            }
        )
        
        if len(st.session_state['previous_searches']) > 0:
            st.dataframe(st.session_state['previous_searches'])
        else:
            st.write('No searches have been made yet.')


def poll_query_tab():
    st.selectbox('Select a poll to query', options = st.session_state['csv_strings'].keys())
    st.text_input('Enter query text')
    if st.button('Run query'):
        run_query()


def main():
    st.title('PollDancer')
    st.image('./images/DALL·E 2024-04-16 17.40.19 - A logo design inverted.png')
    st.subheader('Graceful shortcut to finding polling answers across government')
    if 'previous_searches' not in st.session_state.keys():
        st.session_state['previous_searches'] = []
    if 'previous_results' not in st.session_state.keys():
        st.session_state['previous_results'] = []

    st.header('Upload polling data')
    import_data_tab()
    

    V_SPACE(2)

    st.header('Query polling data')
    rag_search_tab()


if __name__ == '__main__':
    main()



# if uploaded_file is not None:
#     if uploaded_file.type.isin(["xls","xlsx"]):
#         dfs = parse_santava_excel(uploaded_file)
#     elif uploaded_file.type.isin(["csv"]):
#         dfs = parse_santava_csv(uploaded_file)

    
