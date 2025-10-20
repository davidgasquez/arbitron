from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from pydantic import BaseModel

from .models import Comparison, Item, Juror
from .runner import run


class Competition(BaseModel):
    id: str
    description: str
    jurors: List[Juror]
    items: List[Item]
    comparisons_per_juror: int | None = None
    include_reasoning: bool = False
    concurrency: int = 4
    verbose: bool = False
    comparisons: List[Comparison] | None = None

    def run(self) -> List[Comparison]:
        """Execute the competition and store the comparison results."""
        results = run(
            description=self.description,
            jurors=self.jurors,
            items=self.items,
            comparisons_per_juror=self.comparisons_per_juror,
            include_reasoning=self.include_reasoning,
            concurrency=self.concurrency,
            verbose=self.verbose,
        )
        self.comparisons = list(results)
        return self.comparisons

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
            "rationale",
            "comparison_created_at",
        ]

        with output_path.open("w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for comparison in self.comparisons:
                writer.writerow(
                    {
                        "competition_id": self.id,
                        "juror_id": comparison.juror_id,
                        "item_a": comparison.item_a,
                        "item_b": comparison.item_b,
                        "winner": comparison.winner,
                        "rationale": comparison.rationale or "",
                        "comparison_created_at": comparison.created_at.isoformat(),
                    }
                )
