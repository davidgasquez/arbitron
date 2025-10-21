import itertools
import random
from abc import ABC, abstractmethod
from typing import List, Sequence, Tuple

from .models import Item

Pair = Tuple[Item, Item]


class PairSampler(ABC):
    """Interface for generating item pairings."""

    @abstractmethod
    def sample(self, items: Sequence[Item]) -> List[Pair]:
        """Return the list of item pairs to evaluate."""


class AllPairsSampler(PairSampler):
    """Generate every unique pair of items in a randomized order."""

    def __init__(self, seed: int | None = None) -> None:
        self._seed = seed

    def sample(self, items: Sequence[Item]) -> List[Pair]:
        pairs = list(itertools.combinations(items, 2))
        rng = random.Random(self._seed)
        rng.shuffle(pairs)
        return pairs


class RandomPairsSampler(PairSampler):
    """Generate a deterministic random subset of item pairs."""

    def __init__(self, count: int, seed: int | None = None) -> None:
        if count < 1:
            raise ValueError("count must be at least 1")
        self._count = count
        self._seed = seed

    def sample(self, items: Sequence[Item]) -> List[Pair]:
        pairs = list(itertools.combinations(items, 2))
        rng = random.Random(self._seed)
        if self._count >= len(pairs):
            rng.shuffle(pairs)
            return pairs

        return rng.sample(pairs, self._count)


DEFAULT_PAIR_SAMPLER = AllPairsSampler()


__all__ = [
    "PairSampler",
    "AllPairsSampler",
    "RandomPairsSampler",
    "DEFAULT_PAIR_SAMPLER",
]
