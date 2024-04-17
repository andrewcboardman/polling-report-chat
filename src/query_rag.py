#%%
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
import os
#porject specfic
import boto3
from dotenv import load_dotenv, find_dotenv
from langchain.llms.bedrock import Bedrock
import pandas as pd
#local
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import BedrockChat
# from langchain_anthropic import ChatAnthropic
from pathlib import Path
from langchain import hub
from langchain.llms import (
    HuggingFaceHub,
)
from langchain.embeddings import HuggingFaceEmbeddings 
import chromadb
import os
from langchain.prompts import PromptTemplate
from operator import itemgetter
from langchain_core.runnables import RunnableParallel, RunnableLambda

class LLMHandler_rag:
    """LLM handler class - set up client
    """
    def __init__(self, env_path):
        load_dotenv(env_path)
        boto3.setup_default_session(aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
                           aws_session_token = os.getenv('AWS_SESSION_TOKEN'))
        client = boto3.client(service_name='bedrock-runtime',
                       region_name=os.getenv('AWS_DEFAULT_REGION'))
        self.llm = BedrockChat(model_id = "anthropic.claude-3-sonnet-20240229-v1:0",
              client = client,
              model_kwargs = {'temperature':0.5,
                              'top_k':50,
                              'top_p':1
                              } 
             )
        self.problem_cases = {}
    def get_response(self,
                     prompt,
                     rag_prompt):
        """summarise input speech data
        Args:
            prompt (langchain PromptTemplate): prompt to be passed to LLM
        Returns:
        """
        chain = prompt | self.llm
        response = chain.invoke({"prompt":prompt,"rag":rag_prompt})
        return response

def run_rag_final(query):

    folder_path = "data/rag_txt/"

    # List all files and directories in the specified folder
    files_and_directories = os.listdir(folder_path)

    # Filter out only the file paths
    file_paths = [os.path.join(folder_path, file) for file in files_and_directories if os.path.isfile(os.path.join(folder_path, file))]
    # Load the document, split it into chunks, embed each chunk and load it into the vector store.
    doc_list = []
    for doc in file_paths:
        raw_documents = TextLoader(doc).load()
        #text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=20)
        #documents = text_splitter.split_documents(raw_documents)
        doc_list.append(raw_documents[0])

    vectorstore = Chroma.from_documents(
        documents=doc_list,
        embedding=HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        ),
       # persist_directory="./chromadb_3",
    )

    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

    #fine tuned team used this prompt
    prompt_template = """
    ### query: {query}

    ### Context: {context}
    """
    prompt = PromptTemplate.from_template(
        prompt_template
    )
    
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

    query = query
    rag_prompt = chain.invoke({"query": query}).to_string()


    final_prompt_template = PromptTemplate(
        # template = """
        # \n\nHuman: You are a super helpful robot that does exactly as told.
        # Outline the purpose of this poll and briefly describe the data.
        # Include where the poll came from, the question number, and a description of the CSV file.
        # Do not exceed more than 200 words.
        # write the poll name, the table number, the question and a summary of the data
        # {data}
        # Do not repeat instructions back to me, just complete the task.
        #  \n\nAssistant:""",
        template = """
        \n\nHuman: You are a helpful administrative assistant.
    Using only the context provided, detail which questions from polls are relevant to this query. If the context is not relevent return 'There is no information in the database'.
    For each question, return the file name, question and question text. Give a short summary of the findings.
    Here is the query and context:
    {rag}
    Do not use any information not in the context. do not return any information about irrelevent files.
    \n\nAssistant:""",
        input_variables=["rag"])
     
    
    base_dir = Path(os.getcwd())
    handler = LLMHandler_rag(env_path =base_dir/ '.env')
    response = handler.get_response(prompt = final_prompt_template, rag_prompt = rag_prompt)
    
    return response.dict()['content']



#run_rag_final(query = "what do people think about crime")





