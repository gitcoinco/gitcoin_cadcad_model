# %% [markdown]
# # Community funding PoC
# ## Dependences and parameters

# %%
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

G = nx.from_pandas_edgelist(df,
                            source="profile_for_clr_id",
                            target="title",
                            edge_attr=True)
# %%
# Functions for getting the funding for a node and a list of nodes

def grant_funding(graph: nx.Graph,
                  node: str) -> float:
    METRIC = 'amount_per_period_usdt'
    node_edges = [edge for edge in graph.edges if edge[-1] == node]
    grant_funding = sum(graph.edges[edge][METRIC] for edge in node_edges)
    return grant_funding

assert grant_funding(G, 'Cryptocrow.net') == pytest.approx(9.5)

def community_funding(graph: nx.Graph,
                      nodes: List[str]) -> float:
    funding = sum(grant_funding(graph, node) for node in nodes)    
    return funding

COMMUNITY_TEST = ['Cryptocrow.net', 'liquiDefi']
funding_test = sum(grant_funding(G, n) for n in COMMUNITY_TEST)

assert community_funding(G, COMMUNITY_TEST) == pytest.approx(funding_test)

# %%
# Get the giant component

giant_component_nodes = max(nx.connected_components(G), key=len)
giant_subgraph = G.subgraph(giant_component_nodes)
communities = list(nx.algorithms.community.asyn_fluidc(giant_subgraph, 3))
# %%
grant_communities = [comm & GRANTS for comm in communities]
profile_communities = [comm & PROFILES for comm in communities]

# %%
community_funding(G, grant_communities[0])
# %%

# %%
