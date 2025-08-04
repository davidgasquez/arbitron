import pathlib
from typing import List, Tuple

import yaml

from .models import Agent, Item


def load_competition(
    path: str | pathlib.Path,
) -> Tuple[str, List[Agent], List[Item], int | None, bool]:
    """Read YAML config and re-create domain objects."""
    path = pathlib.Path(path).expanduser().resolve()
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    # Mandatory
    description: str = raw["description"]
    agents = [Agent(**a) for a in raw["agents"]]
    items = [Item(**i) for i in raw["items"]]

    # Optional
    cpa = raw.get("comparisons_per_agent")  # may be None
    include_reasoning = raw.get("include_reasoning", False)

    return description, agents, items, cpa, include_reasoning
