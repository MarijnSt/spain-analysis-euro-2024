import pandas as pd
import logging

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)


def calculate_gk_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the statistics for the goal kicks.

    Parameters:
    ----------
    df: pd.DataFrame
        All goal kicks in the dataset.

    Returns:
    --------
    pd.DataFrame: The statistics for the goal kicks per team.
    """

    logger.info(f"Calculating statistics for goal kicks.")

    # Get all teams first
    all_teams = df["team"].unique()
    
    # Calculate completed passes (use size(), reindex and fill empty values)
    completed_short = df[df["pass_outcome"] == "Complete"][df["pass_length"] == "short"].groupby("team").size().reindex(all_teams, fill_value=0)
    completed_long = df[df["pass_outcome"] == "Complete"][df["pass_length"] == "long"].groupby("team").size().reindex(all_teams, fill_value=0)

    # Calculate incomplete passes
    incomplete_short = df[df["pass_outcome"] != "Complete"][df["pass_length"] == "short"].groupby("team").size().reindex(all_teams, fill_value=0)
    incomplete_long = df[df["pass_outcome"] != "Complete"][df["pass_length"] == "long"].groupby("team").size().reindex(all_teams, fill_value=0)

    # Calculate total and percentages
    total_short = completed_short + incomplete_short
    total_long = completed_long + incomplete_long
    total = total_short + total_long

    # Calculate percentages (handle division by zero)
    short_percentage = (total_short / total) * 100
    long_percentage = (total_long / total) * 100
    completed_short_percentage = (completed_short / total_short).replace([float('inf'), -float('inf')], 0) * 100
    completed_long_percentage = (completed_long / total_long).replace([float('inf'), -float('inf')], 0) * 100
    incomplete_short_percentage = (incomplete_short / total_short).replace([float('inf'), -float('inf')], 0) * 100
    incomplete_long_percentage = (incomplete_long / total_long).replace([float('inf'), -float('inf')], 0) * 100

    # Create DataFrame
    result_df = pd.DataFrame({
        "team": all_teams,
        "total_passes": total,
        "short_percentage": short_percentage.round(0),
        "long_percentage": long_percentage.round(0),
        "short_passes": total_short,
        "completed_short_passes": completed_short,
        "incomplete_short_passes": incomplete_short,
        "completed_short_percentage": completed_short_percentage.round(0),
        "incomplete_short_percentage": incomplete_short_percentage.round(0),
        "long_passes": total_long,
        "completed_long_passes": completed_long,
        "incomplete_long_passes": incomplete_long,
        "completed_long_percentage": completed_long_percentage.round(0),
        "incomplete_long_percentage": incomplete_long_percentage.round(0),
    })

    # Convert all columns except 'team' to int
    result_df = result_df.astype({col: int for col in result_df.columns if col != 'team'})

    return result_df.reset_index(drop=True)