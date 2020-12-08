import json
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import cv2
from tqdm.auto import tqdm

def load_contributions_sequence(limit=1000) -> dict:
    """
    Returns a dict that represents a event sequence of contributions containing
    the grant, collaborator and amount as key-values.
    """
    DATA_PATH = "../data/query_result_2020-10-12T20_42_24.031Z.csv"
    raw_df = pd.read_csv(DATA_PATH)

    # Parse the normalized data strings into dictionaries
    json_data: dict = raw_df.normalized_data.map(json.loads)

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

    # Filter GC grants round & GC bot
    QUERY = 'title != "Gitcoin Grants Round 8 + Dev Fund"'
    QUERY += ' | '
    QUERY += 'profile_for_clr_id != 2853'
    df = (raw_df.join(json_df)
                .assign(**sanitize_map)
                .drop(columns=drop_cols)
                .query(QUERY))

    # Sort df and return dict
    sorted_df = df.sort_values('created_on')

    # Get only the --limit-- first rows
    if limit is not None:
        sorted_df = sorted_df.head(limit)

    # Columns which are to keep into the dynamical network
    event_property_map = {'profile_for_clr_id': 'contributor',
                          'title': 'grant',
                          'amount_per_period_usdt': 'amount',
                          'sybil_score': 'sybil_score'}

    # Create a dict in the form {ts: {**event_attrs}}
    event_sequence = (sorted_df.rename(columns=event_property_map)
                      .loc[:, event_property_map.values()]
                      .reset_index(drop=True)
                      .to_dict(orient='index')
                      )

    return event_sequence


def load_contributions_sequence_from_excel(path) -> dict:
    df = pd.read_excel(path, sheet_name='contribution_sequence')
    return df.to_dict(orient='index')


def plot_contributions(contributions: pd.Series):
    g_df = pd.DataFrame(contributions)

    G = nx.from_pandas_edgelist(g_df,
                                source='contributor',
                                target='grant',
                                edge_attr=True)

    profiles = {e[0] for e in G.edges}
    grants = {e[-1] for e in G.edges}

    grant_sizes = (g_df.groupby('grant')
                   .amount
                   .sum()
                   .map(lambda x: x)
                   .to_dict())

    collaborator_sizes = (g_df.groupby('contributor')
                          .amount
                          .sum()
                          .map(lambda x: x)
                          .to_dict())

    node_sizes = {**grant_sizes, **collaborator_sizes}
    nx.set_node_attributes(G, node_sizes, 'size')

    grant_color = (g_df.groupby('grant')
                   .sybil_score
                   .mean()
                   .to_dict())

    collaborator_color = (g_df.groupby('contributor')
                          .sybil_score
                          .mean()
                          .to_dict())

    node_colors = {**grant_color, **collaborator_color}
    nx.set_node_attributes(G, node_colors, 'color')

    edge_weights = {n: v for n,
                    v in nx.get_edge_attributes(G, 'amount_per_period_usdt').items()}

    nx.set_edge_attributes(G, edge_weights, 'weight')
    dt = len(profiles) / len(grants)
    profile_pos = {node: (0, i) for (i, node) in enumerate(profiles)}
    grant_pos = {node: (1, i * dt) for (i, node) in enumerate(grants)}
    pos = {**profile_pos, **grant_pos}
    labels = {node: node for node in profiles | grants}

    options = {
        "node_color": list(nx.get_node_attributes(G, 'color').values()),
        "node_size": list(nx.get_node_attributes(G, 'size').values()),
        "edge_color": nx.get_edge_attributes(G, 'sybil_score').values(),
        "width": list(nx.get_edge_attributes(G, 'weight').values()),
        "alpha": 0.4,
        "cmap": plt.cm.PiYG,
        "edge_cmap": plt.cm.PiYG,
        "with_labels": False,
    }

    fig = plt.figure(figsize=(12, 12))
    nx.draw(G, pos, **options)
    return fig


def create_video_snap(contributions_list: list):
    '''
    Definition:
    Function to create an avi movie going through each stage of the snap plot.
    Parameters:
    nets: network x object
    size_scale: optional size scaling parameter
    dims: optional figure dimension
    savefigs: optional boolean for saving figure
    Returns:
    Moving of the bipartite graph of participants and proposals changing
    '''
    # call snapplot
    for i, contributions in tqdm(enumerate(contributions_list), total=len(contributions_list)):
        fig = plot_contributions(contributions)
        plt.savefig(f'../images/movie_frames/{i}.png', bbox_inches='tight')
        plt.close(fig)

    # sort the resulting images by earliest, which will correspond to the first snap plot
    images = sorted(glob.glob('../images/movies_frames/*.png'), key=os.path.getmtime)

    # iterate through the images, convert, and add to array
    size = 0
    img_array = []
    for filename in images:
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)

    # video object
    out = cv2.VideoWriter(
        '../images/videos/snap_plot.avi', cv2.VideoWriter_fourcc(*'DIVX'), 25, size)

    # iterate through images and make into movie.
    for i in tqdm(range(len(img_array)), total=len(img_array)):
        out.write(img_array[i])
    out.release()
