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
             )
        self.problem_cases = {}

    def get_data(self,
                 prompt,
                 data) -> pd.DataFrame:
        """summarise input speech data 

        Args:
            prompt (langchain PromptTemplate): prompt to be passed to LLM

        Returns:
        """

        output = pd.DataFrame()
        chain = prompt | self.llm 
        response = chain.invoke({"prompt":prompt,
                                "data": data})
        return response


#%%


#---- prompt 
prompt = PromptTemplate(
    template = """
    \n\nHuman: You are a super helpful robot that does exactly as told. 
    Outline the purpose of this poll and briefly describe the data. 
    Include where the poll came from, the question number, and a description of the CSV file.
    Do not exceed more than 200 words.
    write the poll name, the table number, the question and a summary of the data
    {data}
    Do not repeat instructions back to me, just complete the task.
     \n\nAssistant:""",
    input_variables=["data"])


## --------------- set up CFG adn LLM 


base_dir = Path(os.getcwd()).parents[0]
data_dir = base_dir /'data'
example_data_path = data_dir / 'savanta_data'
poll_files = [x for x in os.listdir(example_data_path) if '.csv' in x]
#%%
handler = LLMHandler(env_path =base_dir/ '.env')
for file in poll_files[0:3]:
    data = pd.read_csv(example_data_path /file)
    response = handler.get_data(prompt=prompt,
                            data = data.to_string())