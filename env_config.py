import os

PICKLE_PATH = "model/data/simulation_result.pkl.gz"

# 'yes' for loading the data contained in the 'data/alternate_data/xls' file.
# 'no' for loading from the query result data.
os.environ['GITCOIN_LOAD_EXCEL'] = 'no'

# Set to 'all' for doing all timesteps
# Set to a integer for doing just the first N timesteps
os.environ['GITCOIN_TIMESTEPS'] = str(6000) 
