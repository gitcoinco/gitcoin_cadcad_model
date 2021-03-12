import networkx as nx
import random
from typing import Callable, List
from subgraph_optimizer import *

def create_test_graph(n: int, seed: int) -> nx.Graph:
    internet: nx.Graph = nx.random_internet_as_graph(n, seed=seed)
    node_types: List[str] = ['source', 'destination']

    for i in range(n):
        internet.add_node(i, type=random.choice(node_types))

    return internet

def utility_function(G): return nx.wiener_index(G)


def test_utility():
    test_graph: nx.Graph = create_test_graph(50, 42)
    result: tuple = optimize_graph_connectivity(test_graph, utility_function)
    print(f"Best subgraph: {result[0]}")
    print(f"Best score: {result[1]}")


if __name__ == '__main__':
    test_utility()

