from decimal import Decimal

from agents.finance.src.agent.finance_agent import FinanceAgent
from agents.finance.src.env.finance_env import PortfolioEnvironment, TradingEnvironment
from agents.finance.src.models.finance_models import (
    PortfolioModel,
    PricePredictionModel,
    RiskModel,
)
from agents.finance.src.tools.finance_tools import (
    MarketDataTool,
    PortfolioOptimizerTool,
    RiskCalculatorTool,
    TechnicalIndicatorTool,
)
from shared.models import AgentConfig, AgentDomain, AgentState


def test_finance_models():
    pred = PricePredictionModel(
        symbol="BTC/USD",
        predicted_price=Decimal("60000"),
        confidence_interval_low=Decimal("59000"),
        confidence_interval_high=Decimal("61000"),
        time_horizon_hours=24,
    )
    assert pred.predicted_price == Decimal("60000")

    port = PortfolioModel(
        portfolio_id="p1",
        allocations={"BTC": Decimal("1.0")},
        expected_return=Decimal("0.1"),
        volatility=Decimal("0.05"),
    )
    assert port.portfolio_id == "p1"

    risk = RiskModel(
        symbol_or_portfolio="p1",
        value_at_risk_95=Decimal("0.05"),
        conditional_var_95=Decimal("0.07"),
    )
    assert risk.value_at_risk_95 == Decimal("0.05")


def test_finance_env():
    env = TradingEnvironment(initial_balance=Decimal("10000"))

    # Buy successful
    res = env.execute_trade("BTC/USD", "buy", Decimal("0.1"), Decimal("50000"))
    assert res["status"] == "success"
    assert env.balance["USD"] == Decimal("5000")
    assert env.positions["BTC"] == Decimal("0.1")

    # Buy fail (insufficient balance)
    res2 = env.execute_trade("BTC/USD", "buy", Decimal("10"), Decimal("50000"))
    assert res2["status"] == "failed"

    # Sell successful
    res3 = env.execute_trade("BTC/USD", "sell", Decimal("0.1"), Decimal("60000"))
    assert res3["status"] == "success"
    assert env.balance["USD"] == Decimal("11000")

    # Sell fail
    res4 = env.execute_trade("BTC/USD", "sell", Decimal("1"), Decimal("60000"))
    assert res4["status"] == "failed"

    p_env = PortfolioEnvironment()
    p_res = p_env.rebalance({"BTC": Decimal("0.6"), "ETH": Decimal("0.4")})
    assert p_res["status"] == "success"

    p_res2 = p_env.rebalance({"BTC": Decimal("0.6")})
    assert p_res2["status"] == "failed"


def test_finance_tools():
    md = MarketDataTool()
    assert md._run("BTC/USD").get("price") == "60000.50"

    ti = TechnicalIndicatorTool()
    assert ti._run("BTC/USD", "RSI").get("value") == "65.4"
    assert ti._run("BTC/USD", "MA").get("value") == "58000.00"

    po = PortfolioOptimizerTool()
    assert "allocations" in po._run(["BTC", "ETH"])
    assert "error" in po._run([])

    rc = RiskCalculatorTool()
    assert rc._run("BTC/USD").get("VaR_95") == "0.05"


def test_finance_agent():
    cfg = AgentConfig(name="FinanceAgentTest", domain=AgentDomain.FINANCE)
    agent = FinanceAgent(config=cfg)
    agent.compile()

    hc = agent.health_check()
    assert hc.status == "healthy"

    state = AgentState(messages=[])
    res = agent.run(state)
    assert res.metadata.get("plan") is not None
