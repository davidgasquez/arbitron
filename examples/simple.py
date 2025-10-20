from arbitron import Agent, Competition, Item

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

agents = [
    Agent(
        id="SciFi Purist",
        prompt="Compare based on scientific accuracy and hard sci-fi concepts.",
        model="openai:gpt-5-nano",
    ),
    Agent(
        id="Nolan Fan",
        prompt="Compare based on complex narratives and emotional depth.",
        model="openai:gpt-5-nano",
    ),
    Agent(
        id="Critics Choice",
        prompt="Compare based on artistic merit and cinematic excellence.",
        model="openai:gpt-5-nano",
    ),
]

competition = Competition(
    id="sci-fi-soundtracks",
    description="Rank the movies based on their soundtrack quality.",
    agents=agents,
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
