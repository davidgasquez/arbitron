import arbitron

movies = [
    arbitron.Item(id="arrival"),
    arbitron.Item(id="interstellar"),
    arbitron.Item(id="inception"),
    arbitron.Item(id="the_dark_knight"),
    arbitron.Item(id="dune"),
    arbitron.Item(id="the_matrix"),
    arbitron.Item(id="2001_space_odyssey"),
]

agents = [
    arbitron.Agent(
        id="SciFi Purist",
        prompt="Compare based on scientific accuracy and hard sci-fi concepts.",
        model="openai:gpt-5-nano",
    ),
    arbitron.Agent(
        id="Nolan Fan",
        prompt="Compare based on complex narratives and emotional depth.",
        model="openai:gpt-5-nano",
    ),
    arbitron.Agent(
        id="Critics Choice",
        prompt="Compare based on artistic merit and cinematic excellence.",
        model="openai:gpt-5-nano",
    ),
]

description = "Rank the movies based on their soundtrack quality."

comparisons = arbitron.run(
    description, agents, movies, comparisons_per_agent=2, verbose=True
)

wins = {movie.id: 0 for movie in movies}
for comparison in comparisons:
    wins[comparison.winner] = wins.get(comparison.winner, 0) + 1

leaderboard = sorted(wins.items(), key=lambda entry: entry[1], reverse=True)

print("Leaderboard (wins):")
for rank, (item_id, count) in enumerate(leaderboard, start=1):
    print(f"{rank}. {item_id}: {count}")
