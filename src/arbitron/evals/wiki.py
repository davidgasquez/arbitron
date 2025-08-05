import arbitron
from arbitron.evals.scoring import kendall_tau

movies = [
    arbitron.Item(id="Cleopatra"),
    arbitron.Item(id="Cristiano Ronaldo"),
    arbitron.Item(id="Elizabeth II"),
    arbitron.Item(id="Elon Musk"),
    arbitron.Item(id="Facebook"),
    arbitron.Item(id="HTTP 404"),
    arbitron.Item(id="Michael Jackson"),
    arbitron.Item(id="United States Senate"),
    arbitron.Item(id="United States"),
    arbitron.Item(id="YouTube"),
]

agents = [
    arbitron.Agent(
        id="Will",
        prompt="You are a Wikipedian with a broad knowledge base.",
        model="openai:gpt-4.1-nano",
    ),
    arbitron.Agent(
        id="Hanna",
        prompt="You are an engineer with deep knowledge about many topics.",
        model="google-gla:gemini-2.5-flash",
    ),
    arbitron.Agent(
        id="Mei",
        prompt="You are a mathematician specialized in statistics and probability. Very rational and analytical.",
        model="anthropic:claude-sonnet-4-0",
    ),
]

description = "Choose the MOST POPULAR (total cumulative views) Wikipedia article. Consider the cultural impact, and historical relevance, not just recent trends. Use your best judgment based on your knowledge and experience."

comparisons = arbitron.run(description, agents, movies, concurrency=5)
ranking = arbitron.rank(comparisons)

for i, (item_id, score) in enumerate(ranking, 1):
    print(f"{i}. {item_id}: {score:.3f}")

real_ranking = [
    "United States Senate",
    "YouTube",
    "Facebook",
    "United States",
    "HTTP 404",
    "Elizabeth II",
    "Cristiano Ronaldo",
    "Michael Jackson",
    "Elon Musk",
    "Cleopatra",
]

# Extract arbitron ranking order
arbitron_ranking = [item_id for item_id, score in ranking]

# Calculate Kendall's Tau correlation coefficient
tau = kendall_tau(arbitron_ranking, real_ranking)
print(f"{tau:.3f}")
