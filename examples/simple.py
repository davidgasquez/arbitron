from pydantic import BaseModel

from arbitron import Competition, Item, Juror


class Movie(BaseModel):
    title: str
    year: int
    composer: str


items = [
    Item(
        id="arrival",
        payload=Movie(title="Arrival", year=2016, composer="Johann Johannsson"),
    ),
    Item(
        id="interstellar",
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

competition = Competition(
    id="sci-fi-soundtracks",
    description="Which movie has the better soundtrack?",
    jurors=jurors,
    items=items,
    concurrency=12,
)

print(f"Total pairs: {competition.total_pairs}")
print(f"Total comparisons: {competition.total_comparisons}")

for comparison in competition.run():
    print(comparison)

print(f"Total cost: {competition.cost}")
