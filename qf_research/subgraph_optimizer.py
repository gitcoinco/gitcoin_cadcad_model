import networkx as nx
import numpy as np
import random
from typing import Callable, List, Tuple, Callable
from tqdm.auto import tqdm

from qf_research.meta_heuristics import hill_climb_optimize
from qf_research.meta_heuristics import simulated_annealing_optimize


def subgraph_rewire(G: nx.Graph, nodes: set, seed=None) -> Tuple[nx.Graph, nx.Graph]:
    """
    Rewire a graph with rewiring restricted to a subgraph of it.

    Arguments
    ---
    G: NetworkX graph
    nodes: Set of nodes that makes the subgraph
    seed: random seed
    """
    r = random.Random(seed)

    subgraph = G.subgraph(nodes)

    contributors_set = {
        n for n, attrs in subgraph.nodes(data=True) if attrs["type"] == "contributor"
    }

    grants_set = {
        n for n, attrs in subgraph.nodes(data=True) if attrs["type"] == "grant"
    }

    if len(subgraph.nodes) > 2 and len(subgraph.edges) > 1:
        edge = r.choice(tuple(subgraph.edges))
        edge_data = G.edges[edge]
        node_1 = r.choice(tuple(contributors_set))
        node_2 = r.choice(tuple(grants_set))
        G_new = G.copy()
        G_new.remove_edge(*edge)
        G_new.add_edge(node_1, node_2, **edge_data)
        return G_new
    else:
        raise ValueError("Subgraph must have more than two nodes & one edge")


def optimize_subgraph_connectivity(graph: nx.Graph,
                                   nodes: set,
                                   utility_function: Callable[[nx.Graph], float],
                                   n_iter: int = 50,
                                   **kwargs) -> Tuple[nx.Graph, float]:
    """
    Optimize graph with the rewire operations restricted to the nodes 
    given as arguments.

    Arguments
    ---
    graph: NetworkX graph
    nodes: Set
        Nodes contained on `graph`
    utility_function: Function
        It takes a graph and returns a real number. Higher values are more optimal.
    """

    best_score = utility_function(graph)
    best_subgraph = graph.subgraph(nodes)

    rewiring_rule: callable = lambda x: subgraph_rewire(x, nodes)

    try:
        # (best_score, best_subgraph) = simulated_annealing_optimize(graph,
        #                                                            utility_function,
        #                                                            rewiring_rule,
        #                                                            n_iter=3)
        (best_score, best_subgraph) = hill_climb_optimize(
            graph, utility_function, rewiring_rule, n_iter=n_iter, **kwargs
        )
    finally:
        return (best_subgraph, best_score)
