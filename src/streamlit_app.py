import streamlit as st
import pandas as pd
import os
from pathlib import Path
from parse_excel import parse_santava_excel
from llm_convert_to_text import convert_and_save
from query_rag import run_rag_final

def V_SPACE(lines):
    """
    This function creates vertical space in the streamlit app.
    Args:
        lines (int): The number of lines to create.
    """
    for _ in range(lines):
        st.write("&nbsp;")

def rag_search(topic):
    """
    This function searches the RAG model for relevant polling data according to a given topic.
    Args:
        topic (str): The topic to search for.
    Returns:
        results (list): A list of relevant polling data.
    """
    return "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna"

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
        
        # Summarise the data using calls to Amazon Bedrock
        for uploaded_file in uploaded_files:
            output_path = Path(os.getcwd()) / 'data/rag_txt'
            print(uploaded_files, output_path)
            summary_filenames = convert_and_save(
                uploaded_file, 
                uploaded_file.name,
                output_path)
            st.session_state['summaries'][uploaded_file.name] = summary_filenames

        st.write(f"Data successfully processed!")

def rag_search_tab():
    """
    This function creates the RAG search tab in the streamlit app.
    """
    search_topic = st.text_input(
                'Enter a topic to identify relevant polling data.'
                )
    search = st.button('Search')
    if search:
        # Placeholder for search functionality
        results = run_rag_final(search_topic)
        st.write(results)
        st.session_state['previous_results'].append(results)
        st.session_state['previous_searches'].append(
            {
                'Search topic': search_topic,
                'Number of polls searched': len(st.session_state['summaries']),
            }
        )


def poll_query_tab():
    """
    This function creates the poll query tab in the streamlit app.
    """
    st.selectbox('Select a poll to query', options = st.session_state['csv_strings'].keys())
    st.text_input('Enter query text')
    if st.button('Run query'):
        run_query()


def main():
    """
    This function creates the main streamlit app.
    """
    st.title('PollDancer')
    st.subheader('Graceful shortcut to finding polling answers across government')
    with st.sidebar:
        st.image(
        './images/logo_inverted.png',
        )
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


    
