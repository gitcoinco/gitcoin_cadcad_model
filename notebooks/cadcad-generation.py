
# %% [markdown]
# # Generating Gitcoin Grants Network through cadCAD
#

# %%
import networkx as nx
from typing import List, Tuple, Dict

# %%
EDGE_PER_TIMESTEP: Dict[int, Tuple[str, str]] = {1: (0, 1),
                                                 2: (0, 2),
                                                 3: (1, 5)}


genesis_state = {
    'network': nx.Graph()
}


sys_params = {
    'edge_per_timestep': [EDGE_PER_TIMESTEP]
}


def s_append_edges(params, substep, state_history, prev_state):
    # Dependences
    timestep: int = len(state_history)
    timestep_edge: tuple = params['edge_per_timestep'][timestep]
    G = prev_state['network'].copy()

    # SUF logic
    G.add_edge(*timestep_edge)
    return ('network', G)


partial_state_update_blocks = [
    {
        'label': 'Append new edges to the network',
        'policies': {

        },
        'variables': {
            'network': s_append_edges

        }
    }
]


