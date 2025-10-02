import pandas as pd
import numpy as np
import logging

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def transform_to_progressive_actions(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform events data to progressive actions.

    Parameters:
    ----------
    events_df: pd.DataFrame
        The events data to transform.

    Returns:
    --------
    df: pd.DataFrame: 
        The transformed progressive actions (passes and carries).
    """

    logger.info(f"Transforming {len(events_df)} records from events data to progressive actions...")

    # Collect passes and carries
    df = events_df[
        (
            (events_df["type"] == "Pass") & (events_df["pass_outcome"].isna()) &
            (events_df["pass_type"] != "Goal Kick") &
            (events_df["pass_type"] != "Corner") &
            (events_df["pass_type"] != "Free Kick") &
            (events_df["pass_type"] != "Throw In")
        ) |
        (events_df["type"] == "Carry")
    ].copy()

    logger.info(f"Found {len(df)} actions (passes and carries).")

    # Combine end locations into one column
    df["end_location"] = np.where(
        df["type"] == "Carry",
        df["carry_end_location"],
        df["pass_end_location"]
    )

    # Split locations into x and y
    df[["x", "y"]] = pd.DataFrame(df["location"].tolist(), index=df.index)
    df[["end_x", "end_y"]] = pd.DataFrame(df["end_location"].tolist(), index=df.index)

    # Calculate progression distance
    df["progression"] = df["end_x"] - df["x"]

    # Filter out actions with progression distance less than 10 yards
    df = df[df["progression"] > 10]

    logger.info(f"Found {len(df)} progressive actions (passes and carries).")

    # Only keep actions in own half
    df = df[df["x"] < 60]

    logger.info(f"Done! Found {len(df)} progressive actions in own half (x < 60).")

    # Select relevant columns
    cols = [
        "id", "match_id", "team", "player", "position", "timestamp",
        "x", "y", "end_x", "end_y", "progression", 
        "type", "under_pressure", "possession",
    ]

    return df[cols]