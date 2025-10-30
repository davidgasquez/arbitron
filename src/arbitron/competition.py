import asyncio
import csv
import sys
from decimal import Decimal
from pathlib import Path
from typing import AsyncIterator, List

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
    comparisons: List[Comparison] | None = None
    pair_sampler: PairSampler = Field(default_factory=AllPairsSampler)
    seed: int | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
    _pairs: List[Pair] | None = PrivateAttr(default=None)
    _total_cost: Decimal = PrivateAttr(default_factory=lambda: Decimal("0"))

    def _ensure_pairs(self) -> List[Pair]:
        if self._pairs is None:
            self._pairs = self.pair_sampler.sample(self.items, seed=self.seed)
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

    async def stream(self, progress: bool = False) -> AsyncIterator[Comparison]:
        """Asynchronously stream comparison results as they complete."""
        self._total_cost = Decimal("0")
        if self.comparisons is not None:
            self.comparisons = None
            self._pairs = None
        pairs = self._ensure_pairs()
        comparisons: list[Comparison] = []
        total = self.total_comparisons
        completed = 0
        final_emitted = False

        def _percentage(count: int) -> float:
            if total == 0:
                return 100.0
            return (count / total) * 100

        def _emit_progress(count: int, final: bool = False) -> None:
            nonlocal final_emitted
            if not progress:
                return
            percentage = _percentage(count)
            suffix = "\n" if final else "\r"
            print(
                (
                    f"Competition {self.id}: "
                    f"{count}/{total} comparisons ({percentage:6.2f}%)"
                ),
                end=suffix,
                file=sys.stderr,
                flush=True,
            )
            if final:
                final_emitted = True

        try:
            async for comparison in run_async_iter(
                description=self.description,
                jurors=self.jurors,
                items=self.items,
                concurrency=self.concurrency,
                pair_sampler=self.pair_sampler,
                pairs=pairs,
                seed=self.seed,
            ):
                comparisons.append(comparison)
                if comparison.cost is not None:
                    self._total_cost += comparison.cost
                completed += 1
                is_last = completed == total
                _emit_progress(completed, final=is_last)
                yield comparison
        finally:
            if progress and not final_emitted:
                _emit_progress(completed, final=True)
            self.comparisons = comparisons

    def run(self, progress: bool = False) -> List[Comparison]:
        """Collect all comparison results synchronously."""

        async def _collect() -> List[Comparison]:
            return [comparison async for comparison in self.stream(progress=progress)]

        return asyncio.run(_collect())

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
            "comparison_confidence",
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
                    "comparison_confidence": f"{comparison.confidence:.4f}",
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
