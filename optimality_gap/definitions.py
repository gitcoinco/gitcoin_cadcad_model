from .quadratic_match import total_quadratic_match
from optimality_gap.functions import contributions_to_graph
from optimality_gap.subgraph_optimizer import optimize_graph_connectivity
from typing import Dict, Tuple, List
from tqdm.auto import tqdm
import networkx as nx
import numpy as np


def robust_shortest_path_length(*args, **kwargs) -> float:
    output = np.inf
    try:
        output = nx.shortest_path_length(*args, **kwargs)
    finally:
        return output
    

def NeighborsSubgraph(contribution_graph: nx.Graph,
                      grant: str) -> nx.Graph:
    """

    """
    source = grant
    distances_to_source = {target: robust_shortest_path_length(contribution_graph,
                                                           source,
                                                           target)
                           for target in contribution_graph.nodes}

    neighbors = [node for (node, distance) in distances_to_source.items()
                 if distance <= 3]

    neighbors_subgraph = contribution_graph.subgraph(neighbors)
    return neighbors_subgraph


"""
all_grants = List[Grant]
quadratic_match(Grant) -> float
quadratic_match_subgraph: float = sum(quadratic_match(grant)
                                      for grant in all_grants)
"""
# Implementation of above

THRESHOLD = 0.3  # need to check it up
def utility_function(graph): return total_quadratic_match(graph, THRESHOLD)


def grant_optimality_gap(contribution_graph: nx.Graph,
                         grant: str) -> float:
    """

    """
    real_subgraph = NeighborsSubgraph(contribution_graph, grant)
    real_match = utility_function(real_subgraph)
    (optimal_subgraph, optimal_match) = optimize_graph_connectivity(
        real_subgraph, utility_function)

    if optimal_match > 0:
        optimality_gap = 1 - real_match / optimal_match
    else:
        optimality_gap = np.nan

    return optimality_gap


def graph_optimality_gap_distribution(contribution_graph: nx.Graph) -> List[float]:
    """
    """
    grants = {node
              for (node, data) in contribution_graph.nodes(data=True)
              if data['type'] == 'grant'}

    distribution = []
    for grant in tqdm(grants, desc='Calculating optimality gap'):
        metric = grant_optimality_gap(contribution_graph, grant)
        distribution.append(metric)
    return distribution
