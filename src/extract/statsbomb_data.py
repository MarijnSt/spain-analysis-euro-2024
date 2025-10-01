import pandas as pd
import logging
from statsbombpy import sb

from src.config import config


# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def fetch_statsbomb_event_data(
    competition_id: int = config.statsbomb.competition_id,
    season_id: int = config.statsbomb.season_id
) -> pd.DataFrame:
    """
    Fetch StatsBomb event data for a given competition and season.

    Parameters:
    ----------
    competition_id: int
        The StatsBomb competition ID.
    season_id: int
        The StatsBomb season ID.

    Returns:
    --------
    pd.DataFrame
        The StatsBomb event data for the given competition and season in a pandas DataFrame.
    """

    logger.info(f"Fetching StatsBomb event data for {config.statsbomb.country} - {config.statsbomb.division} - {config.statsbomb.season} - {config.statsbomb.gender}")

    events = sb.competition_events(
        country=config.statsbomb.country,
        division=config.statsbomb.division,
        season=config.statsbomb.season,
        gender=config.statsbomb.gender
    )

    logger.info(f"Found {len(events)} events!")

    return events