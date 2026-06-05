"""Tools khusus untuk Finance Agent. Selalu gunakan Decimal untuk perhitungan uang."""

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from shared.agent.tools.base import BaseTool


# ==========================================
# Input Schemas
# ==========================================
class MarketDataInput(BaseModel):
    symbol: str = Field(..., description="Pasangan aset (mis. BTC/USD).")
    exchange: str = Field(default="mock_exchange", description="Nama exchange.")


class TechIndicatorInput(BaseModel):
    symbol: str = Field(..., description="Simbol aset.")
    indicator: str = Field(..., description="Nama indikator (RSI, MACD, MA).")


class PortfolioOptInput(BaseModel):
    symbols: list[str] = Field(..., description="Daftar simbol aset dalam portofolio.")


class RiskCalcInput(BaseModel):
    symbol: str = Field(..., description="Simbol aset yang dinilai risikonya.")


# ==========================================
# Tool Implementations
# ==========================================
class MarketDataTool(BaseTool):
    """Tool untuk memanggil market data (mock CCXT)."""

    args_schema: type[BaseModel] | None = MarketDataInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="market_data", description="Ambil data harga aset terkini.", **kwargs
        )

    def _run(self, symbol: str, exchange: str = "mock_exchange") -> dict[str, Any]:
        # Fallback fungsional, kembalikan data palsu (Decimal).
        prices = {
            "BTC/USD": Decimal("60000.50"),
            "ETH/USD": Decimal("3000.00"),
        }
        return {
            "symbol": symbol,
            "price": str(prices.get(symbol, Decimal("100.00"))),
            "exchange": exchange,
        }


class TechnicalIndicatorTool(BaseTool):
    """Tool untuk menghitung technical indicator dasar."""

    args_schema: type[BaseModel] | None = TechIndicatorInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="tech_indicator", description="Hitung RSI/MACD/MA.", **kwargs
        )

    def _run(self, symbol: str, indicator: str) -> dict[str, Any]:
        val = Decimal("0")
        if indicator.upper() == "RSI":
            val = Decimal("65.4")  # Dummy value
        elif indicator.upper() == "MA":
            val = Decimal("58000.00")
        return {"symbol": symbol, "indicator": indicator.upper(), "value": str(val)}


class PortfolioOptimizerTool(BaseTool):
    """Tool untuk mengoptimasi alokasi portofolio."""

    args_schema: type[BaseModel] | None = PortfolioOptInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="portfolio_optimizer",
            description="Hitung alokasi optimal aset.",
            **kwargs,
        )

    def _run(self, symbols: list[str]) -> dict[str, Any]:
        if not symbols:
            return {"error": "Symbols list is empty"}

        weight = Decimal("1.0") / Decimal(str(len(symbols)))
        allocations = {sym: str(weight) for sym in symbols}

        return {
            "allocations": allocations,
            "expected_return": "0.15",  # 15% return mock
        }


class RiskCalculatorTool(BaseTool):
    """Tool untuk kalkulasi VaR dan CVaR."""

    args_schema: type[BaseModel] | None = RiskCalcInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="risk_calculator", description="Hitung Value at Risk (VaR).", **kwargs
        )

    def _run(self, symbol: str) -> dict[str, Any]:
        # Mock calculation.
        return {
            "symbol": symbol,
            "VaR_95": "0.05",  # 5% max loss in normal day
            "CVaR_95": "0.07",  # 7% expected shortfall
        }
