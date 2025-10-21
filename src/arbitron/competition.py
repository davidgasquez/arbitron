import asyncio
import csv
from decimal import Decimal
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Iterator, List

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from .models import Comparison, Item, Juror
from .pairing import AllPairsSampler, PairSampler
from .runner import run_async_iter

Pair = tuple[Item, Item]


class Competition(BaseModel):
    id: str
    description: str
    jurors: List[Juror]
    items: List[Item]
    concurrency: int = 4
    verbose: bool = False
    comparisons: List[Comparison] | None = None
    pair_sampler: PairSampler = Field(default_factory=AllPairsSampler)

    model_config = ConfigDict(arbitrary_types_allowed=True)
    _pairs: List[Pair] | None = PrivateAttr(default=None)
    _total_cost: Decimal = PrivateAttr(default_factory=lambda: Decimal("0"))

    def _ensure_pairs(self) -> List[Pair]:
        if self._pairs is None:
            self._pairs = self.pair_sampler.sample(self.items)
        return self._pairs

    @property
    def pairs(self) -> List[Pair]:
        """Return cached item pairs for this competition."""

        return list(self._ensure_pairs())

    @property
    def total_pairs(self) -> int:
        """Total number of unique item pairs to be compared."""

        return len(self._ensure_pairs())

    @property
    def total_comparisons(self) -> int:
        """Total comparisons after accounting for all jurors."""

        return self.total_pairs * len(self.jurors)

    @property
    def cost(self) -> Decimal:
        """Return the accumulated model cost for this competition."""

        return self._total_cost

    def run(self) -> Iterator[Comparison]:
        """Stream comparison results as they are produced."""

        self._total_cost = Decimal("0")

        def iterator() -> Iterator[Comparison]:
            comparisons: List[Comparison] = []
            output_queue: Queue[Comparison | Exception | None] = Queue()
            pairs = self._ensure_pairs()

            def producer() -> None:
                async def consume() -> None:
                    try:
                        async for comparison in run_async_iter(
                            description=self.description,
                            jurors=self.jurors,
                            items=self.items,
                            concurrency=self.concurrency,
                            verbose=self.verbose,
                            pair_sampler=self.pair_sampler,
                            pairs=pairs,
                        ):
                            output_queue.put(comparison)
                    except Exception as exc:  # pragma: no cover - passthrough
                        output_queue.put(exc)
                    finally:
                        output_queue.put(None)

                asyncio.run(consume())

            worker = Thread(target=producer, daemon=True)
            worker.start()

            try:
                while True:
                    item = output_queue.get()
                    if isinstance(item, Exception):
                        raise item
                    if item is None:
                        break
                    comparisons.append(item)
                    if item.cost is not None:
                        self._total_cost += item.cost
                    yield item
            finally:
                worker.join()
                self.comparisons = comparisons

        return iterator()

    def to_csv(self, path: str | Path) -> None:
        """Persist comparison results to a CSV file."""
        if self.comparisons is None:
            raise ValueError("Run the competition before exporting results.")

        output_path = Path(path)
        fieldnames = [
            "competition_id",
            "juror_id",
            "item_a",
            "item_b",
            "winner",
            "comparison_created_at",
            "comparison_cost",
        ]

        with output_path.open("w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for comparison in self.comparisons:
                writer.writerow({
                    "competition_id": self.id,
                    "juror_id": comparison.juror_id,
                    "item_a": comparison.item_a,
                    "item_b": comparison.item_b,
                    "winner": comparison.winner,
                    "comparison_created_at": comparison.created_at.isoformat(),
                    "comparison_cost": (
                        str(comparison.cost) if comparison.cost is not None else ""
                    ),
                })
