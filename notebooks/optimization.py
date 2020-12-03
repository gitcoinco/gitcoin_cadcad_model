# %%
import numpy as np
import pandas as pd
import numpy as np
import json
import xarray as xr
import xarray
(get_ipython().run_line_magic("load_ext", "autotime"))

LIMIT_SEQUENCE = None  # pass None to get everything


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
                      )

    event_sequence.index = event_sequence.index.rename('sequence')

    return event_sequence


# %%

event_df = load_contributions_sequence()
# %%
ds = (xr.Dataset
        .from_dataframe(event_df)
        .set_coords(['contributor', 'grant']))
# %%
from tqdm.auto import tqdm


# %%
# %%


def aggregate_contributions(grant_contributions):
    contrib_dict = {}
    for user, proj, amount in grant_contributions:
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
    return proj_total


threshold = 0.3
contrib_dict = aggregate_contributions(event_df.values)
pair_totals = get_totals_by_pair(contrib_dict)
proj_clrs = {proj: match_project(contribz, pair_totals, threshold)
             for proj, contribz in contrib_dict.items()}
# %%
# %%
1502 * 1502
# %%
# %%
