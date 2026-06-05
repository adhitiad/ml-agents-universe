"""Agen NLP dengan arsitektur ReAct."""

import logging
from typing import Any

from langgraph.graph import StateGraph

from agents.nlp.src.tools.nlp_tools import (
    EntityExtractorTool,
    SentimentAnalyzerTool,
    TextCleanerTool,
    TokenizerTool,
    WebScraperTool,
)
from shared.agent.base import BaseAgent
from shared.agent.graphs.react import create_react_graph
from shared.models import AgentState, ComponentHealth, HealthStatus, HealthStatusEnum


logger = logging.getLogger(__name__)


class NLPAgent(BaseAgent):
    """NLP Agent berbasis ReAct."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Mendaftarkan tool NLP ke dalam internal tool registry."""
        self.tools.register(WebScraperTool())
        self.tools.register(TextCleanerTool())
        self.tools.register(TokenizerTool())
        self.tools.register(SentimentAnalyzerTool())
        self.tools.register(EntityExtractorTool())
        logger.info("NLP Agent: Default tools berhasil diregistrasi.")

    def build_graph(self) -> StateGraph:
        """Mengonstruksi ReAct StateGraph."""
        return create_react_graph(
            state_schema=AgentState,
            reasoning_node=self._reasoning_step,
            action_node=self._action_step,
            continue_condition=self._continue_routing,
        )

    def _reasoning_step(self, state: Any) -> dict[str, Any]:
        """Node LLM Reasoning Mock. Di Prod, panggil model bahasa di sini."""
        logger.info("NLPAgent Reasoning Step.")
        messages = getattr(state, "messages", []) if not isinstance(state, dict) else state.get("messages", [])

        # Simulasi LLM output dengan mengambil alat yang relevan
        next_agent = getattr(state, "next_agent", None) if not isinstance(state, dict) else state.get("next_agent", None)
        if not next_agent: # Simulasi routing
            pass

        # Untuk framework, kembalikan state yang diubah.
        return {"messages": messages}

    def _action_step(self, state: Any) -> dict[str, Any]:
        """Node Action Execution Mock."""
        logger.info("NLPAgent Action Step.")
        messages = getattr(state, "messages", []) if not isinstance(state, dict) else state.get("messages", [])
        return {"messages": messages}

    def _continue_routing(self, state: Any) -> str:
        """Routing untuk ReAct: memutuskan apakah loop ReAct selesai atau belum."""
        # Simulasi kondisi (selalu stop untuk mencegah infinite loop di dummy test)
        return "end"

    def health_check(self) -> HealthStatus:
        """Kondisi agen."""
        return HealthStatus(
            status=HealthStatusEnum.HEALTHY,
            checks=[
                ComponentHealth(name="nlp_agent_tools", status=HealthStatusEnum.HEALTHY),
                ComponentHealth(name="nlp_agent_graph", status=HealthStatusEnum.HEALTHY if self.compiled_graph else HealthStatusEnum.DEGRADED),
            ]
        )
