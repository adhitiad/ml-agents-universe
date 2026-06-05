"""Agen Finance dengan arsitektur Plan-and-Execute."""

import logging
from typing import Any

from langgraph.graph import StateGraph

from agents.finance.src.tools.finance_tools import (
    MarketDataTool,
    PortfolioOptimizerTool,
    RiskCalculatorTool,
    TechnicalIndicatorTool,
)
from shared.agent.base import BaseAgent
from shared.agent.graphs.plan_execute import create_plan_execute_graph
from shared.models import AgentState, ComponentHealth, HealthStatus, HealthStatusEnum


logger = logging.getLogger(__name__)


class FinanceAgent(BaseAgent):
    """Finance Agent berbasis Plan and Execute."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Mendaftarkan tool finance ke dalam internal tool registry."""
        self.tools.register(MarketDataTool())
        self.tools.register(TechnicalIndicatorTool())
        self.tools.register(PortfolioOptimizerTool())
        self.tools.register(RiskCalculatorTool())
        logger.info("Finance Agent: Default tools berhasil diregistrasi.")

    def build_graph(self) -> StateGraph:
        """Mengonstruksi Plan-and-Execute StateGraph."""
        return create_plan_execute_graph(
            state_schema=AgentState,
            planner_node=self._planner_step,
            executor_node=self._executor_step,
            replan_node=self._replan_step,
            check_done_condition=self._check_done,
        )

    def _planner_step(self, state: Any) -> dict[str, Any]:
        """Node untuk merencanakan aksi (contoh: [cek harga, hitung risiko, eksekusi])."""
        logger.info("FinanceAgent Planner Step.")
        metadata = (
            getattr(state, "metadata", {})
            if not isinstance(state, dict)
            else state.get("metadata", {})
        )
        plan = metadata.get("plan", ["market_data", "risk_calculator"])
        metadata["plan"] = plan
        return {"metadata": metadata}

    def _executor_step(self, state: Any) -> dict[str, Any]:
        """Node untuk mengeksekusi step berikutnya dari plan."""
        logger.info("FinanceAgent Executor Step.")
        metadata = (
            getattr(state, "metadata", {})
            if not isinstance(state, dict)
            else state.get("metadata", {})
        )
        plan = metadata.get("plan", [])
        if plan:
            current_step = plan.pop(0)
            logger.info("Mengeksekusi rencana: %s", current_step)
            # Pada implementasi asli, ini akan memanggil tool yang relevan.

        return {"metadata": metadata}

    def _replan_step(self, state: Any) -> dict[str, Any]:
        """Re-evaluasi rencana setelah eksekusi."""
        logger.info("FinanceAgent Replan Step.")
        metadata = (
            getattr(state, "metadata", {})
            if not isinstance(state, dict)
            else state.get("metadata", {})
        )
        return {"metadata": metadata}

    def _check_done(self, state: Any) -> str:
        """Kondisi selesai. Jika plan kosong, maka stop."""
        metadata = (
            getattr(state, "metadata", {})
            if not isinstance(state, dict)
            else state.get("metadata", {})
        )
        plan = metadata.get("plan", [])
        return "end" if len(plan) == 0 else "continue"

    def health_check(self) -> HealthStatus:
        """Kondisi agen."""
        return HealthStatus(
            status=HealthStatusEnum.HEALTHY,
            checks=[
                ComponentHealth(
                    name="finance_agent_tools", status=HealthStatusEnum.HEALTHY
                ),
                ComponentHealth(
                    name="finance_agent_graph",
                    status=HealthStatusEnum.HEALTHY
                    if self.compiled_graph
                    else HealthStatusEnum.DEGRADED,
                ),
            ],
        )
