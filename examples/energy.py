import arbitron

# Enable logging to see what's happening
arbitron.setup_logging("INFO")

# Items
items: list[str] = [
    "solar_photovoltaic",
    "wind_turbines",
    "nuclear_fission",
    "hydroelectric_dams",
    "geothermal_power",
]

# Contest Description
contest_description = """
    Evaluate different energy sources to determine the best overall option for powering a modern society.
    Consider factors including environmental impact, reliability, scalability, cost-effectiveness,
    safety, accessibility, and long-term sustainability.

    Each energy source should be evaluated holistically,
    weighing both immediate benefits and long-term consequences.
"""

safety_specialist = arbitron.Agent(
    """
    You are a grid stability engineer focused on energy security and reliability.
    When comparing energy production methods, evaluate based on capacity,
    weather independence, stability, and any other important metrics.
    """,
    agent_id="safety_specialist",
)

environmental_specialist = arbitron.Agent(
    """
    You are an environmental scientist specializing in climate impact and ecosystem preservation.
    When evaluating energy sources, prioritize carbon emissions, air quality impact, land use,
    water consumption, wildlife disruption, and waste management. Consider both immediate
    environmental effects and long-term ecological consequences.
    """,
    agent_id="environmental_specialist",
)

economic_specialist = arbitron.Agent(
    """
    You are an energy economist focused on cost-effectiveness and market viability.
    Evaluate energy sources based on levelized cost of energy (LCOE), initial capital requirements,
    operational costs, market stability, job creation potential, and economic scalability.
    Consider both current costs and projected future economics with technological advancement.
    """,
    agent_id="economic_specialist",
)

# Add agents with different value systems
agents = [safety_specialist, environmental_specialist, economic_specialist]

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
