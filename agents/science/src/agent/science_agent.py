"""Agen Sains dengan arsitektur ReAct."""

import logging
from typing import Any

from langgraph.graph import StateGraph

from agents.science.src.tools.science_tools import (
    ExperimentDesignerTool,
    LiteratureSearchTool,
    MolecularSimTool,
    StatisticalTestTool,
)
from shared.agent.base import BaseAgent
from shared.agent.graphs.react import create_react_graph
from shared.models import AgentState, ComponentHealth, HealthStatus, HealthStatusEnum


logger = logging.getLogger(__name__)


class ScienceAgent(BaseAgent):
    """Science Agent berbasis ReAct."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Mendaftarkan tool sains."""
        self.tools.register(LiteratureSearchTool())
        self.tools.register(ExperimentDesignerTool())
        self.tools.register(MolecularSimTool())
        self.tools.register(StatisticalTestTool())
        logger.info("Science Agent: Default tools berhasil diregistrasi.")

    def build_graph(self) -> StateGraph:
        """Mengonstruksi ReAct StateGraph."""
        return create_react_graph(
            state_schema=AgentState,
            reasoning_node=self._llm_step,
            action_node=self._tools_step,
            continue_condition=self._should_continue,
        )

    def _llm_step(self, state: Any) -> dict[str, Any]:
        """Eksekusi LLM."""
        logger.info("ScienceAgent LLM Step.")
        messages = (
            getattr(state, "messages", [])
            if not isinstance(state, dict)
            else state.get("messages", [])
        )
        return {"messages": messages}

    def _tools_step(self, state: Any) -> dict[str, Any]:
        """Eksekusi Tools."""
        logger.info("ScienceAgent Tools Step.")
        messages = (
            getattr(state, "messages", [])
            if not isinstance(state, dict)
            else state.get("messages", [])
        )
        return {"messages": messages}

    def _should_continue(self, state: Any) -> str:
        """Kondisi perulangan ReAct."""
        return "end"

    def health_check(self) -> HealthStatus:
        """Kondisi agen."""
        return HealthStatus(
            status=HealthStatusEnum.HEALTHY,
            checks=[
                ComponentHealth(name="science_tools", status=HealthStatusEnum.HEALTHY),
                ComponentHealth(
                    name="science_graph",
                    status=HealthStatusEnum.HEALTHY
                    if self.compiled_graph
                    else HealthStatusEnum.DEGRADED,
                ),
            ],
        )
