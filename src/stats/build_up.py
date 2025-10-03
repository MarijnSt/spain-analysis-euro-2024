import pandas as pd
import logging

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)


def calculate_build_up_stats(
    first_events_df: pd.DataFrame,
    chain_events_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate the statistics for the build up.

    Parameters:
    ----------
    first_events_df: pd.DataFrame
        The first events dataframe.
    chain_events_df: pd.DataFrame
        The chain events dataframe.

    Returns:
    --------
    pd.DataFrame: The statistics for the build up.
    """

    logger.info(f"Calculating statistics for build up.")

    # Get all teams first
    all_teams = first_events_df["team"].unique()
    
    # First phase
    first_phase_completed_short = first_events_df[
        (first_events_df["pass_outcome"].isna()) &
        (first_events_df["pass_category"] == "short")
    ].groupby("team").size().reindex(all_teams, fill_value=0)

    first_phase_completed_long = first_events_df[
        (first_events_df["pass_outcome"].isna()) &
        (first_events_df["pass_category"] == "long")
    ].groupby("team").size().reindex(all_teams, fill_value=0)

    first_phase_incomplete_short = first_events_df[
        (first_events_df["pass_outcome"].notna()) &
        (first_events_df["pass_category"] == "short")
    ].groupby("team").size().reindex(all_teams, fill_value=0)

    first_phase_incomplete_long = first_events_df[
        (first_events_df["pass_outcome"].notna()) &
        (first_events_df["pass_category"] == "long")
    ].groupby("team").size().reindex(all_teams, fill_value=0)

    first_phase_total_short = first_phase_completed_short + first_phase_incomplete_short
    first_phase_total_long = first_phase_completed_long + first_phase_incomplete_long
    first_phase_total = first_phase_total_short + first_phase_total_long

    first_phase_short_percentage = (first_phase_total_short / first_phase_total).fillna(0) * 100
    first_phase_long_percentage = (first_phase_total_long / first_phase_total).fillna(0) * 100
    first_phase_completed_short_percentage = (first_phase_completed_short / first_phase_total_short).replace([float('inf'), -float('inf')], 0).fillna(0) * 100
    first_phase_completed_long_percentage = (first_phase_completed_long / first_phase_total_long).replace([float('inf'), -float('inf')], 0).fillna(0) * 100
    first_phase_incomplete_short_percentage = (first_phase_incomplete_short / first_phase_total_short).replace([float('inf'), -float('inf')], 0).fillna(0) * 100
    first_phase_incomplete_long_percentage = (first_phase_incomplete_long / first_phase_total_long).replace([float('inf'), -float('inf')], 0).fillna(0) * 100

    # Second phase
    second_phase_completed_short = chain_events_df[
        (chain_events_df["pass_outcome"].isna()) &
        (chain_events_df["pass_category"] == "short") &
        (chain_events_df["phase"] == 2)
    ].groupby("team").size().reindex(all_teams, fill_value=0)

    second_phase_completed_long = chain_events_df[
        (chain_events_df["pass_outcome"].isna()) &
        (chain_events_df["pass_category"] == "long") &
        (chain_events_df["phase"] == 2)
    ].groupby("team").size().reindex(all_teams, fill_value=0)

    second_phase_incomplete_short = chain_events_df[
        (chain_events_df["pass_outcome"].notna()) &
        (chain_events_df["pass_category"] == "short") &
        (chain_events_df["phase"] == 2)
    ].groupby("team").size().reindex(all_teams, fill_value=0)

    second_phase_incomplete_long = chain_events_df[
        (chain_events_df["pass_outcome"].notna()) &
        (chain_events_df["pass_category"] == "long") &
        (chain_events_df["phase"] == 2)
    ].groupby("team").size().reindex(all_teams, fill_value=0)

    second_phase_total_short = second_phase_completed_short + second_phase_incomplete_short
    second_phase_total_long = second_phase_completed_long + second_phase_incomplete_long
    second_phase_total = second_phase_total_short + second_phase_total_long

    second_phase_short_percentage = (second_phase_total_short / second_phase_total).fillna(0) * 100
    second_phase_long_percentage = (second_phase_total_long / second_phase_total).fillna(0) * 100
    second_phase_completed_short_percentage = (second_phase_completed_short / second_phase_total_short).replace([float('inf'), -float('inf')], 0).fillna(0) * 100
    second_phase_completed_long_percentage = (second_phase_completed_long / second_phase_total_long).replace([float('inf'), -float('inf')], 0).fillna(0) * 100
    second_phase_incomplete_short_percentage = (second_phase_incomplete_short / second_phase_total_short).replace([float('inf'), -float('inf')], 0).fillna(0) * 100
    second_phase_incomplete_long_percentage = (second_phase_incomplete_long / second_phase_total_long).replace([float('inf'), -float('inf')], 0).fillna(0) * 100

    # Create DataFrame
    result_df = pd.DataFrame({
        "team": all_teams,

        # First phase totals
        "first_total": first_phase_total,
        "first_short": first_phase_total_short,
        "first_long": first_phase_total_long,
        "first_short_pct": first_phase_short_percentage.round(0),
        "first_long_pct": first_phase_long_percentage.round(0),

        # First phase short passes
        "first_completed_short": first_phase_completed_short,
        "first_incomplete_short": first_phase_incomplete_short,
        "first_completed_short_pct": first_phase_completed_short_percentage.round(0),
        "first_incomplete_short_pct": first_phase_incomplete_short_percentage.round(0),

        # First phase long passes
        "first_completed_long": first_phase_completed_long,
        "first_incomplete_long": first_phase_incomplete_long,
        "first_completed_long_pct": first_phase_completed_long_percentage.round(0),
        "first_incomplete_long_pct": first_phase_incomplete_long_percentage.round(0),

        # Second phase totals
        "second_total": second_phase_total,
        "second_short": second_phase_total_short,
        "second_long": second_phase_total_long,
        "second_short_pct": second_phase_short_percentage.round(0),
        "second_long_pct": second_phase_long_percentage.round(0),

        # Second phase short passes
        "second_completed_short": second_phase_completed_short,
        "second_incomplete_short": second_phase_incomplete_short,
        "second_completed_short_pct": second_phase_completed_short_percentage.round(0),
        "second_incomplete_short_pct": second_phase_incomplete_short_percentage.round(0),

        # Second phase long passes
        "second_completed_long": second_phase_completed_long,
        "second_incomplete_long": second_phase_incomplete_long,
        "second_completed_long_pct": second_phase_completed_long_percentage.round(0),
        "second_incomplete_long_pct": second_phase_incomplete_long_percentage.round(0),
    })

    # Convert all columns except 'team' to int
    result_df = result_df.astype({col: int for col in result_df.columns if col != 'team'})

    return result_df.reset_index(drop=True)