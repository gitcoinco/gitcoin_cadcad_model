# %% [markdown]
# # Wrangling Gitcoin Metabase data
#

# %%

# Magic for getting the execution time for each cell
import plotly.express as px
# Power laws are probability distributions with the form:p(x)∝x−α
import powerlaw
import matplotlib.pyplot as plt
import networkx as nx
import json
import pandas as pd
(get_ipython().run_line_magic("load_ext", "autotime"))


# %% [markdown]
# ## Dataframe wrangling
#

# %%

DATA_PATH = "../data/query_result_2020-10-12T20_42_24.031Z.csv"

raw_df = pd.read_csv(DATA_PATH)

#  %%
# Parse the normalized data strings into dictionaries

json_data = raw_df.normalized_data.map(json.loads)
# %%
# Create a data frame from the normalized data parsed series
col_map = {
    "id": "json_id",
    "created_on": "json_created_on",
    "tx_id": "json_tx_id"
}

json_df = pd.DataFrame(json_data.tolist()).rename(columns=col_map)
# %%
# Assign columns from JSON into the main dataframe
# plus clean-up

sanitize_map = {
    "created_on": lambda df: pd.to_datetime(df.created_on),
    "modified_on": lambda df: pd.to_datetime(df.modified_on),
    "json_created_on": lambda df: pd.to_datetime(df.json_created_on),
}

drop_cols = ["normalized_data"]

df = raw_df.join(json_df).assign(**sanitize_map).drop(columns=drop_cols)

# %% [markdown]
# ## Graph wrangling
#
# %%

# %%
df.apply(lambda x: len(x.unique()))
# %%
G = nx.from_pandas_edgelist(df,
                            source="profile_for_clr_id",
                            target="json_tx_id",
                            edge_attr=True)
# %%
len(G.edges)
# %%
degree_sequence = sorted(
    [d for n, d in G.degree() if d < 800],
    reverse=True)  # used for degree distribution and powerlaw test
fit = powerlaw.Fit(degree_sequence)
fit = powerlaw.Fit(degree_sequence, xmin=1)

fig2 = fit.plot_pdf(color='b', linewidth=2)
fit.power_law.plot_pdf(color='g', linestyle='--', ax=fig2)
plt.xlabel("Degree")
plt.ylabel("Probability Density")
# %%
R, p = fit.distribution_compare('power_law',
                                'exponential',
                                normalized_ratio=True)
print(R, p)
# %%
plt.figure(figsize=(10, 6))
fit.distribution_compare('power_law', 'lognormal')
fig4 = fit.plot_ccdf(linewidth=3, color='black')
fit.lognormal.plot_ccdf(ax=fig4, color='g', linestyle='--')  # lognormal
# %%

# %%
plt.hist(degree_sequence, log=True, range=(0, 10))
# %%
degree_sequence
# %%
G = nx.from_pandas_edgelist(df.head(100),
                            source="profile_for_clr_id",
                            target="title",
                            edge_attr=True,
                            create_using=nx.MultiDiGraph)
# %%
nx.draw_kamada_kawai(G)
# %%

y = df.set_index('created_on').amount_per_period_usdt.resample('1h').sum()

fig_df = y.reset_index()

px.density_heatmap(fig_df,
                   x=fig_df.created_on.dt.hour,
                   y=fig_df.amount_per_period_usdt)
# %%
g_map = {
    'created_on': lambda df: df.created_on.astype(int),
    'modified_on': lambda df: df.modified_on.astype(int),
    'json_created_on': lambda df: df.json_created_on.astype(int)
}

r_map = {col: col.replace("_", "") for col in df.columns if "_" in col}

g_df = (df.assign(**g_map)
        .rename(columns=r_map)
        .drop(columns=['txid'])
        .dropna()
        )

G = nx.from_pandas_edgelist(g_df,
                            source="profileforclrid",
                            target="title",
                            edge_attr=True,
                            create_using=nx.MultiDiGraph)

titles = g_df.title.unique()
for node in G.nodes:
    if node in titles:
        kind = 'grant'
    else:
        kind = 'contributor'
    G.nodes[node]['kind'] = kind

deg = nx.degree(G)
to_remove = [k for k, v in deg if v > 500]
G.remove_nodes_from(to_remove)


nx.write_gml(G, 'graph.gml')

# %%
