# %% [markdown]
# # Community funding PoC
# ## Dependences and parameters

# %%
import seaborn as sns
from typing import List, Dict, NewType
import plotly.express as px
import matplotlib.pyplot as plt
import networkx as nx
import json
import pandas as pd
import pytest

from typing import List
(get_ipython().run_line_magic("load_ext", "autotime"))

# %%

# %% [markdown]
# ## Prepare graph

# %%

DATA_PATH = "../data/query_result_2020-10-12T20_42_24.031Z.csv"

raw_df = pd.read_csv(DATA_PATH)

# Parse the normalized data strings into dictionaries
json_data = raw_df.normalized_data.map(json.loads)

# Create a data frame from the normalized data parsed series
col_map = {
    "id": "json_id",
    "created_on": "json_created_on",
    "tx_id": "json_tx_id"
}

json_df = pd.DataFrame(json_data.tolist()).rename(columns=col_map)

# Assign columns from JSON into the main dataframe
# plus clean-up
sanitize_map = {
    "created_on": lambda df: pd.to_datetime(df.created_on),
    "modified_on": lambda df: pd.to_datetime(df.modified_on),
    "json_created_on": lambda df: pd.to_datetime(df.json_created_on),
}

drop_cols = ["normalized_data"]
df = (raw_df.join(json_df)
      .assign(**sanitize_map)
      .drop(columns=drop_cols))

PROFILES = set(df.profile_for_clr_id)
GRANTS = set(df.title)

# %%
matrix = (df.groupby(['title', 'profile_for_clr_id'])
          .amount_per_period_usdt
          .sum()
          .unstack()
          .fillna(0))

# %%

# sns.heatmap(matrix.head(20).T.head(500).T)

plt.matshow(matrix, cmap='inferno')
# %%

# %%

fig_df = (df.groupby(['title', 'profile_for_clr_id'])
          .amount_per_period_usdt
          .sum()
          .reset_index())

cols = ['title', 'profile_for_clr_id', 'amount_per_period_usdt']
fig_df = df.loc[:, cols]

fig = px.parallel_categories(fig_df)
fig.show()
# %%
