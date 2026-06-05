"""ReAct (Reason and Act) Graph Template.

Pola ini sangat cocok untuk general-purpose agents yang membaca input,
berpikir, memilih tool, mengeksekusi tool, lalu merangkum hasil.
"""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, StateGraph

from shared.agent.graphs.builder import GraphBuilder


logger = logging.getLogger(__name__)


def create_react_graph(
    state_schema: type,
    reasoning_node: Any,
    action_node: Any,
    continue_condition: Any,
) -> StateGraph:
    """Membangun graf LangGraph untuk pola ReAct.

    Topologi:
    START -> reasoning -> [continue_condition]
                              |-> "tools" -> action_node -> reasoning
                              |-> "end" -> END

    Args:
        state_schema: Pydantic model class untuk state (e.g. AgentState).
        reasoning_node: Callable/Fungsi untuk memanggil LLM (berpikir).
        action_node: Callable/Fungsi untuk mengeksekusi tools.
        continue_condition: Callable pengambil keputusan rute (apakah butuh tool atau selesai).
    """
    builder = GraphBuilder(state_schema)

    # Definisi node
    builder.add_node("reason", reasoning_node)
    builder.add_node("action", action_node)

    # Definisi Edge
    builder.set_entry_point("reason")

    builder.add_conditional_edge(
        source="reason",
        condition_func=continue_condition,
        route_map={
            "continue": "action",
            "end": END,
        },
    )

    builder.add_edge("action", "reason")

    logger.info("ReAct Graph Template berhasil dikonstruksi.")
    return builder.build()
