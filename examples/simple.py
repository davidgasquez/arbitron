import arbitron

movies = [
    arbitron.Item(id="arrival"),
    arbitron.Item(id="blade_runner"),
    arbitron.Item(id="interstellar"),
    arbitron.Item(id="inception"),
    arbitron.Item(id="the_dark_knight"),
    arbitron.Item(id="dune"),
    arbitron.Item(id="the_matrix"),
    arbitron.Item(id="2001_space_odyssey"),
    arbitron.Item(id="the_fifth_element"),
    arbitron.Item(id="the_martian"),
]

agents = [
    arbitron.Agent(
        id="SciFi Purist",
        prompt="Compare based on scientific accuracy and hard sci-fi concepts.",
        model="google-gla:gemini-2.5-flash",
    ),
    arbitron.Agent(
        id="Nolan Fan",
        prompt="Compare based on complex narratives and emotional depth.",
        model="groq:qwen/qwen3-32b",
    ),
    arbitron.Agent(
        id="Critics Choice",
        prompt="Compare based on artistic merit and cinematic excellence.",
        model="openai:gpt-4.1-nano",
    ),
]

description = "Rank the movies based on their soundtrack quality."

comparisons = arbitron.run(description, agents, movies)
ranking = arbitron.rank(comparisons)

print("Rankings (best to worst):")
for i, (item_id, score) in enumerate(ranking, 1):
    print(f"{i}. {item_id}: {score:.3f}")
