import networkx as nx
import numpy as np
import random
from typing import Callable, List, Tuple, Callable
from tqdm.auto import tqdm
from networkx.algorithms.rewiring import simulated_annealing_optimize


def rewiring_rule(G: nx.Graph, seed=None) -> nx.Graph:
    r = random.Random(seed)

    contributors_set = {n
                        for n, attrs
                        in G.nodes(data=True)
                        if attrs['type'] == 'contributor'}

    grants_set = {n
                  for n, attrs
                  in G.nodes(data=True)
                  if attrs['type'] == 'grant'}

    if len(G.nodes) > 2 and len(G.edges) > 1:
        edge = r.choice(tuple(G.edges))
        edge_data = G.edges[edge]
        node_1 = r.choice(tuple(contributors_set))
        node_2 = r.choice(tuple(grants_set))
        G_temp = G.copy()
        G_temp.remove_edge(*edge)
        G_temp.add_edge(node_1, node_2, **edge_data)
        return G_temp
    else:
        raise ValueError('Graph must have more than two nodes & one edge')


def optimize_graph_connectivity(subgraph: nx.Graph,
                                utility_function: Callable[[nx.Graph], float]) -> Tuple[nx.Graph, float]:

    best_score = utility_function(subgraph)
    best_subgraph = subgraph

    try:
        (best_score, best_subgraph) = simulated_annealing_optimize(subgraph,
                                                                utility_function,
                                                                rewiring_rule,
                                                                n_iter=3)
    finally:
        return (best_subgraph, best_score)
