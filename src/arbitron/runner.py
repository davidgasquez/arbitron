import asyncio
import random
from typing import AsyncIterator, List, Tuple

from .juror import run_juror
from .models import Comparison, Item, Juror
from .pairing import AllPairsSampler, PairSampler


def _randomize_pair_orientations(
    pairs: List[Tuple[Item, Item]],
    rng: random.Random,
) -> List[Tuple[Item, Item]]:
    """Return a copy of pairs with each orientation decided by the RNG."""
    return [
        (item_b, item_a) if rng.randrange(2) else (item_a, item_b)
        for item_a, item_b in pairs
    ]


Job = tuple[Juror, Item, Item]


async def run_async_iter(
    description: str,
    jurors: List[Juror],
    items: List[Item],
    concurrency: int = 4,
    pair_sampler: PairSampler | None = None,
    pairs: List[Tuple[Item, Item]] | None = None,
    seed: int | None = None,
) -> AsyncIterator[Comparison]:
    """
    Run pairwise comparisons between items using multiple jurors.

    Args:
        description: Task description for the comparison
        jurors: List of juror configurations
        items: List of items to compare
        concurrency: Maximum number of concurrent comparisons
        pair_sampler: Pair sampling strategy
        seed: Optional global seed for deterministic sampling and orientation

    Returns:
        Async iterator of comparison results
    """
    if pairs is None:
        sampler = pair_sampler or AllPairsSampler()
        base_pairs = sampler.sample(items, seed=seed)
    else:
        base_pairs = list(pairs)

    orientation_seed = None if seed is None else seed + 1
    rng = random.Random(orientation_seed)
    oriented_pairs = _randomize_pair_orientations(base_pairs, rng)

    jobs: list[Job] = [
        (juror_config, item_a, item_b)
        for item_a, item_b in oriented_pairs
        for juror_config in jurors
    ]

    if not jobs:
        return

    worker_count = max(1, min(concurrency, len(jobs)))

    semaphore = asyncio.Semaphore(worker_count)

    async def execute(job: Job) -> Comparison:
        async with semaphore:
            juror_config, item_a, item_b = job
            return await run_juror(juror_config, description, item_a, item_b)

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(execute(job)) for job in jobs]
        for completed in asyncio.as_completed(tasks):
            yield await completed


async def run_async(
    description: str,
    jurors: List[Juror],
    items: List[Item],
    concurrency: int = 4,
    pair_sampler: PairSampler | None = None,
    seed: int | None = None,
) -> List[Comparison]:
    """Run pairwise comparisons and collect all results."""
    return [
        comparison
        async for comparison in run_async_iter(
            description=description,
            jurors=jurors,
            items=items,
            concurrency=concurrency,
            pair_sampler=pair_sampler,
            seed=seed,
        )
    ]


def run(
    description: str,
    jurors: List[Juror],
    items: List[Item],
    concurrency: int = 4,
    pair_sampler: PairSampler | None = None,
    seed: int | None = None,
) -> List[Comparison]:
    """Synchronous wrapper for run_async."""
    return asyncio.run(
        run_async(
            description=description,
            jurors=jurors,
            items=items,
            concurrency=concurrency,
            pair_sampler=pair_sampler,
            seed=seed,
        )
    )
