import json
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import cv2
from tqdm.auto import tqdm


def load_contributions_sequence_from_csv(path: str, limit: int=None) -> dict:
    df = pd.read_csv(path)
    if limit is not None:
        df = df.head(limit)
    else:
        pass
    return df.to_dict(orient='index')



def load_contributions_sequence_from_excel(path) -> dict:
    df = pd.read_excel(path, sheet_name='contribution_sequence')
    return df.to_dict(orient='index')


def plot_contributions(contributions: pd.Series,counter=0,savefigs=False):
        
    g_df = pd.DataFrame(contributions)

    contributor_nodes = g_df.contributor.values
    grant_nodes = g_df.grant.values
    amount_edges = g_df.amount.values
    sybil_edges = g_df.sybil_score.values

    G = nx.Graph()
    for i in contributor_nodes:
        G.add_node(i)
        G.nodes[i]['type']= 'Contributor'

    for j in grant_nodes:
        G.add_node(j)
        G.nodes[j]['type']= 'Grant'

    for i,j,p in zip(contributor_nodes,grant_nodes,range(0,len(grant_nodes))):
        G.add_edge(i, j)
        G.edges[(i,j)]['amount'] = amount_edges[p]
        G.edges[(i,j)]['type'] = 'support'
        G.edges[(i,j)]['sybil_score'] = sybil_edges[p]


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

    grant_color = (g_df.groupby('grant').sybil_score.mean().to_dict())
    grant_color = {x: 'red' for x in grant_color}

    collaborator_color = (g_df.groupby('contributor').sybil_score.mean().to_dict())
    collaborator_color = {x: 'blue' for x in collaborator_color}

    node_colors = {**grant_color, **collaborator_color}
    nx.set_node_attributes(G, node_colors, 'color')

    edge_weights = {n: v for n,
                    v in nx.get_edge_attributes(G, 'amount').items()}

    nx.set_edge_attributes(G, edge_weights, 'amount')


    edges = []
    for i in nx.get_edge_attributes(G, 'amount').values():
        edges.append(i)

    max_amount = max(edges)
    min_amount = 0
    normed_edges = []
    for i in nx.get_edge_attributes(G, 'amount').values():
        normed_edges.append((i-0)/(max_amount - 0))
        
    fig = plt.figure(figsize=(12, 12))
    nx.draw_networkx(G, 
            pos = nx.drawing.layout.bipartite_layout(G, contributor_nodes),
            node_color= list(nx.get_node_attributes(G, 'color').values()),
            node_size = list(nx.get_node_attributes(G, 'size').values()),
            edge_color = normed_edges,
            alpha = 0.4,
            cmap = plt.cm.PiYG,
            edge_cmap = plt.cm.PiYG,
            with_labels = False
            )

    plt.title('Tokens donated by Contributors to Grants \n Timestep {} \n USDT {}'.format(counter,round(max_amount,2)))
    contributor_patch = mpatches.Patch(color='blue', label='Contributor')
    grant_patch = mpatches.Patch(color='red', label='Grant')
    plt.legend(handles=[contributor_patch,grant_patch],loc='upper left')
    plt.tight_layout()
    plt.xticks([])
    plt.yticks([])
    if savefigs:
        plt.savefig('images/'+str(counter)+'.png',bbox_inches='tight')
    plt.show()
    


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
        plot_contributions(contributions,counter=i,savefigs=True)

    # sort the resulting images by earliest, which will correspond to the first snap plot
    images = sorted(glob.glob('images/*.png'), key=os.path.getmtime)

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
        'snap_plot.avi', cv2.VideoWriter_fourcc(*'DIVX'), 25, size)

    # iterate through images and make into movie.
    for i in tqdm(range(len(img_array)), total=len(img_array)):
        out.write(img_array[i])
    out.release()
    


