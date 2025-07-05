"""Bradley-Terry ranking implementation."""

import logging
import math
from typing import Dict, List

from .models import ComparisonResult

logger = logging.getLogger(__name__)


def calculate_bradley_terry_scores(
    comparisons: List[ComparisonResult], items: List[str]
) -> Dict[str, float]:
    """Calculate Bradley-Terry scores from pairwise comparisons.

    The Bradley-Terry model estimates the "strength" of each item based on
    win/loss records. Higher scores indicate stronger items.

    Args:
        comparisons: List of pairwise comparison results
        items: List of all item names

    Returns:
        Dictionary mapping item names to Bradley-Terry scores
    """
    # Initialize win matrix
    n = len(items)
    item_to_idx = {item: i for i, item in enumerate(items)}

    # Create win matrix as list of lists
    win_matrix = [[0.0 for _ in range(n)] for _ in range(n)]

    # Count wins for each pair
    for comp in comparisons:
        if comp.winner == comp.item_a:
            winner_idx = item_to_idx[comp.item_a]
            loser_idx = item_to_idx[comp.item_b]
        else:
            winner_idx = item_to_idx[comp.item_b]
            loser_idx = item_to_idx[comp.item_a]

        win_matrix[winner_idx][loser_idx] += 1

    # Calculate total games for each pair
    total_games = [
        [win_matrix[i][j] + win_matrix[j][i] for j in range(n)] for i in range(n)
    ]

    # Initialize Bradley-Terry parameters (log-scale for stability)
    log_strengths = [0.0 for _ in range(n)]

    # Iterative algorithm to estimate strengths
    max_iterations = 100
    tolerance = 1e-6

    for iteration in range(max_iterations):
        old_log_strengths = log_strengths[:]

        for i in range(n):
            numerator = 0.0
            denominator = 0.0

            for j in range(n):
                if i != j and total_games[i][j] > 0:
                    # Number of wins for i against j
                    wins_i = win_matrix[i][j]
                    # Total games between i and j
                    total_ij = total_games[i][j]

                    # Bradley-Terry update
                    strength_ratio = math.exp(
                        old_log_strengths[i] - old_log_strengths[j]
                    )
                    numerator += wins_i
                    denominator += total_ij * (strength_ratio / (1 + strength_ratio))

            # Update log strength
            if denominator > 0 and numerator > 0:
                ratio = numerator / denominator
                # Clamp ratio to avoid extreme values
                ratio = max(1e-10, min(ratio, 1e10))
                log_strengths[i] = math.log(ratio)
            elif denominator > 0:
                # Handle case where numerator is 0 (item never won)
                log_strengths[i] = math.log(1e-10)  # Very small value instead of 0

        # Normalize (set geometric mean to 1)
        mean_log_strength = sum(log_strengths) / n
        log_strengths = [ls - mean_log_strength for ls in log_strengths]

        # Check convergence
        max_diff = max(abs(log_strengths[i] - old_log_strengths[i]) for i in range(n))
        if max_diff < tolerance:
            logger.debug(f"Bradley-Terry converged in {iteration + 1} iterations")
            break

    # Convert to actual strengths
    strengths = [math.exp(ls) for ls in log_strengths]

    # Create result dictionary
    scores = {items[i]: float(strengths[i]) for i in range(n)}

    logger.info("Bradley-Terry scores calculated successfully")
    return scores


def rank_items(scores: Dict[str, float]) -> List[str]:
    """Convert scores to a ranked list of items.

    Args:
        scores: Dictionary mapping item names to scores

    Returns:
        List of items in descending order of score
    """
    return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
