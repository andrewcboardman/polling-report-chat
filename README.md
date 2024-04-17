# polling-report-chat
## PollDancer
### A tool for searching through polling data to find relevant poll questions
* `src/parse_excel.py` loops through the excel workbooks provided and writes each worksheet to a separate CSV file.
* `src/llm_convert_to_text.py` loops through the CSV files and writes summaries for each as text files.
* `src/query_rag.py` takes in a query, uses RAG to find relevant poll questions and outputs summaries of each.
* `src/streamlit_app.py` runs the Streamlit app, which allows users to import polling data and search for polling questions.
to run streamlit run `src/streamlit_app.py`
## Requirements
See `requirements.txt` for the required Python packages.
Users also need an Amazon .env file.
## Demo App
[![Streamlit App](
https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://app-starter-kit.streamlit.app/
)
## GitHub Codespaces
[![Open in GitHub Codespaces](
https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/app-starter-kit?quickstart=1
)
