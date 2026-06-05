"""Agen Entertainment dengan arsitektur ReAct."""

import logging
from typing import Any

from langgraph.graph import StateGraph

from agents.entertainment.src.tools.entertainment_tools import (
    CollaborativeFilterTool,
    ContentBasedFilterTool,
    TrendAnalyzerTool,
    UserProfileTool,
)
from shared.agent.base import BaseAgent
from shared.agent.graphs.react import create_react_graph
from shared.models import AgentState, ComponentHealth, HealthStatus, HealthStatusEnum


logger = logging.getLogger(__name__)


class EntertainmentAgent(BaseAgent):
    """Entertainment Agent berbasis ReAct."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Mendaftarkan tool hiburan."""
        self.tools.register(UserProfileTool())
        self.tools.register(ContentBasedFilterTool())
        self.tools.register(CollaborativeFilterTool())
        self.tools.register(TrendAnalyzerTool())
        logger.info("Entertainment Agent: Default tools berhasil diregistrasi.")

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
        logger.info("EntertainmentAgent LLM Step.")
        messages = (
            getattr(state, "messages", [])
            if not isinstance(state, dict)
            else state.get("messages", [])
        )
        return {"messages": messages}

    def _tools_step(self, state: Any) -> dict[str, Any]:
        """Eksekusi Tools."""
        logger.info("EntertainmentAgent Tools Step.")
        messages = (
            getattr(state, "messages", [])
            if not isinstance(state, dict)
            else state.get("messages", [])
        )
        return {"messages": messages}

    def _should_continue(self, state: Any) -> str:
        """Kondisi perulangan ReAct."""
        # Secara logis akan lanjut ke tools jika ada tool_calls. Untuk mock, kita END.
        return "end"

    def health_check(self) -> HealthStatus:
        """Kondisi agen."""
        return HealthStatus(
            status=HealthStatusEnum.HEALTHY,
            checks=[
                ComponentHealth(
                    name="entertainment_tools", status=HealthStatusEnum.HEALTHY
                ),
                ComponentHealth(
                    name="entertainment_graph",
                    status=HealthStatusEnum.HEALTHY
                    if self.compiled_graph
                    else HealthStatusEnum.DEGRADED,
                ),
            ],
        )
