import pandas as pd
import networkx as nx

def total_amount(G: nx.Graph,
                 node: str) -> float:
    """
    Get the total amount in USDT of contribution
    for a given node (grant or contributor)
    """
    # Get all the graph edges associated with the node
    node_edges = G.edges([node])
    
    # Sum all amounts contained in the edges that contains the node
    total_amount = sum(G.edges[edge]['amount']
                       for edge
                       in node_edges)
    
    # Return it
    return total_amount


def contributions_to_graph(contrib_row: list) -> nx.Graph:
    """
    Convert a contributions row from the cadCAD results DataFrame
    into a NetworkX graph.
    """
    # Make sure that we have data
    if len(contrib_row) > 0:
        
        # Load data
        c_df = pd.DataFrame(contrib_row)
        
        # Parse the contributions into a NetworkX graph
        G = nx.from_pandas_edgelist(c_df,
                                    source='contributor',
                                    target='grant',
                                    edge_attr=True)
        
        # Get unique grants and contributors
        unique_grants = c_df.grant.unique()
        unique_contributors = c_df.contributor.unique()
        
        # Associate the 'type' and 'total_amount' attributes for grants and contributors
        grant_node_type = {el: {'type': 'grant',
                                'total_amount': total_amount(G, el)} 
                           for el in unique_grants}
        contrib_node_type = {el: {'type': 'contributor',
                                  'total_amount': total_amount(G, el)} 
                             for el in unique_contributors}
        node_type = {**grant_node_type, **contrib_node_type}    
        
        nx.set_node_attributes(G, node_type)
        
        # Return the graph
        return G
    else:
        return None
