#imports 
#%%
#general
import os
import pathlib 
import json
#project specifc 
import pandas as pd
from langchain.prompts import PromptTemplate
#local
from llm_handler import HandlerCFG, LLMHandler
from parsers.output_parsers import simplified_intel_parser, simplified_filt_intel_parser
from helper_functions.helper_functions import get_quote_edit_distance, get_mp_segments, join_strings, write_to_excel
#%%
#-------------load data

#---- prompt 
prompt = PromptTemplate(
    template = """
    \n\nHuman: As an experienced data analyst for a political organization your task is to analyze a speech and produce strategic summaries. 
    ### Context You have been provided speech data and format guidelines to structure your analysis. 
    ### Instructions from the speech data: 
    1. Write a concise sentence summary 
    2. Provide a relevant one to two sentence quotation 
    3. Indicate whether the speech is relevant to healthcare or social care issues by labeling it as 'True' if so, or 'False' if not. 
    4. Apply any suitable tags from the list of approved topic tags if the speech content matches the tag description. If none of the tags apply or you are unsure, use "Other".  
    
    Organize your responses according to the format instructions.
    Make sure the quotation you return is at least one complete sentence long .
    Ensure you only use tags present in the list of approved topic tags. 
    do you understand these instructions?
    \n\nAssistant:  Yes, I understand the instructions. As an analyst, my task is to analyze speech data and provide strategic summaries following the specified format guidelines.
    \n\nnHuman:  Here are the speech details
    ### Speech Data 
    \n{speech_table}
    ### Format instructions
    \n{format_instructions}
    ### List of approved tags with topic descriptions  
    {topic_tags}
    Do not repeat instructions back to me, just complete the task and return a response compatible  with the format instructions and nothing else.
     \n\nAssistant:""",
    input_variables=["topic_tags","speech_table"],
    partial_variables={"format_instructions": simplified_filt_intel_parser.get_format_instructions()},
    output_parser=simplified_filt_intel_parser)


## --------------- set up CFG adn LLM 

def main(
    speech_data_path,
    outputs_path,
    max_tokens_to_sample,
    temperature,
    top_k=50,
    top_p=1
):
    inference_modifier = {
        'max_tokens_to_sample':max_tokens_to_sample,
        "temperature":temperature,
        "top_k":top_k, #previously 250
        "top_p":top_p
        }

CFG = HandlerCFG(inference_modifier)
handler = LLMHandler(CFG, #configuration settings
                     output_parser = simplified_filt_intel_parser) 
#%%
# sort batches 
if os.path.exists(os.path.join(outputs_path,'processed_speech_data.csv')):
    output = pd.read_csv(os.path.join(outputs_path,'processed_speech_data.csv'))
    raw_speech =  pd.read_csv(os.path.join(outputs_path,'raw_speech_data_comparison.csv'))
    with open(os.path.join(outputs_path,'processed_mps'), "r", encoding = 'utf8') as f:
        processed_mps = json.load(f)
else:
    output = pd.DataFrame()
    raw_speech = pd.DataFrame()
    processed_mps = []

if os.path.exists(os.path.join(outputs_path,'over_limit_debates')):
    with open(os.path.join(outputs_path,'over_limit_debates'),"r", encoding = 'utf8') as f:
        over_limit_debates = json.load(f)
else:
    over_limit_debates = []


unprocessed_speech_data = speech_data.query('Member not in @processed_mps')
unprocessed_speech_data.loc[:,'debate_id'] = [' '.join([unprocessed_speech_data.Date.iloc[x], 
                                                        unprocessed_speech_data.Debate.iloc[x]]) for x in range(0, len(unprocessed_speech_data))]

APPROX_N_SEGMENTS = 1000
data_segments = get_mp_segments(unprocessed_speech_data, APPROX_N_SEGMENTS)
c = 0 
for segment in data_segments[0:1]:   #SMALL HERE
    print(f'-------- processing segment {c} --------')
    segment_summaries = pd.DataFrame()
    segment_raw = pd.DataFrame() # also saving raw data for comp
    #get summaries
    for mp in segment:
        mp_df = speech_data.query('Member == @mp')
        debates = mp_df.debate_id.unique()
        by_debate_df = mp_df.groupby('debate_id').agg({'Speech Content': join_strings}).reset_index()
        mp_over_limit_debates =[d for d in debates if handler.llm.get_num_tokens(by_debate_df.query('debate_id == @d')['Speech Content'].iloc[0]) > 95000]
        valid_debates = [d for d in debates if d not in mp_over_limit_debates]
        mp_over_limit_debates = [' '.join([mp,d]) for d in mp_over_limit_debates]
        results_df = handler.get_speech_intel(prompt = prompt,
                                topic_tags = topic_tags,
                                speech_data =mp_df,
                                debates = valid_debates)
        segment_summaries = pd.concat([segment_summaries, results_df])
        #also saving raw speech for comparison 
        mp_debate_content_df = by_debate_df.query('debate_id in @debates')
        mp_debate_content_df.loc[:,'mp'] = mp
        segment_raw = pd.concat([segment_raw, mp_debate_content_df])
        over_limit_debates = over_limit_debates + mp_over_limit_debates
    #validat 
    cols = ['date', 'debate', 'mp', 'summary', 'quotation', 'topic_tags','relevance']
    segment_summaries = segment_summaries[cols]
    print('------------------ VALIDATING -----------------------')
    segment_summaries.loc[:,'id_col'] = [' '.join([segment_summaries.iloc[x].mp,
                                               segment_summaries.iloc[x].debate]) for x in range(0,len(segment_summaries.index))]
    segment_raw.loc[:,'id_col'] = [' '.join([segment_raw.iloc[x].mp, 
                                                segment_raw.iloc[x].Debate]) for x in range(0,len(segment_raw.index))]

    segment_summaries.loc[:,'AI_generated_topic_tags'] = segment_summaries.topic_tags.apply(lambda x:[tag for tag in x if tag not in list(topic_tags.Tag)])
    segment_summaries.loc[:,'quote_edit_distance'] = get_quote_edit_distance(segment_raw, segment_summaries)

    #save 
    output = pd.concat([output, segment_summaries])
    raw_speech = pd.concat([raw_speech, segment_raw])
    output.to_csv(os.path.join(outputs_path,'processed_speech_data.csv'))
    raw_speech.to_csv(os.path.join(outputs_path,'raw_speech_data_comparison.csv'))
    processed_mps = processed_mps + segment
    c += 1
    with open(os.path.join(outputs_path,'processed_mps'), 'w', encoding = 'utf8') as f:
        json.dump(processed_mps, f)
    with open(os.path.join(outputs_path,'over_limit_debates'), 'w', encoding = 'utf8') as f:
        json.dump(over_limit_debates, f)


write_to_excel(outputs_path, 'LLM_summaries_one_year', output)