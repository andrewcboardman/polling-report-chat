from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain import hub
from langchain.llms import (
    HuggingFaceHub,
)
from langchain.embeddings import HuggingFaceEmbeddings 
import chromadb
from langchain.prompts import PromptTemplate
import os

folder_path = "../data/text_summaries/"

# List all files and directories in the specified folder
files_and_directories = os.listdir(folder_path)

# Filter out only the file paths
file_paths = [os.path.join(folder_path, file) for file in files_and_directories if os.path.isfile(os.path.join(folder_path, file))]

# Print the file paths
for file_path in file_paths:
    print(file_path)

file_path

# Load the document, split it into chunks, embed each chunk and load it into the vector store.
file_paths

for doc in file_paths:
    raw_documents = TextLoader(doc).load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(raw_documents)
    print(documents)

vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    ),
    # persist_directory="./chromadb",
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 1})

#fine tuned team used this prompt
prompt_template = """Given a query, return the a summary of the most similar descriptions on the polling descriptions contained in the contect provided.
 
### query: {query}

 
### Context: {context}

 
### Summary:
"""

prompt = PromptTemplate.from_template(
    prompt_template
)
prompt

from operator import itemgetter
from langchain_core.runnables import RunnableParallel, RunnableLambda

chain = (
        {
        "context": itemgetter("query") 
            | retriever, 
            #| RunnableLambda(format_docs),
        "query": itemgetter("query"),
    }
    | prompt
   # | ft_llm
   # | StrOutputParser()
)
chain

q = "What do young men feel about websites"
print(chain.invoke({"query": q}))
prompt = chain.invoke({"query": q}).to_string()

print(prompt)

