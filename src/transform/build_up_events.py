import pandas as pd
import numpy as np
import logging

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def transform_to_build_up_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform events data in two dataframes:
    - First events: goal kicks
    - Chain events: two first events (passes or carries) from build ups that don't start with the goalkeeper

    Parameters:
    ----------
    df: pd.DataFrame
        The events data to transform.

    Returns:
    --------
    first_events_df: pd.DataFrame
        The transformed first events dataframe.
    chain_events_df: pd.DataFrame
        The transformed chain events dataframe.
    """

    logger.info(f"Transforming {len(df)} records from events data to two phase events.")

    # Filter for goal kick chains and keep passes
    df = df[
        (df["play_pattern"] == "From Goal Kick") &
        (df["type"] == "Pass")
    ].copy()

    # Sort by match_id and timestamp to ensure proper ordering
    df = df.sort_values(['match_id', 'timestamp']).reset_index(drop=True)

    logger.info(f"Filtered {len(df)} records from events data to goal kick chains.")

    # Initialize list of first events and chain events
    first_events = []
    chain_events = []

    # Loop through each match_id
    for match_id in df["match_id"].unique():
        # Filter for current match_id
        match_df = df[df["match_id"] == match_id]
        
        # Loop through possession chain
        for possession in match_df["possession"].unique():
            chain_df = match_df[match_df["possession"] == possession].copy()

            # Skip if chain is empty
            if len(chain_df) == 0:
                continue

            # Skip if chain does not start with a Goal Kick
            if chain_df["pass_type"].iloc[0] != "Goal Kick":
                continue

            # Split locations
            chain_df[["x", "y"]] = pd.DataFrame(chain_df["location"].tolist(), index=chain_df.index)
            chain_df[["end_x", "end_y"]] = pd.DataFrame(chain_df["pass_end_location"].tolist(), index=chain_df.index)

            # Categorize pass length (30 metres = 32.8084 yards)
            chain_df["pass_category"] = pd.cut(
                chain_df["pass_length"], 
                bins=[0, 32.8084, float("inf")], 
                labels=["short", "long"]
            )

            # Add phase column to chain
            chain_df["phase"] = 1

            # Add first event to list
            first_events.append(chain_df.iloc[0:1])

            # Skip chain if it doesn't match the pattern we want
            if (
                len(chain_df) < 2 or                                # Skip if there are less than two events in the chain
                chain_df.iloc[0]["position"] == "Goalkeeper" or     # Skip if the first pass is from the goalkeeper
                pd.notna(chain_df.iloc[0]["pass_outcome"])            # Skip if the first pass is incomplete
            ):
                continue

            # Set phase column to 2 for second event
            chain_df.at[chain_df.index[1], "phase"] = 2

            # Add first two events of chain to list
            chain_events.append(chain_df[0:2])
    
    # Combine lists into dataframes
    first_events_df = pd.concat(first_events, ignore_index=True)
    chain_events_df = pd.concat(chain_events, ignore_index=True)

    # Sort by match_id and timestamp
    first_events_df = first_events_df.sort_values(['match_id', 'timestamp']).reset_index(drop=True)
    chain_events_df = chain_events_df.sort_values(['match_id', 'timestamp']).reset_index(drop=True)

    logger.info(f"Transformed {len(first_events_df)} records from events data to first events dataframe.")
    logger.info(f"Transformed {len(chain_events_df)} records from events data to chain events dataframe.")

    # Select relevant columns
    cols = [
        "match_id", "team", "player", "position", "timestamp", "possession", "type", "phase",
        "x", "y", "end_x", "end_y", "pass_type", "pass_outcome", "pass_category"
    ]

    # Return dataframes
    return first_events_df[cols], chain_events_df[cols]