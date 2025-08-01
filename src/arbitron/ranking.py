from typing import List, Tuple

import choix

from .models import Comparison


def rank(
    comparisons: List[Comparison], *, alpha: float = 0.001, max_iter: int = 1000
) -> List[Tuple[str, float]]:
    """
    Estimate Bradley-Terry scores for every item that appears in the
    supplied `comparisons` list and return a descending ranking.

    Parameters
    ----------
    comparisons : list[Comparison]
        All pairwise judgements that have been produced so far.
    alpha : float, default 0.001
        Damping factor passed straight to `choix.ilsr_pairwise`.
    max_iter : int, default 1000
        Maximum number of ILSR iterations.

    Returns
    -------
    list[tuple[item_id, score]]
        A list of (item_id, estimated_skill) tuples sorted from the
        strongest item to the weakest. The return type is plain
        Python - no pydantic or custom classes - so it is easy to print,
        serialise or post-process.
    """
    if not comparisons:
        return []

    # Collect all unique item ids
    item_ids: set[str] = {cmp.item_a for cmp in comparisons} | {
        cmp.item_b for cmp in comparisons
    }

    if len(item_ids) < 2:
        # Need at least 2 items for ranking
        return [(list(item_ids)[0], 0.0)] if item_ids else []

    # Build stable index mapping for choix
    id_to_idx = {item_id: i for i, item_id in enumerate(sorted(item_ids))}

    # Convert each Comparison into (winner_idx, loser_idx) tuple
    data: List[Tuple[int, int]] = []
    for cmp in comparisons:
        w_id = cmp.winner
        # Winner must be one of the two items
        if w_id == cmp.item_a:
            l_id = cmp.item_b
        elif w_id == cmp.item_b:
            l_id = cmp.item_a
        else:
            raise ValueError(
                f"Winner {w_id!r} is not part of the compared pair "
                f"({cmp.item_a!r}, {cmp.item_b!r})."
            )
        data.append((id_to_idx[w_id], id_to_idx[l_id]))

    # Feed the data to choix
    scores = choix.ilsr_pairwise(
        n_items=len(item_ids), data=data, alpha=alpha, max_iter=max_iter
    )

    # Translate scores back to item ids and sort descending
    ranking = sorted(
        ((item_id, float(scores[idx])) for item_id, idx in id_to_idx.items()),
        key=lambda t: t[1],
        reverse=True,
    )

    return ranking
