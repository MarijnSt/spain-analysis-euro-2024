"""Logging configuration setup."""

import logging

from .config import config

def setup_logging(
    level: str = None,
    log_file: str = None,
    log_format: str = None
) -> logging.Logger:
    """
    Set up logging configuration.
    
    Parameters
    ----------
    level : str, optional
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL), by default None
    log_file : str, optional
        Path to log file, by default None
    log_format : str, optional
        Log message format, by default None
        
    Returns
    -------
    logging.Logger
        Configured logger instance
        
    Notes
    -----
    If parameters are not provided, uses values from global config.
    """
    # Use config defaults if not provided
    level = level or config.logging.level
    log_file = log_file or config.logging.file
    log_format = log_format or config.logging.format
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)