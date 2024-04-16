# %%
import pandas as pd
import glob

# %%

def parse_santava_excel(file):

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
    i = 0
    for file in glob.glob('./data/savanta_data/*.xlsx'):
        dfs = parse_santava_excel(file)
        for j, df in enumerate(dfs):
            df.to_csv(f'./data/savanta_data/polling_{i}_{j}.csv', index=False)

if __name__ == '__main__':
    main()

    
