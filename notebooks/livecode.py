"""
Hey Z! Try to run the following blocks
to see if it works
"""
# %%

(get_ipython()
 .run_line_magic('load_ext', 'autotime'))

import pandas as pd
# %%

DATA_PATH = '../data/query_result_2020-10-12T20_42_24.031Z.csv'

data = pd.read_csv(DATA_PATH)
# %%
data.head(5)
# %%
data.dtypes
#  %%
import json 

json_data = (data.normalized_data
                 .map(json.loads))
# %%
json_df = pd.DataFrame(json_data.tolist())
# %%
data.join(json_df)
# %%
