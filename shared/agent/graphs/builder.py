"""Custom Builder API untuk LangGraph.

Modul ini menyediakan wrapper di atas StateGraph untuk mempermudah
konstruksi topologi node dan edge tanpa harus menulis boilerplate secara berulang.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from langgraph.graph import END, StateGraph


logger = logging.getLogger(__name__)


class GraphBuilder:
    """Wrapper untuk StateGraph yang menyederhanakan registrasi node/edge."""

    def __init__(self, state_schema: type) -> None:
        self.graph = StateGraph(state_schema)
        self.entry_point_set = False

    def add_node(
        self, name: str, action: Callable[[Any], dict[str, Any]]
    ) -> GraphBuilder:
        """Tambahkan node eksekusi baru."""
        self.graph.add_node(name, action)
        logger.debug("Node ditambahkan: %s", name)
        return self

    def set_entry_point(self, node_name: str) -> GraphBuilder:
        """Set node awal graf."""
        self.graph.set_entry_point(node_name)
        self.entry_point_set = True
        logger.debug("Entry point di-set ke: %s", node_name)
        return self

    def add_edge(self, source: str, target: str) -> GraphBuilder:
        """Tambahkan jalur transisi biasa dari source ke target."""
        self.graph.add_edge(source, target)
        logger.debug("Edge ditambahkan: %s -> %s", source, target)
        return self

    def add_conditional_edge(
        self,
        source: str,
        condition_func: Callable[[Any], str],
        route_map: dict[str, str],
    ) -> GraphBuilder:
        """Tambahkan transisi kondisional berdasarkan fungsi kondisi."""
        self.graph.add_conditional_edges(
            source,
            condition_func,
            route_map,
        )
        logger.debug("Conditional Edge ditambahkan dari: %s", source)
        return self

    def set_finish_point(self, source: str) -> GraphBuilder:
        """Hubungkan node ke akhir siklus."""
        self.graph.add_edge(source, END)
        return self

    def build(self) -> StateGraph:
        """Mengembalikan instansiasi StateGraph."""
        if not self.entry_point_set:
            raise ValueError("Entry point belum di-set pada GraphBuilder.")
        return self.graph
