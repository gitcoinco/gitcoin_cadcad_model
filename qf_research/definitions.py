from qf_research.quadratic_match import partial_quadratic_match, quadratic_match, total_quadratic_match
from qf_research.functions import total_amount
from qf_research.subgraph_optimizer import optimize_subgraph_connectivity
from typing import Dict, Tuple, List
from tqdm.auto import tqdm
import networkx as nx
import numpy as np
from pathos.multiprocessing import ProcessingPool


def robust_shortest_path_length(*args, **kwargs) -> float:
    output = np.inf
    try:
        output = nx.shortest_path_length(*args, **kwargs)
    finally:
        return output


def NeighborsSubgraph(contribution_graph: nx.Graph, grant: str) -> nx.Graph:
    """
    This function takes in a graph of contributions (contribution_graph) and a 
    grant that corresponds to a vertex within the contribution graph.
    Using this information, the function finds all neighbors within distance 3
    of the grant. 

    :param contribution_graph: A bipartite graph of contributors and the projects
    they are contributing to.

    :param grant: A grant contained within the contribution graph. Used as the
    starting vertex.

    :return: A subgraph of contribution_graph containing all vertices within
    distance 3 of grant. 
    """
    
    return nx.ego_graph(contribution_graph, grant, radius=3)



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


def get_users(G):
    users: set = {
        node
        for (node, data) in G.nodes(data=True)
        if data["type"] == "contributor"
    }
    return users


def get_grants(G):
    grants: set = {
        node
        for (node, data) in G.nodes(data=True)
        if data["type"] == "grant"
    }
    return grants


def grants_funding_share(G: nx.Graph,
                        threshold: float,
                        simple=False) -> Dict[str, float]:
    match_per_grant = quadratic_match(G, threshold, simple=simple)
    total_match = sum(match_per_grant.values())
    return {grant: match_per_grant[grant] / total_match
            for grant in match_per_grant.keys()}


def grant_conjuctured_optimality_gap(G: nx.Graph,
                                     grant: str) -> float:
    subgraph = NeighborsSubgraph(G, grant)
    grants = get_grants(subgraph)
    users = get_users(subgraph)

    N_users = len(users)
    budget = sum(subgraph.edges[e]['amount'] 
                 for e 
                 in subgraph.edges)
    optimal_value = N_users * (N_users - 1) * budget
    optimal_value /= 2 * (N_users + budget)
    assert optimal_value >= 0


    real_value = partial_quadratic_match(G, grants, 1)
    assert real_value >= 0

    if optimal_value == 0:
        optimality_gap = np.nan 
    else:
        optimality_gap = (1 - real_value / optimal_value)

    assert optimal_value >= real_value, (optimal_value, real_value, grant)

    return optimality_gap



def grant_optimality_gap(contribution_graph: nx.Graph,
                         grant: str,
                         **kwargs) -> float:
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
                                                        utility_function,
                                                        **kwargs
                                                        )
    # Compute Optimality Gap
    if optimal_match > 0:
        optimality_gap = (1 - real_match / optimal_match)
        # print("---")
        # print(f"{grant}: {optimality_gap} | {optimal_match} | {real_match}")
    else:
        optimality_gap = np.nan

    return optimality_gap


def optimality_gap_per_grant(contribution_graph: nx.Graph,
                             **kwargs) -> Dict[str, float]:
    """
    Returns a dictionary containing the optimality gap for each grant on
    a contribution graph.
    """
    grants: set = {
        node
        for (node, data) in contribution_graph.nodes(data=True)
        if data["type"] == "grant"
    }

    def f(g): return grant_optimality_gap(contribution_graph, g, **kwargs)

    with ProcessingPool() as pool:
        grants_list = list(grants)
        iterator = tqdm(pool.imap(f, grants_list),
                        desc="Calculating Optimality Gap",
                        total=len(grants_list))
        grants_values = list(iterator)
        optimality_gap_per_grant = dict(zip(grants_list, grants_values))

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
