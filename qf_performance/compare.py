
# Dependences

import torch
from opt_einsum import contract

import xarray as xr 
import numpy as np 


def generate_data(N_users=5, N_grants=3) -> xr.Dataset:
    """
    Generates random data for testing QF algorithms.

    Output:
    Dataset with {'user', 'grant'} dimensions and
     {'contribution', 'trust'} variables
    """

    # Generates names for the users and grants
    users = [f"u_{i}"
            for i in range(N_users)]

    grants = [f"g_{i}"
            for i in range(N_grants)]

    # Generate contribution between users and grants
    shape = (N_users, N_grants)
    contrib_data = np.random.randn(*shape)
    contributions = xr.DataArray(contrib_data, 
                    coords=[users, grants],
                    dims=['user', 'grant'])
    contributions.name ='contribution'

    # Generate user trust vector
    trust = xr.DataArray(np.random.randn(N_users),
                        coords=[users],
                        dims=['user'])
    trust.name = 'trust'

    # Merge and return
    ds = xr.merge([contributions, trust])
    return ds


def pairwise_clr_match(contribs: torch.tensor,
                       trust: torch.tensor,
                       m: float) -> torch.tensor:
  """
  Arguments
  contribs: array of shape (N_proj, N_user)
  trust: array of shape (N_user,)
  m: number

  Output
  subsidies: array of shape (N_project, )
  """
  participant_overlap = contract('up,pv->uv', contribs.t().sqrt(), contribs.sqrt())
  k = m / (m+participant_overlap)
  # No self-subsidy
  k.fill_diagonal_(0)

  # Mysterious term
  obj_1 = trust.repeat(trust.size()[0],1)
  obj_2 = trust.repeat(trust.size()[0],1).t()
  complicated_obj: tuple = (obj_1, obj_2)
  max_pairwise_trust : float = torch.max(*complicated_obj)

  # To use sparse, we're either going to have to use something like pytaco, which can handle sparse einsum
  # or else break this down row by row, take the outer product, and sum.
  subsidies = contract('pu,uv,uv,pv->p',contribs.sqrt(), k, max_pairwise_trust, contribs.sqrt())
  return subsidies

M = 1
ALGORITHMS = [pairwise_clr_match]

ds = generate_data()


results = {}
for algo in ALGORITHMS:
    match_per_grant = algo(ds.contribution, ds.trust, M)
    name = algo.__name__
    results[name] = match_per_grant

