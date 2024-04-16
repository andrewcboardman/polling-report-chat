import pandas as pd
import glob
import json
from pathlib import Path

### FUNCTIONS ###
def get_subject_and_question_into_json(file):
    subject = file['<< Contents'][0]
    question = file['<< Contents'][2]
    json_file = {}
    json_file['subject'] = subject
    json_file['question'] = question
    return json_file

def fill_with_preceding(row):
    for i in range(1, len(row)):
        if pd.isna(row[i]):
            row[i] = row[i-1]
    return row

def fill_fields(file):
    for i in range(1, len(file)):
        if '%' in file['Field_Type'].iloc[i-1] and pd.isna(file['Field_Type'].iloc[i]):
            file['Field_Type'].iloc[i] = 'Significance test for answer '+file['Field_Type'].iloc[i-2]
        elif pd.isna(file['Field_Type'].iloc[i]):
            file['Field_Type'].iloc[i] = file['Field_Type'].iloc[i-1] + ' ' + 'in %'
        
    return file

def get_json(file):
    end_row = file[file['<< Contents'].str.contains('Columns tested', case=False, na=False)].index[0]
    new_df = file.iloc[4:end_row]
    to_exclude = ['Unnamed: 0','Unnamed: 2']
    file_curated = new_df[[col for col in new_df.columns if col not in to_exclude]]
    file_curated = file_curated.rename(columns={'<< Contents': 'Field description'})
    file_curated = file_curated.apply(fill_with_preceding, axis=1)
    file_curated['Field description'].iloc[0] = 'Field'
    file_curated['Field description'].iloc[1] = 'Type'
    file_curated.columns = pd.MultiIndex.from_arrays([file_curated.iloc[0], file_curated.iloc[1]])
    file_curated.columns = [f'{i}_{j}' for i,j in file_curated.columns]
    file_curated.reset_index(drop=True, inplace=True)
    file_curated.drop([0,1], inplace=True)
    file_curated = fill_fields(file_curated)
    return file_curated.to_json(orient='records')

def compile_json(file):
    json_file = get_subject_and_question_into_json(file)
    print(type(json_file))
    json_file['data'] = json.loads(get_json(file))
    return json_file

def main():
    input_file = '../data/savanta_data/polling_data61.csv'
    output_file = '../data/test_0.json'
    output = compile_json(pd.read_csv(input_file))
    with open(output_file, 'w') as outfile:
        json.dump(output, outfile, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()