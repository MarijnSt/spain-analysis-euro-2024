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

    # Split location into x and y (swap for vertical pitch)
    df[["x", "y"]] = pd.DataFrame(df["location"].tolist(), index=df.index)
    df[["end_x", "end_y"]] = pd.DataFrame(df["pass_end_location"].tolist(), index=df.index)

    # Categorize pass length (30 metres = 32.8084 yards)
    df["pass_length"] = pd.cut(df["pass_length"], bins=[0, 32.8084, float("inf")], labels=["short", "long"])

    # Pass outcome
    df["pass_outcome"] = df["pass_outcome"].fillna("Complete")


    # Select relevant columns
    cols = [
        "match_id", "team", "player", "position", "x", "y", "end_x", "end_y", "pass_outcome", "pass_length"
    ]

    return df[cols]
