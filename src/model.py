import numpy as np
from cadCAD.engine import ExecutionContext, ExecutionMode, Executor
from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment
from collections import defaultdict
import pandas as pd
from typing import DefaultDict
from src.utils import load_contributions_sequence


CONTRIBUTIONS_SEQUENCE: dict = load_contributions_sequence()

genesis_states = {
    # 'network': nx.DiGraph(),
    'contributions': [],
    # (N_user, N_user)
    'pair_totals': defaultdict(lambda: DefaultDict(lambda: 0.0)),
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
    'total_pot': [450000]
}


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


