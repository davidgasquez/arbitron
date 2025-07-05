"""Main contest orchestration logic."""

import logging
import random
from typing import List, Optional, Union

from .agent import Agent
from .models import Competition, Item, RankingResult
from .ranking import calculate_bradley_terry_scores, rank_items

logger = logging.getLogger(__name__)


def rank(
    items: List[Union[str, Item]],
    contest_description: str,
    agents: List[Agent],
    competition_name: Optional[str] = None,
    n_comparisons_per_agent: int = 10,
    random_seed: Optional[int] = None,
) -> RankingResult:
    """Run a ranking contest with multiple agents.

    Args:
        items: List of items to rank (strings or Item objects)
        contest_description: Description of what's being evaluated
        agents: List of Agent objects with different evaluation criteria
        competition_name: Optional name for the competition
        n_comparisons_per_agent: Number of random pairwise comparisons per agent
        random_seed: Optional seed for reproducible random sampling

    Returns:
        RankingResult with final rankings, scores, and all comparisons
    """
    # Set random seed if provided
    if random_seed is not None:
        random.seed(random_seed)

    # Convert strings to Item objects if needed
    item_objects = []
    for item in items:
        if isinstance(item, str):
            item_objects.append(Item(name=item))  # type: ignore
        else:
            item_objects.append(item)

    # Create Competition object
    competition = Competition(
        name=competition_name or "Arbitron Competition",
        description=contest_description,
        items=item_objects,
    )

    logger.info(
        f"Starting competition '{competition.name}' with {len(item_objects)} items "
        f"and {len(agents)} agents"
    )

    # Generate all possible pairs
    all_pairs = []
    for i in range(len(item_objects)):
        for j in range(i + 1, len(item_objects)):
            all_pairs.append((item_objects[i], item_objects[j]))

    logger.debug(f"Total possible pairs: {len(all_pairs)}")

    # Collect all comparisons
    all_comparisons = []

    for agent in agents:
        # Sample random pairs for this agent
        n_samples = min(n_comparisons_per_agent, len(all_pairs))
        sampled_pairs = random.sample(all_pairs, n_samples)

        logger.info(f"Agent {agent.agent_id} will perform {n_samples} comparisons")

        # Perform comparisons
        for item_a, item_b in sampled_pairs:
            # Randomly swap order to avoid position bias
            if random.random() < 0.5:
                item_a, item_b = item_b, item_a

            comparison = agent.compare(item_a, item_b, contest_description)
            all_comparisons.append(comparison)

    logger.info(f"Collected {len(all_comparisons)} total comparisons")

    # Calculate Bradley-Terry scores
    item_names = [item.name for item in item_objects]
    scores = calculate_bradley_terry_scores(all_comparisons, item_names)

    # Get final ranking
    ranking = rank_items(scores)

    # Create result
    result = RankingResult(
        competition=competition,
        ranking=ranking,
        scores=scores,
        comparisons=all_comparisons,
        metadata={
            "n_agents": len(agents),
            "n_comparisons_per_agent": n_comparisons_per_agent,
            "total_comparisons": len(all_comparisons),
            "random_seed": random_seed,
        },
    )

    logger.info(f"Competition complete. Winner: {ranking[0]}")

    return result
