import networkx as nx
import random
from typing import Callable, List


def test():
    test_graph: nx.Graph = create_test_graph(1000, 42)
    result: tuple = optimize_graph_connectivity(test_graph, utility_function)
    print(f"Best subgraph: {result[0]}")
    print(f"Best score: {result[1]}")


def create_test_graph(n: int, seed: int) -> nx.Graph:
    internet: nx.Graph = nx.random_internet_as_graph(n, seed=seed)
    node_types: List[str] = ['source', 'destination']

    for i in range(n):
        internet.add_node(i, type=random.choice(node_types))

    return internet


def utility_function(G): return nx.wiener_index(G)


def optimize_graph_connectivity(subgraph: nx.Graph,
                                utility_function: Callable[[nx.Graph], float]) -> tuple:

    destination_nodes: list = [node
                               for node, value in dict(subgraph.nodes.data('type')).items()
                               if value == 'destination']

    edges: list = [edg for edg in subgraph.edges]

    best_subgraph: nx.Graph = subgraph.copy()
    best_score: float = utility_function(best_subgraph)

    for edge in edges:
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


if __name__ == "__main__":
    test()
