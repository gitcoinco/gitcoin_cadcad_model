from env_config import PICKLE_PATH

print("Preparing simulation")
from model.run import run
import cloudpickle
print("Run simuation")
result = run()

print(f"Simulation executed! Pickling result to {PICKLE_PATH}")
with open(PICKLE_PATH, 'wb') as fid:
    cloudpickle.dump(result, fid)
print("Results pickled sucessfuly")