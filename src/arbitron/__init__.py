"""Arbitron - Multi-agent consensus ranking system."""

__version__ = "0.1.0"

from .agent import Agent
from .contest import rank
from .models import ComparisonResult, Competition, Item, RankingResult
from .utils import setup_logging

__all__ = [
    "Agent",
    "rank",
    "Item",
    "Competition",
    "ComparisonResult",
    "RankingResult",
    "setup_logging",
]

# Setup default logging
setup_logging()
