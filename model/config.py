from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment

from .state_variables import initial_states
from .sys_params import sys_params
from .sys_params import CONTRIBUTIONS_SEQUENCE
from .partial_state_update_block import partial_state_update_blocks

sim_params = {
    'N': 1,
    'T': range(len(CONTRIBUTIONS_SEQUENCE)),
    'M': sys_params
}

sim_config = config_sim(sim_params)

exp = Experiment()
exp.append_configs(sim_configs=sim_config,
                   initial_state=initial_states,
                   partial_state_update_blocks=partial_state_update_blocks)