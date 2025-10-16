import asyncio
from typing import List, Tuple

from .agent import ArbitronAgent
from .models import Agent as AgentConfig
from .models import Comparison, Item
from .pairing import all_pairs, sample_pairs


async def run_async(
    description: str,
    agents: List[AgentConfig],
    items: List[Item],
    comparisons_per_agent: int | None = None,
    include_reasoning: bool = False,
    concurrency: int = 4,
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

    arbitron_agents = [ArbitronAgent(config) for config in agents]
    semaphore = asyncio.Semaphore(concurrency)

    async def compare_pair(
        agent: ArbitronAgent, item_a: Item, item_b: Item
    ) -> Comparison:
        async with semaphore:
            return await agent.compare(description, item_a, item_b, include_reasoning)

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
        )
    )
