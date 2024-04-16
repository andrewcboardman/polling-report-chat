#%%
#general 
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



def parse_santava_excel(file):
    sheets_remaining = True
    sheet_index = 1
    dfs = []
    while sheets_remaining:
        try:
            df = pd.read_excel(file, sheet_name=sheet_index)
            dfs.append(df)
            sheet_index += 1
        except:
            sheets_remaining = False
    return dfs

def retrieve_questions(df):
    all_questions = []
    for list in df.values:
        questions = [x.split('Table')[1] for x in list if 'Table' in str(x)]
        all_questions = all_questions + questions
    return all_questions


class LLMHandler:
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
              model_kwargs = {
                      "temperature":0.5,
                      "top_k":50, #previously 250
                      "top_p":1
                      },
             )
        self.problem_cases = {}

    def get_data(self,
                 prompt,
                 file_name,
                 questions, data) -> pd.DataFrame:
        """summarise input speech data 

        Args:
            prompt (langchain PromptTemplate): prompt to be passed to LLM

        Returns:
        """

        output = pd.DataFrame()
        chain = prompt | self.llm 
        response = chain.invoke({"prompt":prompt,
                                 "file_name": file_name,
                                "data": data,
                                "questions":questions})
        return response


#%%
def convert_and_save(excel_path, output_path):
    prompt = PromptTemplate(
        template = """
        \n\nHuman: You are a super helpful robot that does exactly as told. 
        For this specific question in a poll, outline the purpose of the question
        and briefly describe the key findings of this question from the data. 
        Include the file name that the question came from, the question number, and the question text,
        Do not exceed more than 200 words.
        Here is the file name
        {file_name}
        Here is a list of all the questions in the poll
        {questions}
        Here is the data for this specific question
        {data}
        Do not repeat instructions back to me, or return anything else just complete the task.
        \n\nAssistant:""",
        input_variables=["file_name", "questions", "data"])


    ## --------------- set up CFG adn LLM 

    handler = LLMHandler(env_path =base_dir/ '.env')
    poll_questions_tables = parse_santava_excel(excel_path)
    cover_sheet = pd.read_excel(excel_path,sheet_name=0)
    questions = retrieve_questions(cover_sheet)
    t= 0 
    file_name = str(excel_path).split('/')[-1]
    for table in poll_questions_tables:
        response = handler.get_data(prompt=prompt,
                                    file_name = file_name,
                            data = table.to_csv(),
                            questions = str(questions))
        with open(output_path / f"{file_name}_question{t}.txt", "w") as file:
            file.write(response.dict()['content']) 
        t += 1
        print(file_name)
        print(response.dict()['content'])

#%%
# with open(f"{file}.txt", "w") as file:
#     file.write(response.dict()['content'])  

# data_path = data_dir/'savanta_data/Omni_W184_HomelessAndPolicePR_tables_Private.xlsx'
# sheets = parse_santava_excel(data_path)
# poll_data = ''
# for s in sheets:
#     poll_data = ''.join([poll_data, s.to_csv()])
# response = handler.get_data(prompt=prompt,
#                         data = poll_data)

#%%
    #%%


