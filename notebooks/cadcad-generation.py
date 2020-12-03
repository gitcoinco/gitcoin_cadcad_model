
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
from time import time
import logging
from functools import wraps
logging.basicConfig(level=logging.DEBUG)


def print_time(f):
    """

    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Current timestep
        t = len(args[2])
        t1 = time()
        f_out = f(*args, **kwargs)
        t2 = time()
        text = f"{t}|{f.__name__}  (exec time: {t2 - t1:.2f}s)"
        logging.debug(text)
        return f_out
    return wrapper
# %%


LIMIT_SEQUENCE = 200  # pass None to get everything


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
                          'amount_per_period_usdt': 'amount'}

    event_sequence = (sorted_df.rename(columns=event_property_map)
                      .loc[:, event_property_map.values()]
                      .reset_index(drop=True)
                      .to_dict(orient='index')
                      )

    return event_sequence


# %%

CONTRIBUTIONS_SEQUENCE: dict = load_contributions_sequence()
unique_users = {c['contributor'] for c in CONTRIBUTIONS_SEQUENCE}
unique_grants = {c['grant'] for c in CONTRIBUTIONS_SEQUENCE}

genesis_states = {
    'network': nx.DiGraph(),
    'contributions': [],
    # (N_user, N_user)
    'pair_totals': np.zeros((N_users, N_users)),
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


def s_pair_totals(params, substep, state_history, prev_state, policy_input):
    # Dependences
    pair_totals = prev_state['pair_totals'].copy()
    contributions = prev_state['contributions']
    new_contribution = policy_input['new_contribution']

    new_amount = new_contribution['amount']
    new_user = new_contribution['contributor']

    # Logic
    for c in contributions:
        (i, j) = sorted([new_user, c['contributor']])
        pair_totals[i][j] += np.lib.scimath.sqrt(new_amount * c['amount'])
    return ('pair_totals', pair_totals)


# %%
x = np.array([1, 2, 3])
np.outer(x, x)
# %%


@print_time
def p_quadratic_match(params, substep, state_history, prev_state):
    k = params['v_threshold']
    total_pot = params['total_pot']
    T = params['trust_bonus_per_user']
    pair_totals = prev_state['pair_totals']
    contributions = prev_state['contributions']

    grants = {c['grant'] for c in contributions}
    M = defaultdict(lambda: 0.0)
    for grant in grants:
        grant_contributions = [c
                               for c in contributions
                               if c['grant'] == grant]

        amounts = np.array(c['amount'] for c in grant_contributions])
        users = np.array(c['contributor' for c in grant_contributions])
        C = np.outer(grant_contributions, grant_contributions).tril()



        for (i, c_i) in enumerate(grant_contributions):
            v_i = c_i['amount']
            u_i = c_i['contributor']
            for (j, c_j) in enumerate(grant_contributions):
                v_j = c_j['amount']
                u_j = c_j['contributor']
                if i > j:
                    (u_i, u_j) = sorted([u_i, u_j])
                    trust_bonus = max([T[u_i], T[u_j]])
                    cross_contribution = np.lib.scimath.sqrt(max(v_i * v_j, 0))
                    user_covariance = 1 + pair_totals[u_i][u_j]
                    partial_match = trust_bonus * cross_contribution
                    partial_match *= k
                    partial_match /= user_covariance
                    M[grant] += partial_match

                else:
                    continue

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
            'pair_totals': s_pair_totals,
            'contributions': s_append_contribution
        },
    },
    {
        'label': 'Quadratic Funding',
        'policies': {
            'quadratic_match': p_quadratic_match
        },
        'variables': {
            # 'quadratic_match_per_grant': s_quadratic_match_per_grant,
            # 'quadratic_funding_per_grant': s_quadratic_funding_per_grant,
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
