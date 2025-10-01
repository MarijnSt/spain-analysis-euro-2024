"""Module for configuring the project."""

from .config import config
from .logging_config import setup_logging
from .styling import styling

__all__ = [
    "config",
    "setup_logging",
    "styling",
]