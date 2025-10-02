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

    # Only keep events in own half
    df_copy = events_df[events_df["location"].notna()].copy()
    df_copy[["x", "y"]] = pd.DataFrame(df_copy["location"].tolist(), index=df_copy.index)
    df_copy = df_copy[df_copy["x"] < 60]

    # Collect turnovers by type
    type_df = df_copy[
        (df_copy["type"] == "Dispossessed") |
        (df_copy["type"] == "Miscontrol")
    ].copy()

    logger.info(f"Found {len(type_df)} turnovers by type (Dispossessed and Miscontrol).")

    # Collect 50/50s
    fifty_fifty_df = df_copy[
        (df_copy["type"] == "50/50")
    ].copy()

    # Extract outcome from 50/50s
    fifty_fifty_df["50_50"] = fifty_fifty_df["50_50"].apply(
        lambda x: x["outcome"]["name"] if isinstance(x, dict) and "outcome" in x and "name" in x["outcome"] else x
    )

    # Keep turnovers from failed 50/50s
    fifty_fifty_df = fifty_fifty_df[
        (fifty_fifty_df["50_50"] == "Lost") |
        (fifty_fifty_df["50_50"] == "Success To Opposition")
    ]

    logger.info(f"Found {len(fifty_fifty_df)} turnovers from 50/50s.")

    # Collect turnovers from failed passes
    passes_df = df_copy[
        (df_copy["type"] == "Pass") &
        (df_copy["pass_outcome"].notna()) &
        (df_copy["pass_type"] != "Goal Kick") &
        (df_copy["pass_type"] != "Corner") &
        (df_copy["pass_type"] != "Free Kick") &
        (df_copy["pass_type"] != "Throw In") &
        (df_copy["pass_outcome"] != "Injury Clearance")
    ].copy()

    logger.info(f"Found {len(passes_df)} turnovers from passes.")

    # Collect turnovers from incomplete dribbles
    dribbles_df = df_copy[
        (df_copy["dribble_outcome"] == "Incomplete")
    ].copy()

    logger.info(f"Found {len(dribbles_df)} turnovers from dribbles.")

    # Collect turnovers from incomplete ball receipts
    ball_receipts_df = df_copy[
        (df_copy["ball_receipt_outcome"] == "Incomplete")
    ].copy()

    logger.info(f"Found {len(ball_receipts_df)} turnovers from incomplete ball receipts.")

    # Collect turnovers from failed duels when in possession
    duels_df = df_copy[
        (df_copy["type"] == "Duel") &
        (df_copy["team"] == df_copy["possession_team"]) &
        (
            (df_copy["duel_outcome"].isna()) | 
            (df_copy["duel_outcome"] == "Lost") |
            (df_copy["duel_outcome"] == "Lost In Play") |
            (df_copy["duel_outcome"] == "Lost Out")
        )
    ].copy()

    logger.info(f"Found {len(duels_df)} turnovers from duels when in possession.")

    # Combine all turnovers
    df = pd.concat([type_df, fifty_fifty_df, passes_df, dribbles_df, ball_receipts_df, duels_df])

    logger.info(f"Found {len(df)} turnovers.")

    # Filter out duplicates (by id)
    df = df.drop_duplicates(subset=["id"])

    logger.info(f"Filtered out duplicates. {len(df)} turnovers left.")

    # Select relevant columns
    turnover_cols = [
        "id", "match_id", "team", "player", "position", "timestamp", "possession", "possession_team",
        "x", "y",
        "type", 
        "50_50",
        "pass_outcome", "pass_end_location", "pass_type",
        "dribble_outcome",
        "ball_receipt_outcome",
        "duel_type", "duel_outcome",
        "under_pressure", "counterpress",
    ]

    return df[turnover_cols]