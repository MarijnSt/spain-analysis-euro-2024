import pandas as pd
import logging

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def calculate_shots_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the statistics for the shots.

    Parameters:
    ----------
    df: pd.DataFrame
        The shots dataframe.

    Returns:
    --------
    df: pd.DataFrame
        The statistics for the shots.
    """

    logger.info(f"Calculating statistics for shots.")

    # Get all teams first
    all_teams = df["team"].unique()

    # Shots from set piece or open play
    shots_from_set_piece = df[df["shot_from_set_piece"]].groupby("team").size().reindex(all_teams, fill_value=0)
    shots_from_open_play = df[~df["shot_from_set_piece"]].groupby("team").size().reindex(all_teams, fill_value=0)
    shots_from_set_piece_percentage = (shots_from_set_piece / (shots_from_set_piece + shots_from_open_play)).fillna(0) * 100
    shots_from_open_play_percentage = (shots_from_open_play / (shots_from_set_piece + shots_from_open_play)).fillna(0) * 100

    # xG from set piece or open play
    xg_from_set_piece = df[df["shot_from_set_piece"]].groupby("team")["shot_statsbomb_xg"].sum().reindex(all_teams, fill_value=0)
    xg_from_open_play = df[~df["shot_from_set_piece"]].groupby("team")["shot_statsbomb_xg"].sum().reindex(all_teams, fill_value=0)
    xg_from_set_piece_percentage = (xg_from_set_piece / (xg_from_set_piece + xg_from_open_play)).fillna(0) * 100
    xg_from_open_play_percentage = (xg_from_open_play / (xg_from_set_piece + xg_from_open_play)).fillna(0) * 100

    # Create DataFrame
    result_df = pd.DataFrame({
        "team": all_teams,
        "shots_from_set_piece": shots_from_set_piece,
        "shots_from_open_play": shots_from_open_play,
        "shots_from_set_piece_percentage": shots_from_set_piece_percentage,
        "shots_from_open_play_percentage": shots_from_open_play_percentage,
        "xg_from_set_piece": xg_from_set_piece,
        "xg_from_open_play": xg_from_open_play,
        "xg_from_set_piece_percentage": xg_from_set_piece_percentage,
        "xg_from_open_play_percentage": xg_from_open_play_percentage
    })

    return result_df.reset_index(drop=True)