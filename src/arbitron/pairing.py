import itertools
import random
from typing import List, Tuple

from .models import Item


def all_pairs(items: List[Item]) -> List[Tuple[Item, Item]]:
    """Generate all possible pairs from a list of items."""
    return [(a, b) for a, b in itertools.combinations(items, 2)]


def sample_pairs(items: List[Item], k: int) -> List[Tuple[Item, Item]]:
    """Generate a random sample of k pairs from a list of items."""
    all_item_pairs = all_pairs(items)
    if k >= len(all_item_pairs):
        return all_item_pairs
    return random.sample(all_item_pairs, k)
