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

class ClassificationConfig:
    set_piece_allowed_time = 10 # seconds
    set_piece_allowed_actions = 5 # actions

class Config:
    logging = LoggingConfig()
    statsbomb = StatsbombConfig()
    classification = ClassificationConfig()

config = Config()