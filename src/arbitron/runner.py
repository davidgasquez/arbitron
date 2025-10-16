import asyncio
import logging
from contextlib import contextmanager
from typing import List, Tuple

from .agent import ArbitronAgent
from .models import Agent as AgentConfig
from .models import Comparison, Item
from .pairing import all_pairs, sample_pairs


logger = logging.getLogger("arbitron.runner")
if not logger.handlers:
    logger.addHandler(logging.NullHandler())


@contextmanager
def _configure_logging(verbose: bool):
    """Temporarily enable runner logging."""
    if not verbose:
        yield
        return

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    previous_level = logger.level
    previous_propagate = logger.propagate

    try:
        logger.setLevel(logging.INFO)
        logger.propagate = False
        yield
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)
        logger.propagate = previous_propagate


async def run_async(
    description: str,
    agents: List[AgentConfig],
    items: List[Item],
    comparisons_per_agent: int | None = None,
    include_reasoning: bool = False,
    concurrency: int = 4,
    verbose: bool = False,
) -> List[Comparison]:
    """
    Run pairwise comparisons between items using multiple agents.

    Args:
        description: Task description for the comparison
        agents: List of agent configurations
        items: List of items to compare
        comparisons_per_agent: Number of distinct item pairs each agent evaluates
            (None runs all unique pairs)
        include_reasoning: Whether to request rationale text from agents
        concurrency: Maximum number of concurrent comparisons

    Returns:
        List of comparison results
    """
    pairs: List[Tuple[Item, Item]] = (
        all_pairs(items)
        if comparisons_per_agent is None
        else sample_pairs(items, comparisons_per_agent)
    )

    with _configure_logging(verbose):
        arbitron_agents = [ArbitronAgent(config) for config in agents]
        semaphore = asyncio.Semaphore(concurrency)

        async def compare_pair(
            agent: ArbitronAgent, item_a: Item, item_b: Item
        ) -> Comparison:
            async with semaphore:
                logger.info(
                    "Comparing %s vs %s with %s",
                    item_a.id,
                    item_b.id,
                    agent.config.id,
                )
                comparison = await agent.compare(
                    description, item_a, item_b, include_reasoning
                )
                logger.info(
                    "%s chose %s", agent.config.id, comparison.winner
                )
                return comparison

        tasks = [
            compare_pair(agent, item_a, item_b)
            for agent in arbitron_agents
            for item_a, item_b in pairs
        ]

        return await asyncio.gather(*tasks)


def run(
    description: str,
    agents: List[AgentConfig],
    items: List[Item],
    comparisons_per_agent: int | None = None,
    include_reasoning: bool = False,
    concurrency: int = 4,
    verbose: bool = False,
) -> List[Comparison]:
    """
    Synchronous wrapper for run_async.
    """
    return asyncio.run(
        run_async(
            description,
            agents,
            items,
            comparisons_per_agent,
            include_reasoning,
            concurrency,
            verbose,
        )
    )
