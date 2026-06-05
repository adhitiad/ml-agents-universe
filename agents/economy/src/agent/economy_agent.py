"""Agen Ekonomi dengan arsitektur Hierarchical Multi-Agent."""

import logging
from typing import Any

from langgraph.graph import StateGraph

from agents.economy.src.tools.economy_tools import (
    MacroIndicatorTool,
    PolicyEvaluatorTool,
    SimulationRunnerTool,
    TradeFlowTool,
)
from shared.agent.base import BaseAgent
from shared.agent.graphs.supervisor import create_supervisor_graph
from shared.models import AgentState, ComponentHealth, HealthStatus, HealthStatusEnum


logger = logging.getLogger(__name__)


class EconomyAgent(BaseAgent):
    """Economy Agent berbasis Hierarchical Supervisor."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Mendaftarkan tool economy."""
        self.tools.register(SimulationRunnerTool())
        self.tools.register(PolicyEvaluatorTool())
        self.tools.register(MacroIndicatorTool())
        self.tools.register(TradeFlowTool())
        logger.info("Economy Agent: Default tools berhasil diregistrasi.")

    def build_graph(self) -> StateGraph:
        """Mengonstruksi Supervisor Graph."""
        # Agen anak: macro_agent dan policy_agent
        return create_supervisor_graph(
            state_schema=AgentState,
            supervisor_node=self._supervisor_step,
            worker_nodes={
                "macro_agent": self._macro_worker_step,
                "policy_agent": self._policy_worker_step,
            },
            route_condition=self._route_condition,
        )

    def _route_condition(self, state: Any) -> str:
        next_agent = getattr(state, "next_agent", None) if not isinstance(state, dict) else state.get("next_agent", None)
        return next_agent if next_agent in ["macro_agent", "policy_agent"] else "finish"

    def _supervisor_step(self, state: Any) -> dict[str, Any]:
        """Supervisor mendelegasikan tugas."""
        logger.info("EconomyAgent Supervisor Step.")
        next_agent = (
            getattr(state, "next_agent", None)
            if not isinstance(state, dict)
            else state.get("next_agent", None)
        )

        # Jika baru mulai, delegasikan ke macro_agent
        if not next_agent or next_agent not in [
            "macro_agent",
            "policy_agent",
            "FINISH",
        ]:
            next_agent = "macro_agent"

        return {"next_agent": next_agent}

    def _macro_worker_step(self, state: Any) -> dict[str, Any]:
        """Worker 1: Macro & Simulation Analysis."""
        logger.info("EconomyAgent Macro Worker Step.")
        return {"next_agent": "policy_agent"}

    def _policy_worker_step(self, state: Any) -> dict[str, Any]:
        """Worker 2: Policy Evaluation."""
        logger.info("EconomyAgent Policy Worker Step.")
        return {"next_agent": "FINISH"}

    def health_check(self) -> HealthStatus:
        """Kondisi agen."""
        return HealthStatus(
            status=HealthStatusEnum.HEALTHY,
            checks=[
                ComponentHealth(
                    name="economy_agent_tools", status=HealthStatusEnum.HEALTHY
                ),
                ComponentHealth(
                    name="economy_agent_graph",
                    status=HealthStatusEnum.HEALTHY
                    if self.compiled_graph
                    else HealthStatusEnum.DEGRADED,
                ),
            ],
        )
