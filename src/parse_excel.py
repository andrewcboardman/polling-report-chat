# %%
import pandas as pd
import glob

# %%
i = 0

for file in glob.glob('../data/savanta_data/*.xlsx'):
    sheets_remaining = True
    sheet_index = 1
    while sheets_remaining:
        try:
            print(f'Reading sheet {sheet_index} for {file}...')
            df = pd.read_excel(file, sheet_name=sheet_index)
            df.to_csv(f'../data/savanta_data/polling_data{i}.csv', index=False)
            sheet_index += 1
            i += 1
        except:
            sheets_remaining = False

# %%
df.drop('Unnamed: 0', axis=1, inplace=True)

# %%
file

# %%
dfs


