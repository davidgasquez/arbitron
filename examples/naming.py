import arbitron

# Enable logging to see what's happening
arbitron.setup_logging("INFO")

# Items
items: list[str] = [
    "Tribunal",
    "Tribunai",
    "Jury",
    "Council",
    "Chorus",
    "Quorum",
    "Gravitai",
    "Gravitas",
    "Arbiter",
    "Arbitron",
    "Dependex",
    "Impactify",
    "Impetus",
    "Aestimator",
    "Ranksmith",
]

# Contest Description
contest_description = """
    Choose the best name for a project that implements a multi-agent consensus ranking system to derive optimal weights through pairwise comparisons.
    The project uses multiple agents, each one configured with unique values, to perform pairwise evaluations across any arbitrary set of items. Using multiple ranking algorithms, it synthesizes these diverse judgments into robust, bias-resistant rankings.
    The name should be one word, simple, and convey a sense of agentic AI.
"""

branding_specialist = arbitron.Agent(
    """
    You are a branding expert focused on creating impactful names.
    When evaluating project names, consider factors like memorability,
    relevance, simplicity, and the emotions they evoke.
    """,
    agent_id="branding_specialist",
)

developer = arbitron.Agent(
    """
    You are a software developer with a focus on technical clarity.
    When evaluating project names, consider factors like technical accuracy,
    ease of understanding, and how well the name conveys the project's purpose.
    """,
    agent_id="developer",
)

github_expert = arbitron.Agent(
    """
    You are a GitHub expert who understands how names perform in search and discoverability.
    When evaluating project names, consider factors like uniqueness,
    searchability, and how well the name aligns with GitHub's conventions.
    """,
    agent_id="github_expert",
)

# Add agents with different value systems
agents = [branding_specialist, developer, github_expert]

# Run the ranking contest
results = arbitron.rank(
    items=list(items), contest_description=contest_description, agents=agents
)

# Display results
print("\n=== FINAL RANKING ===")
for i, item in enumerate(results.ranking, 1):
    print(f"{i}. {item} (score: {results.scores[item]:.3f})")

print(f"\nTotal comparisons made: {len(results.comparisons)}")

# Show a few example comparisons
print("\n=== SAMPLE COMPARISONS ===")
for comp in results.comparisons[:3]:
    print(f"\n{comp.agent_id} compared {comp.item_a} vs {comp.item_b}")
    print(f"Winner: {comp.winner}")
    print(f"Reasoning: {comp.reasoning[:150]}...")
