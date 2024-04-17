# %%
import pandas as pd
import glob

# %%

def parse_santava_excel(file):
    """
    This function reads an excel file and returns a list of pandas dataframes, one for each sheet in the excel file.

    Args:
        file (str): The path to the excel file to be read.
    Returns:
        dfs (list): A list of pandas dataframes, one for each sheet in the excel file.
    """
    sheets_remaining = True
    sheet_index = 1
    dfs = []
    while sheets_remaining:
        try:
            print(f'Reading sheet {sheet_index} for {file}...')
            df = pd.read_excel(file, sheet_name=sheet_index)
            dfs.append(df)
            sheet_index += 1
        except:
            sheets_remaining = False
            return dfs

def main():
    """
    This function reads all excel files in the data/savanta_data directory and writes the data to csv files in the same directory.
    The function reads each sheet in the excel file and writes the data to a separate csv file.
    The csv files are named according to the excel file and sheet index.
    """
    i = 0
    for file in glob.glob('./data/savanta_data/*.xlsx'):

        dfs = parse_santava_excel(file)
        for j, df in enumerate(dfs):
            df.to_csv(f'./data/savanta_data/polling_{i}_{j}.csv', index=False)
        i+=1

if __name__ == '__main__':
    main()

    
