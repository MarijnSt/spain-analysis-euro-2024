import pandas as pd
import logging
from statsbombpy import sb

from src.config import config


# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def fetch_statsbomb_event_data(
    country: str = config.statsbomb.country,
    division: str = config.statsbomb.division,
    season: str = config.statsbomb.season,
    gender: str = config.statsbomb.gender
) -> pd.DataFrame:
    """
    Fetch StatsBomb event data for a given competition and season.

    Parameters:
    ----------
    country: str
        The country of the competition.
    division: str
        The division of the competition.
    season: str
        The season of the competition.
    gender: str
        The gender of the players in the competition.

    Returns:
    --------
    pd.DataFrame
        The StatsBomb event data for the given competition and season in a pandas DataFrame.
    """

    logger.info(f"Fetching StatsBomb event data for {country} - {division} - {season} - {gender}")

    events = sb.competition_events(
        country=country,
        division=division,
        season=season,
        gender=gender
    )

    logger.info(f"Found {len(events)} events!")

    return events