import pandas as pd
import numpy as np
import logging
from src.config import config

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def transform_to_box_entry_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform events data to box entry events.

    Parameters:
    ----------
    df: pd.DataFrame
        The events data to transform.

    Returns:
    --------
    df: pd.DataFrame
        The transformed box entry events.
    """

    logger.info(f"Transforming {len(df)} records from events data to box entry events.")

    # Filter for passes and carries
    df = df[df["type"].isin(["Pass", "Carry"])].copy()

    logger.info(f"Found {len(df)} passes and carries.")

    # Set end location
    df["end_location"] = np.where(
        df["type"] == "Carry",
        df["carry_end_location"],
        df["pass_end_location"]
    )

    # Split locations
    df[["x", "y"]] = pd.DataFrame(df["location"].tolist(), index=df.index)
    df[["end_x", "end_y"]] = pd.DataFrame(df["end_location"].tolist(), index=df.index)

    # Filter out events that don't start on the opponent's half
    df = df[df["x"] >= 60]

    # Filter out events that don't end in the box
    df = df[
        (df["end_x"] >= 102) &
        (df["end_y"] >= 18) &
        (df["end_y"] <= 62)
    ]

    logger.info(f"Found {len(df)} box entry events.")

    # Classify box entry origin
    df["box_entry_from_set_piece"] = df.apply(
        lambda x: classify_box_entry_from_set_piece(df, x), axis=1
    )

    logger.info(f"Box entry events from set piece: {len(df[df['box_entry_from_set_piece']])}")
    logger.info(f"Box entry events from open play: {len(df[~df['box_entry_from_set_piece']])}")

    # Select relevant columns
    box_entry_cols = [
        "id","match_id", "team", "player", "location", "timestamp", "possession", "type", "x", "y", "end_x", "end_y", "box_entry_from_set_piece",
    ]

    return df[~df["box_entry_from_set_piece"]][box_entry_cols]

def classify_box_entry_from_set_piece(
    events_df: pd.DataFrame, 
    entry_event: pd.Series
) -> bool:
    """
    Classify if a box entry comes from a set piece based on time OR action count

    Parameters:
    ----------
    events_df: pd.DataFrame
        The events data to classify.
    entry_event: pd.Series
        The box entry event to classify.

    Returns:
    --------
    bool:
        True if the box entry comes from a set piece, False otherwise.
    """
    match_id = entry_event['match_id']
    possession = entry_event['possession']
    
    # Get all events in the same possession
    possession_events = events_df[
        (events_df['match_id'] == match_id) & 
        (events_df['possession'] == possession)
    ].sort_values('timestamp')
    
    # Find the first event (set piece origin)
    first_event = possession_events.iloc[0]
    
    # Get events up to and including this specific shot
    events_up_to_entry = possession_events[
        possession_events['timestamp'] <= entry_event['timestamp']
    ]
    
    # Calculate time elapsed (in seconds)
    first_time = pd.to_timedelta(first_event['timestamp']).total_seconds()
    entry_time = pd.to_timedelta(entry_event['timestamp']).total_seconds()
    time_elapsed = entry_time - first_time
    
    # Count possessing actions (passes, carries, dribbles) up to this shot
    possessing_actions = events_up_to_entry[
        events_up_to_entry['type'].isin(['Pass', 'Carry', 'Dribble'])
    ]
    actions_between = len(possessing_actions)
    
    # Apply hybrid cutoffs based on play_pattern
    play_pattern = first_event['play_pattern']
    
    if play_pattern in ["From Corner", "From Free Kick", "From Throw In"]:
        return (time_elapsed <= config.classification.set_piece_allowed_time) or (actions_between <= config.classification.set_piece_allowed_actions)
    else:
        return False