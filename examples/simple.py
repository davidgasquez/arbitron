import math
from typing import Any

from choix import ilsr_pairwise
from pydantic import BaseModel

from arbitron import Competition, Item, Juror


# Custom Pydantic model
class Movie(BaseModel):
    title: str
    year: int
    composer: str


items = [
    Item(
        id="arrival",
        # Using a Pydantic model as payload
        payload=Movie(title="Arrival", year=2016, composer="Johann Johannsson"),
    ),
    Item(
        id="interstellar",
        # Using a Python dict as payload
        payload={"title": "Interstellar", "year": 2014, "composer": "Hans Zimmer"},
    ),
    Item(
        id="inception",
        payload=Movie(title="Inception", year=2010, composer="Hans Zimmer"),
    ),
]

jurors = [
    Juror(
        id="SciFi Purist",
        instructions="Score based on impact and originality of the soundtrack.",
        model="openai:gpt-5-nano",
    ),
    Juror(
        id="Soundtrack Enthusiast",
        instructions="Score based on emotional impact and memorability of the soundtrack.",
        model="google-gla:gemini-2.5-flash-lite",
    ),
]


def item_label(item: Item) -> str:
    payload: Any = item.payload
    if isinstance(payload, BaseModel):
        maybe_title = getattr(payload, "title", None)
    elif isinstance(payload, dict):
        maybe_title = payload.get("title")
    else:
        maybe_title = None
    return maybe_title if isinstance(maybe_title, str) else item.id


competition = Competition(
    id="sci-fi-soundtracks",
    description="Which movie has the better soundtrack?",
    jurors=jurors,
    items=items,
    concurrency=12,
)

print(f"Total pairs: {competition.total_pairs}")
print(f"Total comparisons: {competition.total_comparisons}")

results = competition.run()

for comparison in results:
    print(comparison)

item_index = {item.id: index for index, item in enumerate(items)}
pairwise_data = [
    (
        item_index[comparison.winner],
        item_index[
            comparison.item_b
            if comparison.winner == comparison.item_a
            else comparison.item_a
        ],
    )
    for comparison in results
]

params = ilsr_pairwise(len(items), pairwise_data, alpha=1.0)
weights = [math.exp(float(param)) for param in params]
total = sum(weights)
ranking = sorted(
    ((item, weight / total) for item, weight in zip(items, weights, strict=True)),
    key=lambda pair: pair[1],
    reverse=True,
)

print("\nRanking:")
for position, (item, weight) in enumerate(ranking, start=1):
    print(f"{position}. {item_label(item)} — {weight:.2%}")

print(f"Total cost: {competition.cost}")
