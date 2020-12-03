
# %% [markdown]
# # Generating Gitcoin Grants Network through cadCAD
#

# %%
import matplotlib.pyplot as plt
from collections import defaultdict
from typing import List, Tuple, Dict
import plotly.express as px
import json
import pandas as pd
import networkx as nx
from cadCAD.engine import Executor, ExecutionMode, ExecutionContext
from cadCAD.configuration import Experiment
from cadCAD.configuration.utils import bound_norm_random, ep_time_step, config_sim, access_block
from cadCAD import configs
import numpy as np
(get_ipython().run_line_magic("load_ext", "autotime"))


# %%


LIMIT_SEQUENCE = 1000  # pass None to get everything


def load_contributions_sequence() -> dict:
    """
    Returns a dict that represents a event sequence of contributions containing
    the grant, collaborator and amount as key-values.
    """
    DATA_PATH = "../data/query_result_2020-10-12T20_42_24.031Z.csv"
    raw_df = pd.read_csv(DATA_PATH)

    # Parse the normalized data strings into dictionaries
    json_data: dict = raw_df.normalized_data.map(json.loads)

    # Create a data frame from the normalized data parsed series
    col_map = {
        "id": "json_id",
        "created_on": "json_created_on",
        "tx_id": "json_tx_id"
    }
    json_df = pd.DataFrame(json_data.tolist()).rename(columns=col_map)

    # Assign columns from JSON into the main dataframe
    # plus clean-up
    sanitize_map = {
        "created_on": lambda df: pd.to_datetime(df.created_on),
        "modified_on": lambda df: pd.to_datetime(df.modified_on),
        "json_created_on": lambda df: pd.to_datetime(df.json_created_on),
    }

    drop_cols = ["normalized_data"]

    # Filter GC grants round & GC bot
    QUERY = 'title != "Gitcoin Grants Round 8 + Dev Fund"'
    QUERY += ' | '
    QUERY += 'profile_for_clr_id != 2853'
    df = (raw_df.join(json_df)
                .assign(**sanitize_map)
                .drop(columns=drop_cols)
                .query(QUERY))

    # Sort df and return dict
    sorted_df = df.sort_values('created_on')

    if LIMIT_SEQUENCE is not None:
        sorted_df = sorted_df.head(LIMIT_SEQUENCE)

    event_property_map = {'profile_for_clr_id': 'contributor',
                          'title': 'grant',
                          'amount_per_period_usdt': 'amount',
                          'sybil_score': 'sybil_score'}

    event_sequence = (sorted_df.rename(columns=event_property_map)
                      .loc[:, event_property_map.values()]
                      .reset_index(drop=True)
                      .to_dict(orient='index')
                      )

    return event_sequence


# %%

CONTRIBUTIONS_SEQUENCE: dict = load_contributions_sequence()

genesis_states = {
    # 'network': nx.DiGraph(),
    'contributions': [],
    # (N_user, N_user)
    'pair_totals': defaultdict(lambda: defaultdict(lambda: 0.0)),
    'quadratic_match': defaultdict(lambda: 0.0),  # (N_grant)
    'quadratic_funding_per_grant': defaultdict(lambda: 0.0),
    'quadratic_match_per_grant': defaultdict(lambda: 0.0),
    'quadratic_total_match': 0.0,
    'quadratic_total_funding': 0.0,
}


sys_params = {
    'contribution_sequence': [CONTRIBUTIONS_SEQUENCE],
    'trust_bonus_per_user': [defaultdict(lambda: 1.0)],
    'v_threshold': [0.3],
    'total_pot': [5000]
}


# %%

def aggregate_contributions(grant_contributions):
    contrib_dict = {}
    for contrib in grant_contributions:
        user, proj, amount, _ = contrib.values()
        if proj not in contrib_dict:
            contrib_dict[proj] = {}
        contrib_dict[proj][user] = contrib_dict[proj].get(user, 0) + amount
    return contrib_dict


