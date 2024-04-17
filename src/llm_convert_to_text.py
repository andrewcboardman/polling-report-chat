# %%
""" Module to convert poll excel files to per question .txt file summaries"""
# general
import os
from pathlib import Path

# project specfic
import boto3
from dotenv import load_dotenv, find_dotenv
from langchain.llms.bedrock import Bedrock
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import BedrockChat


def parse_santava_excel(file):
    """helper function to parse excel file in list of dfs

    one df for each sheet in xlsx (excepting first sheet)"""
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
    """func to retrieve list of all quesitons in a poll from the first
    sheet of excel"""
    all_questions = []
    for list in df.values:
        questions = [x.split("Table")[1] for x in list if "Table" in str(x)]
        all_questions = all_questions + questions
    return all_questions


class LLMHandler:
    """LLM handler class - set up client"""

    def __init__(self, env_path: Path):
        """

        Args:
            env_path (Path): path to .env with aws creds
        """
        load_dotenv(env_path)
        boto3.setup_default_session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        )
        client = boto3.client(
            service_name="bedrock-runtime", region_name=os.getenv("AWS_DEFAULT_REGION")
        )

        self.llm = BedrockChat(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            client=client,
            model_kwargs={
                "temperature": 0.5,
                "top_k": 50,  # previously 250
                "top_p": 1,
            },
        )

    def get_data(
        self, prompt: PromptTemplate, file_name: str, questions: str, data: str
    ):
        """get summary of poll question data

        Args:
            prompt (PromptTemplate): langchain prompt template
            file_name (str): name of file poll questions taken from
            questions (str): list of other questions in the poll
            data (str): poll table as csv
        """

        output = pd.DataFrame()
        chain = prompt | self.llm
        response = chain.invoke(
            {
                "prompt": prompt,
                "file_name": file_name,
                "data": data,
                "questions": questions,
            }
        )
        return response


# %%
def convert_and_save(excel_path: Path, file_name: str, output_path: Path):
    """
    convert a poll xlsx into .txt file per question summaries


    Args:
        excel_path (Path): path to poll excel file
        file_name (str): name of file poll questions taken from
        output_path (Path): path to svae .txt in

    """
    prompt = PromptTemplate(
        template="""
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
        input_variables=["file_name", "questions", "data"],
    )

    ## --------------- set up CFG and LLM
    base_dir = Path(os.getcwd())
    handler = LLMHandler(env_path=base_dir / ".env")
    poll_questions_tables = parse_santava_excel(excel_path)  # get question dats as dfs
    cover_sheet = pd.read_excel(excel_path, sheet_name=0)
    questions = retrieve_questions(cover_sheet)  # get list of questions
    t = 0
    file_name = file_name
    output_filenames = []

    for table in poll_questions_tables:
        response = handler.get_data(
            prompt=prompt,
            file_name=file_name,
            data=table.to_csv(),
            questions=str(questions),
        )
        output_filename = output_path / f"{file_name}_question{t}.txt"
        output_filenames.append(output_filename)
        with open(output_filename, "w") as file:
            file.write(response.dict()["content"])
        t += 1
    return output_filenames
