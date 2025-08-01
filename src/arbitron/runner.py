import asyncio
from typing import List

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
    concurrency: int = 10,
) -> List[Comparison]:
    """
    Run pairwise comparisons between items using multiple agents.

    Args:
        description: Task description for the comparison
        agents: List of agent configurations
        items: List of items to compare
        comparisons_per_agent: Number of comparisons per agent (None for all pairs)
        include_reasoning: Whether agents should provide reasoning (default: False)
        concurrency: Maximum number of concurrent comparisons

    Returns:
        List of comparison results
    """
    # Generate pairs of items
    if comparisons_per_agent is None:
        pairs = all_pairs(items)
    else:
        pairs = sample_pairs(items, comparisons_per_agent)

    # Create ArbitronAgent instances
    arbitron_agents = [ArbitronAgent(config) for config in agents]

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(concurrency)

    async def run_comparison(
        agent: ArbitronAgent, item_a: Item, item_b: Item
    ) -> Comparison:
        async with semaphore:
            return await agent.compare(description, item_a, item_b, include_reasoning)

    # Create tasks for all agent-pair combinations
    tasks = []
    for agent in arbitron_agents:
        for item_a, item_b in pairs:
            task = run_comparison(agent, item_a, item_b)
            tasks.append(task)

    # Run all comparisons concurrently
    comparisons = await asyncio.gather(*tasks)

    return comparisons


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
