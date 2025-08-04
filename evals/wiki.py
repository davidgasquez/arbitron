from scoring import kendall_tau

import arbitron

movies = [
    arbitron.Item(id="United States Senate"),
    arbitron.Item(id="YouTube"),
    arbitron.Item(id="Facebook"),
    arbitron.Item(id="United_States"),
    arbitron.Item(id="HTTP 404"),
    arbitron.Item(id="Elizabeth II"),
    arbitron.Item(id="Cristiano Ronaldo"),
    arbitron.Item(id="Michael Jackson"),
    arbitron.Item(id="Elon Musk"),
    arbitron.Item(id="Cleopatra"),
]

agents = [
    arbitron.Agent(
        id="Wikipedia Enthusiast",
        prompt="You are an expert Wikipedian with a good graps of the community and articles.",
        model="openai:gpt-4.1-nano",
    ),
    arbitron.Agent(
        id="Random Person",
        prompt="You are a person with general knowledge.",
        model="openai:gpt-4o-mini",
    ),
    arbitron.Agent(
        id="Researcher",
        prompt="You are a researcher with a deep knowledge of many topics. Very rational and analytical.",
        model="openai:o4-mini",
    ),
    arbitron.Agent(
        id="Researcher",
        prompt="You are a researcher with a deep knowledge of many topics. Very rational and analytical.",
        model="google-gla:gemini-2.5-flash",
    ),
]

description = "Choose the most popular Wikipedia article (more views)."

comparisons = arbitron.run(description, agents, movies, concurrency=5)
ranking = arbitron.rank(comparisons)

# for i, (item_id, score) in enumerate(ranking, 1):
#     print(f"{i}. {item_id}: {score:.3f}")

real_ranking = [
    "United States Senate",
    "YouTube",
    "Facebook",
    "United_States",
    "HTTP 404",
    "Elizabeth II",
    "Cristiano Ronaldo",
    "Michael Jackson",
    "Elon Musk",
    "Cleopatra",
]

# Extract arbitron ranking order
arbitron_ranking = [item_id for item_id, score in ranking]


tau = kendall_tau(arbitron_ranking, real_ranking)
print(f"{tau:.3f}")
