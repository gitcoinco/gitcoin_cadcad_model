import networkx as nx
import random
from typing import Callable, List, Tuple
from tqdm.auto import tqdm

def optimize_graph_connectivity(subgraph: nx.Graph,
                                utility_function: Callable[[nx.Graph], float]) -> Tuple[nx.Graph, float]:

    destination_nodes: list = [node
                               for node, value in dict(subgraph.nodes.data('type')).items()
                               if value == 'destination']

    edges: list = [edg for edg in subgraph.edges]

    best_subgraph: nx.Graph = subgraph.copy()
    best_score: float = utility_function(best_subgraph)

    print("Optimizing subgraph")
    for edge in tqdm(edges, desc='Sweeping edges'):
        src_node: str = edge[0]
        for dst_node in destination_nodes:
            # Create a copy from the original graph for mutation
            temp_subgraph: nx.Graph = subgraph.copy()
            temp_subgraph.remove_edge(*edge)

            # Add the edge mutation
            temp_edge: tuple = (src_node, dst_node)
            temp_subgraph.add_edge(*temp_edge)

            # Retrieve score
            score: float = utility_function(temp_subgraph)
            if score > best_score:
                best_subgraph: nx.Graph = temp_subgraph.copy()

    return (best_subgraph, best_score)
