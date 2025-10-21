from arbitron import Competition, Item, Juror

items = [
    Item(id="Arrival"),
    Item(id="Interstellar"),
    Item(id="Inception"),
    Item(id="Lord of the Rings"),
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
        model="openai:gpt-5-nano",
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
