import asyncio
import logging
import random
from contextlib import contextmanager, suppress
from typing import AsyncIterator, Iterator, List, Tuple

from .juror import run_juror
from .models import Comparison, Item, Juror
from .pairing import AllPairsSampler, PairSampler

logger = logging.getLogger("arbitron.runner")
if not logger.handlers:
    logger.addHandler(logging.NullHandler())


@contextmanager
def _configure_logging(verbose: bool) -> Iterator[None]:
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
        base_pairs = sampler.sample(items)
    else:
        base_pairs = list(pairs)

    rng = random.Random(pair_shuffle_seed)
    oriented_pairs = _randomize_pair_orientations(base_pairs, rng)

    jobs: list[Job] = [
        (juror_config, item_a, item_b)
        for item_a, item_b in oriented_pairs
        for juror_config in jurors
    ]

    if not jobs:
        return

    worker_count = max(1, min(concurrency, len(jobs)))

    with _configure_logging(verbose):
        job_queue: asyncio.Queue[Job | None] = asyncio.Queue()
        result_queue: asyncio.Queue[Comparison | BaseException] = asyncio.Queue()

        for job in jobs:
            job_queue.put_nowait(job)
        for _ in range(worker_count):
            job_queue.put_nowait(None)

        async def worker() -> None:
            while True:
                job = await job_queue.get()
                if job is None:
                    return

                juror_config, item_a, item_b = job
                try:
                    logger.info(
                        "Comparing %s vs %s with %s",
                        item_a.id,
                        item_b.id,
                        juror_config.id,
                    )
                    comparison = await run_juror(
                        juror_config, description, item_a, item_b
                    )
                    logger.info("%s chose %s", juror_config.id, comparison.winner)
                    await result_queue.put(comparison)
                except Exception as exc:  # pragma: no cover - passthrough
                    await result_queue.put(exc)
                    return

        workers = [asyncio.create_task(worker()) for _ in range(worker_count)]

        try:
            remaining = len(jobs)
            while remaining:
                message = await result_queue.get()
                if isinstance(message, BaseException):
                    raise message
                remaining -= 1
                yield message
        finally:
            for worker_task in workers:
                if not worker_task.done():
                    worker_task.cancel()
                with suppress(asyncio.CancelledError):
                    await worker_task


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
    """Synchronous wrapper for run_async."""
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
