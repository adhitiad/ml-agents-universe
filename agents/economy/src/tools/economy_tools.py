"""Tools khusus untuk Economy Agent."""

from typing import Any

from pydantic import BaseModel, Field

from shared.agent.tools.base import BaseTool


# ==========================================
# Input Schemas
# ==========================================
class SimRunnerInput(BaseModel):
    ticks: int = Field(default=10, description="Jumlah siklus (ticks) untuk menjalankan simulasi.")
    seed: int = Field(default=42, description="Random seed untuk memastikan reproduktibilitas.")

class PolicyEvalInput(BaseModel):
    policy_type: str = Field(..., description="Jenis kebijakan (e.g. 'interest_hike', 'fiscal_stimulus').")

class MacroIndicatorInput(BaseModel):
    indicator: str = Field(..., description="Nama indikator (e.g. 'gdp', 'inflation').")

class TradeFlowInput(BaseModel):
    origin: str = Field(..., description="Kode wilayah asal.")
    destination: str = Field(..., description="Kode wilayah tujuan.")


# ==========================================
# Tool Implementations
# ==========================================
class SimulationRunnerTool(BaseTool):
    """Tool untuk menjalankan ABM simulation headlessly."""

    args_schema: type[BaseModel] | None = SimRunnerInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="simulation_runner", description="Jalankan simulasi ekonomi X siklus.", **kwargs)

    def _run(self, ticks: int = 10, seed: int = 42) -> dict[str, Any]:
        # Mengembalikan status mock berhasil setelah iterasi
        return {
            "status": "completed",
            "ticks_run": ticks,
            "seed_used": seed,
            "final_gdp_mock": 1000.0 * (1.02 ** (ticks/10))
        }


class PolicyEvaluatorTool(BaseTool):
    """Tool untuk mensimulasikan dampak kebijakan pada ekonomi."""

    args_schema: type[BaseModel] | None = PolicyEvalInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="policy_evaluator", description="Evaluasi kebijakan makro.", **kwargs)

    def _run(self, policy_type: str) -> dict[str, Any]:
        impact = "neutral"
        if "hike" in policy_type.lower():
            impact = "contractionary"
        elif "stimulus" in policy_type.lower():
            impact = "expansionary"
        return {"policy": policy_type, "estimated_impact": impact}


class MacroIndicatorTool(BaseTool):
    """Tool untuk mem-fetch indikator makro simulasi saat ini."""

    args_schema: type[BaseModel] | None = MacroIndicatorInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="macro_indicator", description="Ambil status GDP/inflasi terbaru.", **kwargs)

    def _run(self, indicator: str) -> dict[str, Any]:
        val = 0.0
        if indicator.lower() == "gdp":
            val = 1050.0
        elif indicator.lower() == "inflation":
            val = 0.025
        return {"indicator": indicator, "value": val}


class TradeFlowTool(BaseTool):
    """Tool untuk menganalisis aliran dagang antar dua region."""

    args_schema: type[BaseModel] | None = TradeFlowInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="trade_flow", description="Analisis ekspor-impor bilateral.", **kwargs)

    def _run(self, origin: str, destination: str) -> dict[str, Any]:
        return {
            "origin": origin,
            "destination": destination,
            "volume_estimate": 500.0,
            "tariffs": 0.05
        }
