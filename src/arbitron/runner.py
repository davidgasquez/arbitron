import asyncio
import logging
from contextlib import contextmanager
from typing import List, Tuple

from .juror import run_juror
from .models import Comparison, Item, Juror
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
    jurors: List[Juror],
    items: List[Item],
    comparisons_per_juror: int | None = None,
    include_reasoning: bool = False,
    concurrency: int = 4,
    verbose: bool = False,
) -> List[Comparison]:
    """
    Run pairwise comparisons between items using multiple jurors.

    Args:
        description: Task description for the comparison
        jurors: List of juror configurations
        items: List of items to compare
        comparisons_per_juror: Number of distinct item pairs each juror evaluates
            (None runs all unique pairs)
        include_reasoning: Whether to request rationale text from jurors
        concurrency: Maximum number of concurrent comparisons

    Returns:
        List of comparison results
    """
    pairs: List[Tuple[Item, Item]] = (
        all_pairs(items)
        if comparisons_per_juror is None
        else sample_pairs(items, comparisons_per_juror)
    )

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
                comparison = await run_juror(
                    juror_config, description, item_a, item_b, include_reasoning
                )
                logger.info(
                    "%s chose %s", juror_config.id, comparison.winner
                )
                return comparison

        tasks = [
            compare_pair(juror_config, item_a, item_b)
            for juror_config in jurors
            for item_a, item_b in pairs
        ]

        return await asyncio.gather(*tasks)


def run(
    description: str,
    jurors: List[Juror],
    items: List[Item],
    comparisons_per_juror: int | None = None,
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
            jurors,
            items,
            comparisons_per_juror,
            include_reasoning,
            concurrency,
            verbose,
        )
    )