def get_totals_by_pair(contrib_dict):
    tot_overlap = {}

    # start pairwise match
    for _, contribz in contrib_dict.items():
        for k1, v1 in contribz.items():
            if k1 not in tot_overlap:
                tot_overlap[k1] = {}

            # pairwise matches to current round
            for k2, v2 in contribz.items():
                if k2 not in tot_overlap[k1]:
                    tot_overlap[k1][k2] = 0
                tot_overlap[k1][k2] += (v1 * v2) ** 0.5

    return tot_overlap


def match_project(contribz, pair_totals, threshold):
    proj_total = 0
    for k1, v1 in contribz.items():
        for k2, v2 in contribz.items():
            if k2 > k1:
                # quadratic formula
                p = pair_totals[k1][k2]
                if p == 0:
                    continue
                else:
                    proj_total += (threshold + 1) * ((v1 * v2) ** 0.5) / p
    return np.real(proj_total)


def p_new_contribution(params, substep, state_history, prev_state):
    timestep: int = prev_state['timestep']
    new_contribution: tuple = params['contribution_sequence'][timestep]
    return {'new_contribution': new_contribution}


def s_append_contribution(params, substep, state_history, prev_state, policy_input):
    contributions = prev_state['contributions'].copy()
    contributions.append(policy_input.get('new_contribution'))
    return ('contributions', contributions)


def s_append_edges(params, substep, state_history, prev_state, policy_input):
    # Dependences
    G = prev_state['network'].copy()
    contribution = policy_input['new_contribution']
    G.add_edge(contribution['contributor'], contribution['grant'])
    return ('network', G)


def p_quadratic_match(params, substep, state_history, prev_state):
    threshold = params['v_threshold']
    total_pot = params['total_pot']
    pair_totals = prev_state['pair_totals']
    contributions = prev_state['contributions']

    grants = {c['grant'] for c in contributions}
    contrib_dict = aggregate_contributions(contributions)
    pair_totals = get_totals_by_pair(contrib_dict)
    M = {proj: match_project(contribz, pair_totals, threshold)
         for proj, contribz in contrib_dict.items()}

    total_match = sum(M.values())
    F = {}
    if total_match > total_pot:
        F = {g: total_pot * M[g] / total_match
             for g in grants}
    else:
        if total_match == 0:
            total_match = 1.0
        F = {g: M[g] + (1 + np.log(total_pot / total_match) / 100)
             for g in grants}

    return {'quadratic_match_per_grant': M,
            'quadratic_funding_per_grant': F}


def s_quadratic_match_per_grant(params, substep, state_history, prev_state, policy_input):
    M = policy_input['quadratic_match_per_grant']
    return ('quadratic_match_per_grant', M)


def s_quadratic_funding_per_grant(params, substep, state_history, prev_state, policy_input):
    F = policy_input['quadratic_funding_per_grant']
    return ('quadratic_funding_per_grant', F)


def s_quadratic_total_match(params, substep, state_history, prev_state, policy_input):
    M = policy_input['quadratic_match_per_grant']
    return ('quadratic_total_match', sum(M.values()))


def s_quadratic_total_funding(params, substep, state_history, prev_state, policy_input):
    F = policy_input['quadratic_funding_per_grant']
    return ('quadratic_total_funding', sum(F.values()))


partial_state_update_blocks = [
    {
        'label': 'Append new edges to the network',
        'policies': {
            'new_contribution': p_new_contribution
        },
        'variables': {
            # 'network': s_append_edges,
            'contributions': s_append_contribution
        },
    },
    {
        'label': 'Quadratic Funding',
        'policies': {
            'quadratic_match': p_quadratic_match
        },
        'variables': {
            'quadratic_match_per_grant': s_quadratic_match_per_grant,
            'quadratic_funding_per_grant': s_quadratic_funding_per_grant,
            'quadratic_total_funding': s_quadratic_total_funding,
            'quadratic_total_match': s_quadratic_total_match

        }
    },
]


sim_params = {
    'N': 1,
    'T': range(len(CONTRIBUTIONS_SEQUENCE)),
    'M': sys_params
}

