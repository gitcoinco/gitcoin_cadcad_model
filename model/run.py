import pandas as pd
#from .parts.utils import * 
from model import config 
from cadCAD.engine import ExecutionMode, ExecutionContext,Executor
from cadCAD import configs

def run():
    '''
    Definition:
    Run simulation
    Parameters:
    input_config: Optional way to pass in system configuration
    '''
    exec_mode = ExecutionMode()
    local_mode_ctx = ExecutionContext(context=exec_mode.local_mode)
    simulation = Executor(exec_context=local_mode_ctx, configs=configs)
    raw_system_events, tensor_field, sessions = simulation.execute()
    df = (pd.DataFrame(raw_system_events))
    # Clean substeps
    first_ind = (df.substep == 0) & (df.timestep == 0)
    last_ind = df.substep == max(df.substep)
    inds_to_drop = (first_ind | last_ind)
    df = df.loc[inds_to_drop].drop(columns=['substep'])

    # Set indexes
    df = df.set_index(['simulation', 'subset', 'run', 'timestep'])
    return df