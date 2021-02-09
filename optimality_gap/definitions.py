from optimality_gap.quadratic_match import partial_quadratic_match
from optimality_gap.functions import total_amount
from optimality_gap.subgraph_optimizer import optimize_subgraph_connectivity
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


def NeighborsSubgraph(contribution_graph: nx.Graph, grant: str) -> nx.Graph:
    """"""
    source = grant
    distances_to_source = {
        target: robust_shortest_path_length(contribution_graph, source, target)
        for target in contribution_graph.nodes
    }

    neighbors = [
        node for (node, distance) in distances_to_source.items() if distance <= 3
    ]

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


def partial_utility_function(graph, nodes):
    return partial_quadratic_match(graph, nodes, THRESHOLD)


def grant_optimality_gap(contribution_graph: nx.Graph, grant: str) -> float:
    """"""
    # Get the Neighbors Subgraph
    real_subgraph = NeighborsSubgraph(contribution_graph, grant)
    subgraph_nodes = set(real_subgraph.nodes)

    # Prepare associated utility function with a given grant
    def utility_function(x): return partial_utility_function(x, subgraph_nodes)

    # Get current match
    real_match = utility_function(contribution_graph)

    # Compute optimal match
    (_, optimal_match) = optimize_subgraph_connectivity(contribution_graph,
                                                        subgraph_nodes,
                                                        utility_function
                                                        )
    # Compute Optimality Gap
    if optimal_match > 0:
        optimality_gap = (1 - real_match / optimal_match)
        # print("---")
        # print(f"{grant}: {optimality_gap} | {optimal_match} | {real_match}")
    else:
        optimality_gap = np.nan

    return optimality_gap


def optimality_gap_per_grant(contribution_graph: nx.Graph) -> Dict[str, float]:
    """
    Returns a dictionary containing the optimality gap for each grant on
    a contribution graph.
    """
    grants: set = {
        node
        for (node, data) in contribution_graph.nodes(data=True)
        if data["type"] == "grant"
    }

    optimality_gap_per_grant = {grant: grant_optimality_gap(contribution_graph, grant)
                                for grant
                                in tqdm(grants, desc="Calculating Optimality Gap")}

    return optimality_gap_per_grant


def amount_per_grant(contribution_graph: nx.Graph) -> Dict[str, float]:
    """
    Returns a dictionary containing the quadratic match for each grant on
    a contribution graph.
    """
    grants: set = {
        node
        for (node, data) in contribution_graph.nodes(data=True)
        if data["type"] == "grant"
    }

    amount_per_grant = {grant: total_amount(contribution_graph, grant)
                                for grant in grants}

    return amount_per_grant
