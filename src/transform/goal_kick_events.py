import pandas as pd
import logging

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def transform_to_goal_kick_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform events data to goal kick events.

    Parameters:
    ----------
    df: pd.DataFrame
        The events data to transform.

    Returns:
    --------
    pd.DataFrame: The transformed goal kick events.
    """

    logger.info(f"Transforming {len(df)} records from events data to goal kick events.")

    # Filter for goal kick events
    df = df[df["pass_type"] == "Goal Kick"].copy()

    # Split location into x and y
    df[["x", "y"]] = pd.DataFrame(df["location"].tolist(), index=df.index)
    df[["end_x", "end_y"]] = pd.DataFrame(df["pass_end_location"].tolist(), index=df.index)

    # Categorize pass length (30 metres = 32.8084 yards)
    df["pass_length"] = pd.cut(df["pass_length"], bins=[0, 32.8084, float("inf")], labels=["short", "long"])

    # Pass outcome
    df["pass_outcome"] = df["pass_outcome"].fillna("Complete")

    logger.info(f"Transformed {len(df)} records from events data to goal kick events.")

    # Select relevant columns
    cols = [
        "match_id", "team", "player", "position", "x", "y", "end_x", "end_y", "pass_outcome", "pass_length"
    ]

    return df[cols]

def transform_to_two_phase_goal_kick_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform events data to two phase events.
    Phase one: goal kick from centre back
    Phase two: next pass

    Parameters:
    ----------
    df: pd.DataFrame
        The events data to transform.

    Returns:
    --------
    pd.DataFrame: The transformed data in two phases (goal kick and next pass).
    """

    logger.info(f"Transforming {len(df)} records from events data to two phase events.")

    # Filter for goal kick events
    df = df[
        (df["play_pattern"] == "From Goal Kick") &
        (df["type"] == "Pass")
    ].copy()

    # Fill pass outcome for first phase (goal kicks are always complete) - DO THIS EARLY
    df['pass_outcome'] = df['pass_outcome'].fillna("Complete")

    # Split location into x and y
    df[["x", "y"]] = pd.DataFrame(df["location"].tolist(), index=df.index)
    df[["end_x", "end_y"]] = pd.DataFrame(df["pass_end_location"].tolist(), index=df.index)

    # Sort by match_id, timestamp, then possession to ensure proper ordering
    df = df.sort_values(['match_id', 'timestamp', 'possession']).reset_index(drop=True)

    # Filter out possession chains that start with a goalkeeper
    # First, identify the first event of each possession chain
    first_events = df.groupby(['match_id', 'possession']).first().reset_index()

    # Get possession IDs that don't start with a goalkeeper
    valid_chains = first_events[first_events['position'] != 'Goalkeeper'][['match_id', 'possession']]
    
    # Filter the original dataframe to only include valid possession chains
    df = df.merge(valid_chains, on=['match_id', 'possession'], how='inner')

    # Keep only the first two events of each possession chain
    df = df.groupby(['match_id', 'possession']).head(2).reset_index(drop=True)

    # Add phase column (first or second pass in the chain)
    df['phase'] = df.groupby(['match_id', 'possession']).cumcount() + 1

    # Drop entire chains where phase 1 is incomplete (no phase 2 will exist)
    # First, identify chains where phase 1 is incomplete
    incomplete_chains = df[(df['phase'] == 1) & (df['pass_outcome'] != 'Complete')][['match_id', 'possession']]
    
    # Remove those entire chains
    df = df[~df.set_index(['match_id', 'possession']).index.isin(incomplete_chains.set_index(['match_id', 'possession']).index)]

    # Recalculate phase numbers after filtering
    df['phase'] = df.groupby(['match_id', 'possession']).cumcount() + 1

    # Categorize pass length for second phase passes (30 metres = 32.8084 yards)
    df['pass_length_category'] = None  # Initialize as object type
    df.loc[df['phase'] == 2, 'pass_length_category'] = pd.cut(
        df.loc[df['phase'] == 2, 'pass_length'], 
        bins=[0, 32.8084, float("inf")], 
        labels=["short", "long"]
    )

    logger.info(f"Transformed {len(df)} records from events data to two phase goal kick events.")

    # Select relevant columns
    cols = [
        "match_id", "team", "player", "position", "timestamp", "possession", "phase",
        "x", "y", "end_x", "end_y", "pass_type", "pass_outcome", "pass_length_category"
    ]

    return df[cols]