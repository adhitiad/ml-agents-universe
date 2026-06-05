"""Agen Matematika dengan arsitektur Plan-and-Execute."""

import logging
from typing import Any

from langgraph.graph import StateGraph

from agents.mathematics.src.tools.math_tools import (
    LaTeXConverterTool,
    MathSearchTool,
    ProofCheckerTool,
    SymbolicSolverTool,
)
from shared.agent.base import BaseAgent
from shared.agent.graphs.plan_execute import create_plan_execute_graph
from shared.models import AgentState, ComponentHealth, HealthStatus, HealthStatusEnum


logger = logging.getLogger(__name__)


class MathAgent(BaseAgent):
    """Mathematics Agent berbasis Plan and Execute."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Mendaftarkan tool matematika."""
        self.tools.register(SymbolicSolverTool())
        self.tools.register(ProofCheckerTool())
        self.tools.register(LaTeXConverterTool())
        self.tools.register(MathSearchTool())
        logger.info("Math Agent: Default tools berhasil diregistrasi.")

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
        """Merencanakan langkah pembuktian teorema."""
        logger.info("MathAgent Planner Step.")
        metadata = (
            getattr(state, "metadata", {})
            if not isinstance(state, dict)
            else state.get("metadata", {})
        )
        plan = metadata.get("plan", ["step_1", "step_2", "conclusion"])
        metadata["plan"] = plan
        return {"metadata": metadata}

    def _executor_step(self, state: Any) -> dict[str, Any]:
        """Eksekusi pembuktian logis."""
        logger.info("MathAgent Executor Step.")
        metadata = (
            getattr(state, "metadata", {})
            if not isinstance(state, dict)
            else state.get("metadata", {})
        )
        plan = metadata.get("plan", [])
        if plan:
            current_step = plan.pop(0)
            logger.info("Mengeksekusi proof: %s", current_step)
        return {"metadata": metadata}

    def _replan_step(self, state: Any) -> dict[str, Any]:
        """Re-evaluasi rencana pembuktian jika ada kontradiksi."""
        logger.info("MathAgent Replan Step.")
        metadata = (
            getattr(state, "metadata", {})
            if not isinstance(state, dict)
            else state.get("metadata", {})
        )
        return {"metadata": metadata}

    def _check_done(self, state: Any) -> str:
        """Kondisi berhenti (Q.E.D)."""
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
                ComponentHealth(name="math_tools", status=HealthStatusEnum.HEALTHY),
                ComponentHealth(
                    name="math_graph",
                    status=HealthStatusEnum.HEALTHY
                    if self.compiled_graph
                    else HealthStatusEnum.DEGRADED,
                ),
            ],
        )
