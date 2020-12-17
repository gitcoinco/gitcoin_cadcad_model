import click
import pandas as pd
import json
from cape_privacy.pandas import transformations as tfms


def parse_grants_data(input_csv_path: str, output_csv_path: str=None) -> pd.DataFrame:
    """
    Clean the Gitcoin Rounds data for privacy and 
    ease of the use in the simulation.
    """
    raw_df = pd.read_csv(input_csv_path)

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

    # Columns which are to keep into the dynamical network
    event_property_map = {'profile_for_clr_id': 'contributor',
                          'title': 'grant',
                          'amount_per_period_usdt': 'amount'}

    # Prepare tokenizer
    tokenize_contributor = tfms.Tokenizer(max_token_len=10)

    # Create a dict in the form {ts: {**event_attrs}}
    event_df = (sorted_df.rename(columns=event_property_map)
                         .loc[:, event_property_map.values()]
                         .reset_index(drop=True)
                         .reset_index()
                         .rename(columns={'index': 'time_sequence'})
                         .assign(contributor=lambda df: tokenize_contributor(df.contributor.astype(str)))
                         .assign(flag=0)
                      )
    
    if output_csv_path is not None:
        event_df.to_csv(output_csv_path, index=False, compression='xz')
        
    return event_df

@click.command()
@click.option('--src', default=None, help='Path for the input raw data (eg. raw_data/gc_round_7.csv)')
@click.option('--dst', default=None, help='Path for the output clean data: (eg. model/data/OUTPUT.csv.xz)')
def main(src, dst):
    if src is None or dst is None:
        print("Paths must be provided in order to continue")
    else:
        parse_grants_data(src, dst)


if __name__ == '__main__':
    main()