"""Graph Templates.

Koleksi arsitektur topologi LangGraph siap pakai untuk diimplementasikan
ke dalam fungsi `build_graph()` dari domain agent.
"""

from shared.agent.graphs.builder import GraphBuilder
from shared.agent.graphs.plan_execute import create_plan_execute_graph
from shared.agent.graphs.react import create_react_graph
from shared.agent.graphs.supervisor import create_supervisor_graph


__all__ = [
    "GraphBuilder",
    "create_plan_execute_graph",
    "create_react_graph",
    "create_supervisor_graph",
]
