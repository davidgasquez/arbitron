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
    "Cofee",
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

developer = arbitron.Agent(
    """
    You are a software developer with a focus on simplicity.
    When evaluating project names, consider factors like technical accuracy,
    ease of understanding, and how well the name conveys the project's purpose.
    """,
    agent_id="developer",
    model="openai:gpt-4.1-nano",
)

github_expert = arbitron.Agent(
    """
    You are a GitHub expert who understands how names perform in search and discoverability.
    When evaluating project names, consider factors like uniqueness,
    searchability, and how well the name aligns with GitHub's conventions.
    """,
    agent_id="github_expert",
    model="google-gla:gemini-2.5-flash-lite",
)

python_backend = arbitron.Agent(
    """
    You are a Python backend developer with a focus on technical clarity and performance.
    When evaluating project names, consider factors like clarity in naming and how easy it is to install in Python environments.
    You also consider how the name might be used in code, such as package names or module names.
    Ensure the name is not too long and follows Python's naming conventions.
    """,
    agent_id="python_backend",
    model="groq:moonshotai/kimi-k2-instruct",
)

# Add agents with different value systems
agents = [
    developer,
    github_expert,
    python_backend,
]

# Run the ranking contest
results = arbitron.rank(
    items=list(items),
    contest_description=contest_description,
    agents=agents,
    n_comparisons_per_agent=20,
    output_file="new_naming_competition.csv",
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
