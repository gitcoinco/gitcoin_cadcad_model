
# %% [markdown]
# # Generating Gitcoin Grants Network through cadCAD
#

# %%
import numpy as np
from cadCAD import configs
from cadCAD.configuration.utils import bound_norm_random, ep_time_step, config_sim, access_block
from cadCAD.configuration import Experiment
from cadCAD.engine import Executor, ExecutionMode, ExecutionContext
import networkx as nx
import pandas as pd
import numpy as np
import json
from typing import List, Tuple, Dict
from collections import defaultdict

# %%


def load_edges() -> dict:
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
    sorted_df = df.sort_values('created_on').head(100)
    timesteps = range(len(sorted_df))
    src = sorted_df.profile_for_clr_id.values
    dst = sorted_df.title.values
    return {i + 1: (src[i], dst[i]) for i in timesteps}


EDGE_PER_TIMESTEP: dict = load_edges()

unique_users = set(src for (src, dst) in EDGE_PER_TIMESTEP.values()) 
unique_grants = set(dst for (src, dst) in EDGE_PER_TIMESTEP.values())
N_users = len(unique_users)
N_grants = len(unique_grants)

genesis_states = {
    'network': nx.DiGraph(),
    'pair_totals': defaultdict(lambda: defaultdict(0.0)),
    'user_totals': defaultdict(0.0),
    'total_pot': 0.0,
    'quadratic_match': defaultdict(0.0)
}


sys_params = {
    'edge_per_timestep': [EDGE_PER_TIMESTEP],
    'trust_per_user': [None],
    'v_threshold': None,
}


def p_new_contribution(params, substep, state_history, prev_state):
    timestep: int = len(state_history)
    timestep_edge: tuple = params['edge_per_timestep'][timestep]

    new_contribution = {'amount': None,
                        'contributor': timestep_edge[0],
                        'grant': timestep[1]}
    new_contributions = [new_contribution]
    return {'new_contributions': []}


def s_append_edges(params, substep, state_history, prev_state, policy_input):
    # Dependences
    G = prev_state['network'].copy()
    for contribution in policy_input['new_contributions']:
        G.add_edge(contribution['contributor'], contribution['grant'])
    return ('network', G)


def s_pair_totals(params, substep, state_history, prev_state, policy_input):
    pair_totals = prev_state['pair_totals']
    for contribution in policy_input['new_contributions']:
        pass
    return ('pair_totals', None)


def s_total_pot(params, substep, state_history, prev_state, policy_input):
    pass


def s_quadratic_match(params, substep, state_history, prev_state, policy_input):
    total_pot = params['total_pot']

    total_match = None

    quadratic_match = {}
    for grant in grants:



        if total_match > total_pot:
            grant_funding = total_pot * grant_match / total_match
        else:
            grant_funding = grant_match
            grant_funding *= (1 + np.log(total_pot / total_match) / 100)
        quadratic_match[grant] = grant_funding

    return ('quadratic_match', quadratic_match)


partial_state_update_blocks = [
    {
        'label': 'Append new edges to the network',
        'policies': {
            'new_contribution': p_new_contribution
        },
        'variables': {
            'network': s_append_edges,
            'pair_totals': s_pair_totals,
        },
    },
    {
        'label': 'Funding mechanisms',
        'policies': {

        },
        'variables': {
            'quadratic_match': s_quadratic_match
        }
    }
]


sim_params = {
    'N': 1,
    'T': range(len(EDGE_PER_TIMESTEP)),
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
nx.draw(result.reset_index().iloc[0].network)
# %%
nx.draw(result.reset_index().iloc[10].network)
# %%
nx.draw(result.reset_index().iloc[-1].network)

# %%