sim_config = config_sim(sim_params)

exp = Experiment()
exp.append_configs(sim_configs=sim_config,
                   initial_state=genesis_states,
                   partial_state_update_blocks=partial_state_update_blocks)


def run(input_config):
    '''
    Definition:
    Run simulation

    Parameters:
    input_config: Optional way to pass in system configuration
    '''
    exec_mode = ExecutionMode()
    # the code below selects the execution mode.
    # local_mode defaults to multi-threaded.
    # using single_mode for development
    local_mode_ctx = ExecutionContext(context=exec_mode.local_mode)
    simulation = Executor(exec_context=local_mode_ctx, configs=input_config)
    raw_system_events, tensor_field, sessions = simulation.execute()
    # dataframe = pd.DataFrame(raw_system_events)  # Result System Events DataFrame
    # representation of the data./ when n=5 you have 5x the data. additional runs are in a sequential order.
    # looking at a time step
    # Postprocessing from Danilo
    # Get system events and attribute index
    df = (pd.DataFrame(raw_system_events))
    # Clean substeps
    first_ind = (df.substep == 0) & (df.timestep == 0)
    last_ind = df.substep == max(df.substep)
    inds_to_drop = (first_ind | last_ind)
    df = df.loc[inds_to_drop].drop(columns=['substep'])

    # Set indexes
    df = df.set_index(['simulation', 'subset', 'run', 'timestep'])
    return df


result = run(configs)

# %%
df = result.loc[(0, 0, 1, slice(None))]
px.line(df.reset_index(),
        x='timestep',
        y=['quadratic_total_match', 'quadratic_total_funding'])


# %%
y = df.quadratic_total_funding / df.quadratic_total_match
y.name = 'funding_per_match'
px.line(y.reset_index(),
        x='timestep',
        y='funding_per_match',
        log_y=True)
# %%

g_df = pd.DataFrame(df.contributions.iloc[-1])

G = nx.from_pandas_edgelist(g_df,
                            source='contributor',
                            target='grant',
                            edge_attr=True)

profiles = {e[0] for e in G.edges}
grants = {e[-1] for e in G.edges}

grant_sizes = (g_df.groupby('grant')
                 .amount
                 .sum()
                 .map(lambda x: x)
                 .to_dict())

collaborator_sizes = (g_df.groupby('contributor')
                        .amount
                        .sum()
                        .map(lambda x: x)
                        .to_dict())

node_sizes = {**grant_sizes, **collaborator_sizes}
nx.set_node_attributes(G, node_sizes, 'size')

grant_color = (g_df.groupby('grant')
               .sybil_score
               .mean()
               .to_dict())

collaborator_color = (g_df.groupby('contributor')
                      .sybil_score
                      .mean()
                      .to_dict())


node_colors = {**grant_color, **collaborator_color}
nx.set_node_attributes(G, node_colors, 'color')

edge_weights = {n: v for n,
                v in nx.get_edge_attributes(G, 'amount_per_period_usdt').items()}

nx.set_edge_attributes(G, edge_weights, 'weight')
dt = len(profiles) / len(grants)
profile_pos = {node: (0, i) for (i, node) in enumerate(profiles)}
grant_pos = {node: (1, i * dt) for (i, node) in enumerate(grants)}
pos = {**profile_pos, **grant_pos}
labels = {node: node for node in profiles | grants}


options = {
    "node_color": list(nx.get_node_attributes(G, 'color').values()),
    "node_size": list(nx.get_node_attributes(G, 'size').values()),
    "edge_color": nx.get_edge_attributes(G, 'sybil_score').values(),
    "width": list(nx.get_edge_attributes(G, 'weight').values()),
    "alpha": 0.4,
    "cmap": plt.cm.PiYG,
    "edge_cmap": plt.cm.PiYG,
    "with_labels": False,
}

fig = plt.figure(figsize=(12, 12))
nx.draw(G, pos, **options)
# fig.set_facecolor('black')
plt.show()
# %%
G.edge
# %%
