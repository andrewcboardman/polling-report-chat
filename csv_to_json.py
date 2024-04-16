import pandas as pd

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

def get_json(file):
    end_row = file[file['<< Contents'].str.contains('Columns tested', case=False, na=False)].index[0]
    new_df = file.iloc[4:end_row]
    to_exclude = ['Unnamed: 0','<< Contents','Unnamed: 2']
    file_curated = new_df[[col for col in new_df.columns if col not in to_exclude]]
    file_curated = file_curated.apply(fill_with_preceding, axis=1)
    file_curated.columns = pd.MultiIndex.from_arrays([file_curated.iloc[0], file_curated.iloc[1]])
    file_curated.columns = [f'{i}_{j}' for i,j in file_curated.columns]
    file_curated.reset_index(drop=True, inplace=True)
    file_curated.drop([0,1], inplace=True)
    return file_curated.to_json(orient='records')

def compile_json(file):
    json_file = get_subject_and_question_into_json(file)
    json_file['data'] = get_json(file)
    return json_file