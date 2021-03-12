import cloudpickle
from env_config import PICKLE_PATH, RUN_PARAMS
import os
import click


@click.command()
@click.option('--n', default=None, help="Number of timesteps to process ('all' for doing everything)")
@click.option('--compute_qf', default=None, help="Compute QF. This can be computationally expensive (yes/no)")
def main(n: str, compute_qf: str):
    params = {**RUN_PARAMS}

    if n is not None:
        params['GITCOIN_TIMESTEPS'] = n

    if compute_qf is not None:
        params['GITCOIN_COMPUTE_QF'] = compute_qf

    for (key, value) in params.items():
        os.environ[key] = value

    print("Preparing simulation")
    from model_gitcoin.run import run
    print("Run simuation")
    result = run()

    print(f"Simulation executed! Pickling result to {PICKLE_PATH}")
    with open(PICKLE_PATH, 'wb') as fid:
        cloudpickle.dump(result, fid)
    print("Results pickled sucessfuly")


if __name__ == '__main__':
    main()
