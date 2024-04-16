#general 
import os
#porject specfic
import boto3
from dotenv import load_dotenv
from langchain.llms.bedrock import Bedrock
import pandas as pd
#local
from parsers.input_parsers import InputTopicTags, InputSimplified

class HandlerCFG:
    """Configuration class - currenly only holds inference modifier kwargs"""
    def __init__(self,
                 inference_modifier
                 ):
        self.inference_modifier = inference_modifier


class LLMHandler:
    """LLM handler class - set up client 
    """
    def __init__(self,
                 CFG,
                 output_parser):
        
        load_dotenv()
        boto3.setup_default_session(aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
                           )
        client = boto3.client(service_name='bedrock-runtime', 
                       region_name=os.getenv('BWB_REGION_NAME'))
        self.llm = Bedrock(model_id = "anthropic.claude-instant-v1",
              client = client,
              model_kwargs = CFG.inference_modifier
             )
        self.CFG = CFG
        self.output_parser = output_parser
        self.problem_cases = {}

    def get_speech_intel(self,
                         prompt,
                         topic_tags ,
                         speech_data,
                         debates) -> pd.DataFrame:
        """summarise input speech data 

        Args:
            prompt (langchain PromptTemplate): prompt to be passed to LLM
            topic_tags (df): topic tags and associated descriptions
            speech_data (df): speech date from a single MP
            debates (_type_): list of debates to extract data from 

        Returns:
            output (df): datafrane with the following columns (date, debate, mp, sumarry, quote, topic_tags)
        """
        
        topic_tags_dict = {k:v for (k,v) in zip(topic_tags.Tag,topic_tags.Topic) }
        topic_tags_input = InputTopicTags(input_data= topic_tags_dict)
        # topic_tags_list = list(topic_tags.Tag.values)
        # topic_tags_input = InputTopicTagsList(input_data= topic_tags_list)

        output = pd.DataFrame()
        chain = prompt | self.llm | self.output_parser 

        for debate in debates:
            debate_df = speech_data.query('debate_id == @debate')
            print(f'Working on {debate_df.iloc[0]['Member']} : {debate}')
            # input_debate = InputDataSingleDebate(date = debate_df.iloc[0]['Date'],
            #                           debate = debate_df.iloc[0]['Debate'],
            #                           debate_location = debate_df.iloc[0]['Debate Location'],
            #                           member = debate_df.iloc[0]['Member'],
            #                           speech_content = debate_df['Speech Content'].to_string(index =False))   #send as string
            
            input_debate = InputSimplified(speech = debate_df['Speech Content'].str.cat(sep=' '))
            try:
                response = chain.invoke({"topic_tags":topic_tags_input,
                                        "speech_table": input_debate})
                response_dict = dict(response)
                response_dict['topic_tags'] = [response_dict['topic_tags']]
                #for simplified version
                response_dict['date'] =  debate_df.iloc[0]['Date']
                response_dict['debate'] =  debate_df.iloc[0]['Debate']
                response_dict['mp'] = debate_df.iloc[0]['Member']
                response_df = pd.DataFrame(response_dict, index=[0])
                output = pd.concat([output,response_df])
            except ValueError as e:
                self.problem_cases[' '.join([debate_df.iloc[0]['Member'],
                                             debate_df.iloc[0]['Date'], 
                                             debate_df.iloc[0]['Debate']])] = e
                continue
        return output





