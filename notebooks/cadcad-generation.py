
# %% [markdown]
# # Generating Gitcoin Grants Network through cadCAD
#

# %%
from cadCAD.configuration.utils import bound_norm_random, ep_time_step, config_sim, access_block
from cadCAD.configuration import Experiment
from cadCAD.engine import Executor, ExecutionMode, ExecutionContext
import networkx as nx
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict

# %%
EDGE_PER_TIMESTEP: Dict[int, Tuple[str, str]] = {1: (0, 1),
                                                 2: (0, 2),
                                                 3: (1, 5)}


genesis_states = {
    'network': nx.Graph()
}


sys_params = {
    'edge_per_timestep': [EDGE_PER_TIMESTEP, EDGE_PER_TIMESTEP.copy()]
}


def s_append_edges(params, substep, state_history, prev_state, policy_input):
    # Dependences
    timestep: int = len(state_history)
    timestep_edge: tuple = params['edge_per_timestep'][timestep]
    G = prev_state['network'].copy()

    # SUF logic
    G.add_edge(*timestep_edge)
    return ('network', G)


partial_state_update_blocks = [
    {
        'label': 'Append new edges to the network',
        'policies': {
            'test': None

        },
        'variables': {
            'network': s_append_edges

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

from cadCAD import configs
result = run(configs)

# %%
configs[1].sim_config['M']['edge_per_timestep']
# %%
result
# %%
result.query('timestep == 2 & subset == 0').reset_index().network[0].edges
# %%

# %%
