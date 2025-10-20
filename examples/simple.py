from pydantic_ai import Agent as PydanticAgent

from arbitron import ComparisonDecision, Competition, Item, Juror

movies = [
    Item(id="arrival"),
    Item(id="blade_runner"),
    Item(id="interstellar"),
    Item(id="inception"),
    Item(id="the_dark_knight"),
    Item(id="dune"),
    Item(id="the_matrix"),
    Item(id="2001_space_odyssey"),
    Item(id="the_fifth_element"),
    Item(id="the_martian"),
]

jurors = [
    Juror(
        id="SciFi Purist",
        instructions="Compare based on scientific accuracy and hard sci-fi concepts.",
        model="openai:gpt-5-nano",
    ),
    Juror(
        id="Custom Composer",
        agent=PydanticAgent(
            model="openai:gpt-5-nano",
            instructions="You are a film composer evaluating the emotional impact of each soundtrack.",
            output_type=ComparisonDecision,
        ),
    ),
]

competition = Competition(
    id="sci-fi-soundtracks",
    description="Rank the movies based on their soundtrack quality.",
    jurors=jurors,
    items=movies,
)

comparisons = competition.run()
competition.to_csv("comparisons.csv")

wins = {movie.id: 0 for movie in movies}
for comparison in comparisons:
    wins[comparison.winner] = wins.get(comparison.winner, 0) + 1

leaderboard = sorted(wins.items(), key=lambda entry: entry[1], reverse=True)

print("Leaderboard (wins):")
for rank, (item_id, count) in enumerate(leaderboard, start=1):
    print(f"{rank}. {item_id}: {count}")
