"""Module for configuring the project."""

class LoggingConfig:
    level = "INFO"
    file = "analysis.log"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class StatsbombConfig:
    competition_id = 55
    season_id = 282
    country = "Europe"
    division = "UEFA Euro"
    season = "2024"
    gender = "male"
    spain_id = 772

class Config:
    logging = LoggingConfig()
    statsbomb = StatsbombConfig()

config = Config()