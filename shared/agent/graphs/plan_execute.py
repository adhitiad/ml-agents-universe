"""Plan-and-Execute Graph Template.

Pola ini memisahkan agen menjadi dua fase: Perencana (Planner) yang
memecah tugas menjadi langkah-langkah, dan Eksekutor (Executor) yang
menyelesaikan langkah-langkah tersebut secara iteratif.
Cocok untuk tugas kompleks (Coding, Data Analysis panjang).
"""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, StateGraph

from shared.agent.graphs.builder import GraphBuilder


logger = logging.getLogger(__name__)


def create_plan_execute_graph(
    state_schema: type,
    planner_node: Any,
    executor_node: Any,
    replan_node: Any,
    check_done_condition: Any,
) -> StateGraph:
    """Membangun graf Plan and Execute.

    Topologi:
    START -> planner -> executor -> replan -> [check_done]
                                                |-> "continue" -> executor
                                                |-> "end" -> END
    """
    builder = GraphBuilder(state_schema)

    builder.add_node("planner", planner_node)
    builder.add_node("executor", executor_node)
    builder.add_node("replan", replan_node)

    builder.set_entry_point("planner")

    builder.add_edge("planner", "executor")
    builder.add_edge("executor", "replan")

    builder.add_conditional_edge(
        source="replan",
        condition_func=check_done_condition,
        route_map={
            "continue": "executor",
            "end": END,
        },
    )

    logger.info("Plan-and-Execute Graph Template berhasil dikonstruksi.")
    return builder.build()
