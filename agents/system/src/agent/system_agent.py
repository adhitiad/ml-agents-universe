"""Agen System/OS dengan arsitektur ReAct."""

import logging
from typing import Any

from langgraph.graph import StateGraph

from agents.system.src.tools.file_tools import (
    ListDirectoryTool,
    ReadFileTool,
    WriteFileTool,
)
from shared.agent.base import BaseAgent
from shared.agent.graphs.react import create_react_graph
from shared.models import AgentState, ComponentHealth, HealthStatus, HealthStatusEnum


logger = logging.getLogger(__name__)


class SystemAgent(BaseAgent):
    """System Agent berbasis ReAct untuk otomasi desktop."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Mendaftarkan tool OS/File ke dalam internal tool registry."""
        from agents.system.src.tools.computer_tools import get_computer_tools
        from agents.system.src.tools.os_tools import RunCommandTool

        self.tools.register(ReadFileTool())
        self.tools.register(WriteFileTool())
        self.tools.register(ListDirectoryTool())
        self.tools.register(RunCommandTool())
        self.tools.register_multiple(
            get_computer_tools(), tags=["system", "rpa", "desktop"]
        )

    def build_graph(self) -> StateGraph:
        """Mengonstruksi ReAct StateGraph."""
        return create_react_graph(
            state_schema=AgentState,
            reasoning_node=self._reasoning_step,
            action_node=self._action_step,
            continue_condition=self._continue_routing,
        )

    def _reasoning_step(self, state: Any) -> dict[str, Any]:
        """Memanggil LLM dengan tool binding."""
        from langchain_core.messages import (
            AIMessage,
            BaseMessage,
            HumanMessage,
            SystemMessage,
        )

        from shared.models.llm_provider import LLMManager

        llm = LLMManager.from_env()
        tools = [t for t in self.tools.get_all_tools()]
        llm_with_tools = llm.bind_tools([t.to_openai_function() for t in tools])

        system_prompt = (
            "Kamu adalah System Automation AI Agent. Kamu memiliki akses langsung ke OS dan file system pengguna.\n"
            "Tugasmu adalah secara cerdas mengidentifikasi kapan harus menggunakan tools yang tersedia untuk memenuhi "
            "permintaan pengguna. \n\n"
            "PENTING: Pengguna seringkali menggunakan bahasa kasual atau kata ganti acak, seperti:\n"
            "- 'tolong lihat isi', 'cek file', 'kasih tau ada apa' -> Gunakan ReadFileTool\n"
            "- 'catat ini', 'tuliskan', 'simpan ke' -> Gunakan WriteFileTool\n"
            "- 'ada folder apa saja', 'cek isi direktori' -> Gunakan ListDirectoryTool\n"
            "- 'jalankan', 'eksekusi perintah', 'buka program' -> Gunakan RunCommandTool\n\n"
            "Meskipun perintahnya tidak baku, asalkan berkaitan dengan operasi OS atau file, JANGAN PERNAH menolak atau "
            "mengatakan tidak bisa. Segera panggil Tool yang tepat secara asinkron/langsung untuk mendapatkan hasilnya "
            "sebelum menjawab pengguna."
        )

        # Handle Pydantic state dict
        messages = (
            state.get("messages", [])
            if isinstance(state, dict)
            else getattr(state, "messages", [])
        )

        lc_messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]
        for msg in messages:
            if isinstance(msg, dict):
                if msg.get("role") == "user":
                    lc_messages.append(HumanMessage(content=msg.get("content", "")))
                elif msg.get("role") == "assistant":
                    if "tool_calls" in msg:
                        lc_messages.append(
                            AIMessage(
                                content=msg.get("content", ""),
                                tool_calls=msg["tool_calls"],
                            )
                        )
                    else:
                        lc_messages.append(AIMessage(content=msg.get("content", "")))
                elif msg.get("role") == "tool":
                    from langchain_core.messages import ToolMessage

                    lc_messages.append(
                        ToolMessage(
                            content=msg.get("content", ""),
                            tool_call_id=msg.get("tool_call_id", ""),
                        )
                    )
            else:
                lc_messages.append(msg)

        logger.info(f"SystemAgent Reasoning Step. Memanggil LLM: {llm}")
        response = llm_with_tools.invoke(lc_messages)

        new_msg: dict[str, Any] = {"role": "assistant", "content": response.content}
        if hasattr(response, "tool_calls") and response.tool_calls:
            new_msg["tool_calls"] = response.tool_calls

        return {"messages": [*messages, new_msg]}

    def _action_step(self, state: Any) -> dict[str, Any]:
        """Node Action Execution untuk memanggil tool."""
        logger.info("SystemAgent Action Step.")
        messages = (
            state.get("messages", [])
            if isinstance(state, dict)
            else getattr(state, "messages", [])
        )
        last_msg = messages[-1] if messages else {}

        new_messages = list(messages)
        if isinstance(last_msg, dict) and "tool_calls" in last_msg:
            for tc in last_msg["tool_calls"]:
                tool_name = tc["name"]
                tool_args = tc["args"]
                tool_id = tc["id"]

                try:
                    tool = self.tools.get_tool(tool_name)
                    if tool:
                        result = tool.run(tool_args)
                        new_messages.append(
                            {
                                "role": "tool",
                                "content": str(result),
                                "tool_call_id": tool_id,
                            }
                        )
                    else:
                        new_messages.append(
                            {
                                "role": "tool",
                                "content": f"Tool {tool_name} not found",
                                "tool_call_id": tool_id,
                            }
                        )
                except Exception as e:
                    new_messages.append(
                        {
                            "role": "tool",
                            "content": f"Error: {e!s}",
                            "tool_call_id": tool_id,
                        }
                    )

        return {"messages": new_messages}

    def _continue_routing(self, state: Any) -> str:
        """Routing untuk ReAct: memutuskan apakah loop ReAct selesai atau belum."""
        messages = (
            state.get("messages", [])
            if isinstance(state, dict)
            else getattr(state, "messages", [])
        )
        if messages and isinstance(messages[-1], dict) and "tool_calls" in messages[-1]:
            return "continue"
        return "end"

    def health_check(self) -> HealthStatus:
        """Kondisi agen."""
        return HealthStatus(
            status=HealthStatusEnum.HEALTHY,
            checks=[
                ComponentHealth(
                    name="system_agent_tools", status=HealthStatusEnum.HEALTHY
                ),
                ComponentHealth(
                    name="system_agent_graph",
                    status=HealthStatusEnum.HEALTHY
                    if self.compiled_graph
                    else HealthStatusEnum.DEGRADED,
                ),
            ],
        )
