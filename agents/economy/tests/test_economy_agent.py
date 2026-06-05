from agents.economy.src.agent.economy_agent import EconomyAgent
from agents.economy.src.env.economy_env import EconomicEnvironment, PolicyEnvironment
from agents.economy.src.models.economy_models import (
    AgentBasedModel,
    MacroModel,
    TradeModel,
)
from agents.economy.src.tools.economy_tools import (
    MacroIndicatorTool,
    PolicyEvaluatorTool,
    SimulationRunnerTool,
    TradeFlowTool,
)
from shared.models import AgentConfig, AgentDomain, AgentState


def test_economy_models():
    abm = AgentBasedModel(agent_type="consumer", initial_wealth=100.0, propensity_to_consume=0.8)
    assert abm.propensity_to_consume == 0.8

    macro = MacroModel(gdp=1000.0, inflation_rate=0.02, unemployment_rate=0.05, interest_rate=0.03)
    assert macro.gdp == 1000.0

    trade = TradeModel(origin="US", destination="ID", volume=500.0)
    assert trade.tariffs == 0.0


def test_economy_env_reproducibility():
    # Test seed reproducibility
    env1 = EconomicEnvironment(seed=42)
    env2 = EconomicEnvironment(seed=42)

    out1 = env1.step()
    out2 = env2.step()

    assert out1["macro"]["gdp"] == out2["macro"]["gdp"]
    assert out1["macro"]["inflation_rate"] == out2["macro"]["inflation_rate"]

    # Test policy
    pol = PolicyEnvironment(env1)
    res1 = pol.apply_shock("interest_hike")
    assert "increased" in res1
    assert env1.macro_state.interest_rate > 0.03

    res2 = pol.apply_shock("fiscal_stimulus")
    assert "increased" in res2

    res3 = pol.apply_shock("unknown")
    assert res3 == "Unknown shock."


def test_economy_tools():
    runner = SimulationRunnerTool()
    res = runner._run(ticks=5, seed=123)
    assert res["status"] == "completed"
    assert res["seed_used"] == 123

    pe = PolicyEvaluatorTool()
    assert pe._run("hike")["estimated_impact"] == "contractionary"
    assert pe._run("stimulus")["estimated_impact"] == "expansionary"
    assert pe._run("none")["estimated_impact"] == "neutral"

    mi = MacroIndicatorTool()
    assert mi._run("gdp")["value"] == 1050.0
    assert mi._run("inflation")["value"] == 0.025
    assert mi._run("unknown")["value"] == 0.0

    tf = TradeFlowTool()
    assert tf._run("US", "UK")["volume_estimate"] == 500.0


def test_economy_agent():
    cfg = AgentConfig(name="EconomyAgentTest", domain=AgentDomain.ECONOMY)
    agent = EconomyAgent(config=cfg)
    agent.compile()

    hc = agent.health_check()
    assert hc.status == "healthy"

    state = AgentState(messages=[])
    res = agent.run(state)
    assert "next_agent" in res.model_dump()
