"""Supervisor Graph Template.

Pola ini menggunakan node utama (Supervisor) yang bertindak sebagai
router untuk memanggil agen spesifik ("pekerja") berdasarkan permintaan.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from langgraph.graph import END, StateGraph

from shared.agent.graphs.builder import GraphBuilder


logger = logging.getLogger(__name__)


def create_supervisor_graph(
    state_schema: type,
    supervisor_node: Any,
    worker_nodes: Mapping[str, Any],
    route_condition: Any,
) -> StateGraph:
    """Membangun graf multi-agent hierarchical (Supervisor).

    Topologi:
    START -> supervisor -> [route_condition]
                              |-> worker_1 -> supervisor
                              |-> worker_N -> supervisor
                              |-> "finish" -> END
    """
    builder = GraphBuilder(state_schema)

    builder.add_node("supervisor", supervisor_node)

    route_map: dict[str, str] = {"finish": END}

    for worker_name, worker_node in worker_nodes.items():
        builder.add_node(worker_name, worker_node)
        builder.add_edge(worker_name, "supervisor")
        route_map[worker_name] = worker_name

    builder.set_entry_point("supervisor")

    builder.add_conditional_edge(
        source="supervisor",
        condition_func=route_condition,
        route_map=route_map,
    )

    logger.info(
        "Supervisor Graph Template berhasil dikonstruksi dengan %d pekerja.",
        len(worker_nodes),
    )
    return builder.build()
