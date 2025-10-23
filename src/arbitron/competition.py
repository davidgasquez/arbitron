import asyncio
import csv
from decimal import Decimal
from pathlib import Path
from queue import SimpleQueue
from threading import Thread
from typing import Iterator, List

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

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
    pair_shuffle_seed: int | None = None

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
        pairs = self._ensure_pairs()
        queue: SimpleQueue[Comparison | BaseException | None] = SimpleQueue()
        worker = self._launch_worker(queue, pairs)

        comparisons: list[Comparison] = []

        try:
            while True:
                message = queue.get()
                if message is None:
                    break
                if isinstance(message, BaseException):
                    raise message

                comparison = message
                comparisons.append(comparison)
                if comparison.cost is not None:
                    self._total_cost += comparison.cost
                yield comparison
        finally:
            worker.join()
            self.comparisons = comparisons

    def _launch_worker(
        self,
        queue: SimpleQueue[Comparison | BaseException | None],
        pairs: List[Pair],
    ) -> Thread:
        """Spin up the background worker that bridges async execution."""

        def _produce() -> None:
            async def _consume() -> None:
                try:
                    async for comparison in run_async_iter(
                        description=self.description,
                        jurors=self.jurors,
                        items=self.items,
                        concurrency=self.concurrency,
                        verbose=self.verbose,
                        pair_sampler=self.pair_sampler,
                        pairs=pairs,
                        pair_shuffle_seed=self.pair_shuffle_seed,
                    ):
                        queue.put(comparison)
                except Exception as exc:  # pragma: no cover - passthrough
                    queue.put(exc)
                finally:
                    queue.put(None)

            asyncio.run(_consume())

        worker = Thread(target=_produce, daemon=True)
        worker.start()
        return worker

    def to_csv(self, path: str | Path) -> None:
        """Persist comparison results to a CSV file."""
        if self.comparisons is None:
            raise ValueError("Run the competition before exporting results.")

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
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

    @model_validator(mode="after")
    def _validate_unique_ids(self) -> "Competition":
        """Ensure items and jurors provide unique identifiers."""

        def _duplicates(values: list[str]) -> list[str]:
            seen: set[str] = set()
            duplicates: set[str] = set()
            for value in values:
                if value in seen:
                    duplicates.add(value)
                else:
                    seen.add(value)
            return sorted(duplicates)

        item_ids = [item.id for item in self.items]
        juror_ids = [juror.id for juror in self.jurors]

        duplicate_items = _duplicates(item_ids)
        if duplicate_items:
            raise ValueError(f"Duplicate item ids: {duplicate_items}")

        duplicate_jurors = _duplicates(juror_ids)
        if duplicate_jurors:
            raise ValueError(f"Duplicate juror ids: {duplicate_jurors}")

        return self
