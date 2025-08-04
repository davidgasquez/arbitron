import csv
from datetime import datetime
from pathlib import Path
from typing import List

from .models import Comparison

CSV_HEADER = ["agent_id", "item_a", "item_b", "winner", "rationale", "created_at"]


def write_comparisons(path: str | Path, comparisons: List[Comparison]) -> None:
    path = Path(path).expanduser()
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_HEADER)
        w.writeheader()
        for c in comparisons:
            w.writerow(c.model_dump())


def read_comparisons(path: str | Path) -> List[Comparison]:
    path = Path(path).expanduser()
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return [
            Comparison(
                agent_id=row["agent_id"],
                item_a=row["item_a"],
                item_b=row["item_b"],
                winner=row["winner"],
                rationale=row["rationale"] or None,
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in r
        ]
