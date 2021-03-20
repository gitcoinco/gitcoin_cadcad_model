import os

PICKLE_PATH = "data/model_results/simulation_result.pkl.gz"

RUN_PARAMS = {}

# 'yes' for loading the data contained in the 'data/alternate_data/xls' file.
# 'no' for loading from the query result data.
RUN_PARAMS['GITCOIN_LOAD_EXCEL'] = 'no'

# Set to 'all' for doing all timesteps
# Set to a integer for doing just the first N timesteps
RUN_PARAMS['GITCOIN_TIMESTEPS'] = str(100) 


# Set to 'no' for not computing the QF match algorithm
# This can save a lot of execute time
RUN_PARAMS['GITCOIN_COMPUTE_QF'] = 'yes'