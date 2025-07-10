# Arbitron ⚖️

A multi-agent consensus ranking system to derive optimal weights through pairwise comparisons. Arbitron uses multiple agents, each one configured with unique values, to perform pairwise evaluations across any arbitrary set of items. Using multiple ranking algorithms, it synthesizes these diverse judgments into robust, bias-resistant rankings.

### Why not a proper council and let the agents talk?

Needs to be done with the entire list and that requires a global view. Easy for agents to ignore one element and mess things up. Adding a new dependencies requires rerunning everything.

## 🌟 Features

- 🤖 Deploy multiple AI agents with customizable value systems.
- ⚖️ Aggregate diverse perspectives using different ranking methods.
- 🛡️ Reduces single-agent bias through ensemble decision-making.

## 🚀 Quickstart

Running an Arbitron contest is easy. First, install Arbitron.

```bash
pip install arbitron
```

Then, you can do a simple evaluation run like this:

```python
import arbitron

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

print(results.ranking)
print(results.scores)
print(results.comparisons)
```

That will kickoff a contest...

```bash
❯ uv run examples/energy.py
2025-07-05 17:15:20 - arbitron.agent - INFO - Initialized agent safety_specialist
2025-07-05 17:15:20 - arbitron.agent - INFO - Initialized agent environmental_specialist
2025-07-05 17:15:20 - arbitron.agent - INFO - Initialized agent economic_specialist
2025-07-05 17:15:20 - arbitron.contest - INFO - Starting competition 'Arbitron Competition' with 5 items and 3 agents
2025-07-05 17:15:20 - arbitron.contest - INFO - Agent safety_specialist will perform 10 comparisons
2025-07-05 17:15:21 - arbitron.agent - INFO - Agent safety_specialist chose nuclear_fission over wind_turbines
2025-07-05 17:15:23 - arbitron.agent - INFO - Agent safety_specialist chose hydroelectric_dams over solar_photovoltaic
2025-07-05 17:15:24 - arbitron.agent - INFO - Agent safety_specialist chose geothermal_power over solar_photovoltaic
2025-07-05 17:15:26 - arbitron.agent - INFO - Agent safety_specialist chose nuclear_fission over hydroelectric_dams
2025-07-05 17:15:28 - arbitron.agent - INFO - Agent safety_specialist chose nuclear_fission over solar_photovoltaic
2025-07-05 17:15:29 - arbitron.agent - INFO - Agent safety_specialist chose hydroelectric_dams over geothermal_power
2025-07-05 17:15:30 - arbitron.agent - INFO - Agent safety_specialist chose geothermal_power over wind_turbines
2025-07-05 17:15:31 - arbitron.agent - INFO - Agent safety_specialist chose wind_turbines over solar_photovoltaic
2025-07-05 17:15:32 - arbitron.agent - INFO - Agent safety_specialist chose nuclear_fission over geothermal_power
2025-07-05 17:15:33 - arbitron.agent - INFO - Agent safety_specialist chose hydroelectric_dams over wind_turbines
2025-07-05 17:15:33 - arbitron.contest - INFO - Agent environmental_specialist will perform 10 comparisons
2025-07-05 17:15:35 - arbitron.agent - INFO - Agent environmental_specialist chose solar_photovoltaic over hydroelectric_dams
2025-07-05 17:15:37 - arbitron.agent - INFO - Agent environmental_specialist chose wind_turbines over hydroelectric_dams
2025-07-05 17:15:39 - arbitron.agent - INFO - Agent environmental_specialist chose wind_turbines over nuclear_fission
2025-07-05 17:15:40 - arbitron.agent - INFO - Agent environmental_specialist chose nuclear_fission over hydroelectric_dams
2025-07-05 17:15:41 - arbitron.agent - INFO - Agent environmental_specialist chose geothermal_power over nuclear_fission
2025-07-05 17:15:43 - arbitron.agent - INFO - Agent environmental_specialist chose geothermal_power over hydroelectric_dams
2025-07-05 17:15:44 - arbitron.agent - INFO - Agent environmental_specialist chose solar_photovoltaic over nuclear_fission
2025-07-05 17:15:46 - arbitron.agent - INFO - Agent environmental_specialist chose wind_turbines over geothermal_power
```

And you get a nice ranking!

```bash
1. solar_photovoltaic (score: 1.227)
2. wind_turbines (score: 1.127)
3. nuclear_fission (score: 1.127)
4. hydroelectric_dams (score: 0.801)
5. geothermal_power (score: 0.801)
```

## 📜 License

Arbitron is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
