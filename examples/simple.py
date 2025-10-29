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

print(f"Total cost: {competition.cost}")
