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

def transform_to_turnovers(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform events data to turnovers data.

    Parameters:
    ----------
    events_df: pd.DataFrame
        The events data to transform.

    Returns:
    --------
    df: pd.DataFrame: 
        The transformed turnovers data.
    """

    logger.info(f"Transforming {len(events_df)} records from events data to turnovers data...")

    # Filter to own half once
    df = events_df[events_df["location"].notna()].copy()
    df[["x", "y"]] = pd.DataFrame(df["location"].tolist(), index=df.index)
    df = df[df["x"] < 60]

    # Create boolean masks for different turnover types
    type_mask = (df["type"] == "Dispossessed") | (df["type"] == "Miscontrol")
    
    fifty_fifty_mask = (df["type"] == "50/50")
    
    pass_mask = (
        (df["type"] == "Pass") &
        (df["pass_outcome"].notna()) &
        (df["pass_type"] != "Goal Kick") &
        (df["pass_type"] != "Corner") &
        (df["pass_type"] != "Free Kick") &
        (df["pass_type"] != "Throw In") &
        (df["pass_outcome"] != "Injury Clearance")
    )
    
    dribble_mask = (df["dribble_outcome"] == "Incomplete")
    
    ball_receipt_mask = (df["ball_receipt_outcome"] == "Incomplete")
    
    duel_mask = (
        (df["type"] == "Duel") &
        (df["team"] == df["possession_team"]) &
        (
            (df["duel_outcome"].isna()) | 
            (df["duel_outcome"] == "Lost") |
            (df["duel_outcome"] == "Lost In Play") |
            (df["duel_outcome"] == "Lost Out")
        )
    )

    # Combine all masks
    turnover_mask = type_mask | fifty_fifty_mask | pass_mask | dribble_mask | ball_receipt_mask | duel_mask
    
    # Filter turnovers
    df = df[turnover_mask].copy()
    
    # Handle 50/50 events
    df.loc[fifty_fifty_mask, "50_50"] = df.loc[fifty_fifty_mask, "50_50"].apply(
        lambda x: x["outcome"]["name"] if isinstance(x, dict) and "outcome" in x and "name" in x["outcome"] else x
    )
    
    # Filter 50/50s to only lost ones
    df = df[~fifty_fifty_mask | ((df["type"] == "50/50") & ((df["50_50"] == "Lost") | (df["50_50"] == "Success To Opposition")))]

    logger.info(f"Found {len(df)} turnovers.")

    # Remove duplicates
    df = df.drop_duplicates(subset=["id"])

    logger.info(f"Filtered out duplicates. {len(df)} turnovers left.")

    # Select relevant columns
    turnover_cols = [
        "id", "match_id", "team", "player", "position", "timestamp", "possession", "possession_team",
        "x", "y", "type", "50_50", "pass_outcome", "pass_end_location", "pass_type",
        "dribble_outcome", "ball_receipt_outcome", "duel_type", "duel_outcome",
        "under_pressure", "counterpress"
    ]

    return df[turnover_cols]