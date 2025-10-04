import pandas as pd
import numpy as np
import logging

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def transform_to_shot_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform events data to shot events.

    Parameters:
    ----------
    df: pd.DataFrame
        The events data to transform.

    Returns:
    --------
    df: pd.DataFrame
        The transformed shot events.
    """

    logger.info(f"Transforming {len(df)} records from events data to shot events.")

    # Filter for shot events
    df = df[df["type"] == "Shot"].copy()

    # Classify shot origin
    df["shot_from_set_piece"] = df.apply(
        lambda x: classify_shot_from_set_piece(df, x), axis=1
    )

    logger.info(f"Transformed {len(df)} records from events data to shot events.")
    logger.info(f"Shots from set piece: {len(df[df['shot_from_set_piece']])}")
    logger.info(f"Shots from open play: {len(df[~df['shot_from_set_piece']])}")

    # Select relevant columns
    shot_cols = [
        "match_id", "team", "player", "location", "timestamp", "possession", "type", "play_pattern", "shot_from_set_piece", "shot_type", "shot_aerial_won", "shot_body_part", "shot_end_location", "shot_first_time", "shot_follows_dribble", 
        "shot_one_on_one", "shot_outcome", "shot_redirect", "shot_saved_off_target", "shot_saved_to_post", "shot_statsbomb_xg", "shot_technique"
    ]

    return df[shot_cols]

def classify_shot_from_set_piece(
    events_df: pd.DataFrame, 
    shot_event: pd.Series
) -> bool:
    """
    Classify if a shot comes from a set piece based on time OR action count
    """
    match_id = shot_event['match_id']
    possession = shot_event['possession']
    
    # Get all events in the same possession
    possession_events = events_df[
        (events_df['match_id'] == match_id) & 
        (events_df['possession'] == possession)
    ].sort_values('timestamp')
    
    # Find the first event (set piece origin)
    first_event = possession_events.iloc[0]
    
    # Get events up to and including this specific shot
    events_up_to_shot = possession_events[
        possession_events['timestamp'] <= shot_event['timestamp']
    ]
    
    # Calculate time elapsed (in seconds)
    first_time = pd.to_timedelta(first_event['timestamp']).total_seconds()
    shot_time = pd.to_timedelta(shot_event['timestamp']).total_seconds()
    time_elapsed = shot_time - first_time
    
    # Count possessing actions (passes, carries, dribbles) up to this shot
    possessing_actions = events_up_to_shot[
        events_up_to_shot['type'].isin(['Pass', 'Carry', 'Dribble'])
    ]
    actions_between = len(possessing_actions)
    
    # Apply hybrid cutoffs based on play_pattern
    play_pattern = first_event['play_pattern']
    
    if play_pattern in ["From Corner", "From Free Kick", "From Throw In"]:
        return (time_elapsed <= 10) or (actions_between <= 5)
    else:
        return False