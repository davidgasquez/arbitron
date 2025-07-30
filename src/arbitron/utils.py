"""Utility functions and logging configuration."""

import logging
import sys
def setup_logging(level: str | None = None) -> None:
    """Configure logging for Arbitron.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, (level or "INFO").upper(), logging.INFO)
    
    logger = logging.getLogger("arbitron")
    
    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(handler)
        logger.setLevel(log_level)
        logger.propagate = False
