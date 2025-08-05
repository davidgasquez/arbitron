import arbitron
from arbitron.evals.scoring import kendall_tau

movies = [
    arbitron.Item(id="Avatar"),
    arbitron.Item(id="Black Panther"),
    arbitron.Item(id="Casablanca"),
    arbitron.Item(id="E.T. the Extra-Terrestrial"),
    arbitron.Item(id="Inception"),
    arbitron.Item(id="Psycho"),
    arbitron.Item(id="Star Wars"),
    arbitron.Item(id="The Godfather"),
    arbitron.Item(id="The Matrix"),
    arbitron.Item(id="The Wizard of Oz"),
]

agents = [
    arbitron.Agent(
        id="Will",
        prompt="You are a Wikipedian with a broad knowledge base.",
        model="openai:gpt-4.1-mini",
    ),
    arbitron.Agent(
        id="Hanna",
        prompt="You are an engineer with deep knowledge about many topics.",
        model="google-gla:gemini-2.5-flash",
    ),
    arbitron.Agent(
        id="Mei",
        prompt="You are a mathematician specialized in statistics and probability. Very rational and analytical.",
        model="google-gla:gemini-2.5-flash",
    ),
]

description = "Choose the movie that was released earlier (older release date)."

comparisons = arbitron.run(description, agents, movies, concurrency=5)
ranking = arbitron.rank(comparisons)

# Real ranking from oldest to newest
real_ranking = [
    "The Wizard of Oz",  # 1939
    "Casablanca",  # 1942
    "Psycho",  # 1960
    "The Godfather",  # 1972
    "Star Wars",  # 1977
    "E.T. the Extra-Terrestrial",  # 1982
    "The Matrix",  # 1999
    "Avatar",  # 2009
    "Inception",  # 2010
    "Black Panther",  # 2018
]

# Extract arbitron ranking order
arbitron_ranking = [item_id for item_id, score in ranking]


tau = kendall_tau(arbitron_ranking, real_ranking)
print(f"{tau:.3f}")
