import asyncio
import logging
import random
from contextlib import contextmanager, suppress
from typing import AsyncIterator, List, Tuple

from .juror import run_juror
from .models import Comparison, Item, Juror
from .pairing import AllPairsSampler, PairSampler

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


def _randomize_pair_orientations(
    pairs: List[Tuple[Item, Item]],
    rng: random.Random,
) -> List[Tuple[Item, Item]]:
    """Return a copy of pairs with each orientation decided by the RNG."""
    randomized: List[Tuple[Item, Item]] = []
    for item_a, item_b in pairs:
        if rng.randrange(2):
            randomized.append((item_b, item_a))
        else:
            randomized.append((item_a, item_b))
    return randomized


async def run_async_iter(
    description: str,
    jurors: List[Juror],
    items: List[Item],
    concurrency: int = 4,
    verbose: bool = False,
    pair_sampler: PairSampler | None = None,
    pairs: List[Tuple[Item, Item]] | None = None,
    pair_shuffle_seed: int | None = None,
) -> AsyncIterator[Comparison]:
    """
    Run pairwise comparisons between items using multiple jurors.

    Args:
        description: Task description for the comparison
        jurors: List of juror configurations
        items: List of items to compare
        concurrency: Maximum number of concurrent comparisons
        pair_sampler: Pair sampling strategy

    Returns:
        Async iterator of comparison results
    """
    if pairs is None:
        sampler = pair_sampler or AllPairsSampler()
        pairs = sampler.sample(items)
    else:
        pairs = list(pairs)

    rng = random.Random(pair_shuffle_seed)
    pairs = _randomize_pair_orientations(pairs, rng)

    with _configure_logging(verbose):
        semaphore = asyncio.Semaphore(concurrency)

        async def compare_pair(
            juror_config: Juror, item_a: Item, item_b: Item
        ) -> Comparison:
            async with semaphore:
                logger.info(
                    "Comparing %s vs %s with %s",
                    item_a.id,
                    item_b.id,
                    juror_config.id,
                )
                comparison = await run_juror(juror_config, description, item_a, item_b)
                logger.info("%s chose %s", juror_config.id, comparison.winner)
                return comparison

        tasks = [
            asyncio.create_task(compare_pair(juror_config, item_a, item_b))
            for item_a, item_b in pairs
            for juror_config in jurors
        ]

        try:
            for future in asyncio.as_completed(tasks):
                yield await future
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
                    with suppress(asyncio.CancelledError):
                        await task


async def run_async(
    description: str,
    jurors: List[Juror],
    items: List[Item],
    concurrency: int = 4,
    verbose: bool = False,
    pair_sampler: PairSampler | None = None,
    pair_shuffle_seed: int | None = None,
) -> List[Comparison]:
    """Run pairwise comparisons and collect all results."""
    return [
        comparison
        async for comparison in run_async_iter(
            description,
            jurors,
            items,
            concurrency,
            verbose,
            pair_sampler,
            pair_shuffle_seed=pair_shuffle_seed,
        )
    ]


def run(
    description: str,
    jurors: List[Juror],
    items: List[Item],
    concurrency: int = 4,
    verbose: bool = False,
    pair_sampler: PairSampler | None = None,
    pair_shuffle_seed: int | None = None,
) -> List[Comparison]:
    """
    Synchronous wrapper for run_async.
    """
    return asyncio.run(
        run_async(
            description,
            jurors,
            items,
            concurrency,
            verbose,
            pair_sampler,
            pair_shuffle_seed,
        )
    )
