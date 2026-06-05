"""Tool Registry untuk menyimpan dan mencari tools.

Module ini menyediakan `ToolRegistry` yang digunakan oleh AgentOrchestrator
untuk mencari dan menyuntikkan tool secara dinamis berdasarkan domain atau kategori.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable

from shared.agent.tools.base import BaseTool


logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry tersentralisasi untuk menyimpan koleksi BaseTool.

    Memungkinkan registrasi tool baru secara dinamis, filter berdasarkan tag/domain,
    dan mempermudah passing multiple tools ke dalam LLM context.
    """

    def __init__(self) -> None:
        """Inisialisasi ToolRegistry kosong."""
        self._tools: dict[str, BaseTool] = {}
        self._tags: dict[str, set[str]] = {}

    def register(self, tool: BaseTool, tags: list[str] | None = None) -> None:
        """Daftarkan tool ke dalam registry.

        Args:
            tool: Instance dari BaseTool.
            tags: Daftar tag string (misal: "finance", "calculator").
        """
        if tool.name in self._tools:
            logger.warning("Overwriting tool yang sudah ada: '%s'", tool.name)

        self._tools[tool.name] = tool

        tags = tags or []
        for tag in tags:
            if tag not in self._tags:
                self._tags[tag] = set()
            self._tags[tag].add(tool.name)

        logger.debug("Tool '%s' terdaftar dengan tags: %s", tool.name, tags)

    def register_multiple(
        self, tools: Iterable[BaseTool], tags: list[str] | None = None
    ) -> None:
        """Mendaftarkan beberapa tool sekaligus."""
        for t in tools:
            self.register(t, tags)

    def get_tool(self, name: str) -> BaseTool | None:
        """Ambil tool berdasarkan nama."""
        return self._tools.get(name)

    def get_tools_by_tag(self, tag: str) -> list[BaseTool]:
        """Ambil daftar tool yang memiliki tag tertentu."""
        tool_names = self._tags.get(tag, set())
        return [self._tools[name] for name in tool_names if name in self._tools]

    def get_all_tools(self) -> list[BaseTool]:
        """Ambil semua tool yang terdaftar."""
        return list(self._tools.values())

    def get_openai_tools(self, tags: list[str] | None = None) -> list[dict]:
        """Mengembalikan list of dict definition dalam format OpenAI function.

        Args:
            tags: Jika diberikan, hanya filter tool berdasarkan tags.

        Returns:
            Daftar dict format function untuk dilempar ke OpenAI API.
        """
        tools_to_convert: list[BaseTool] = []

        if not tags:
            tools_to_convert = self.get_all_tools()
        else:
            seen: set[str] = set()
            for tag in tags:
                for t in self.get_tools_by_tag(tag):
                    if t.name not in seen:
                        seen.add(t.name)
                        tools_to_convert.append(t)

        return [
            {"type": "function", "function": t.to_openai_function()}
            for t in tools_to_convert
        ]

    def clear(self) -> None:
        """Bersihkan semua tool dari registry."""
        self._tools.clear()
        self._tags.clear()
        logger.debug("ToolRegistry dibersihkan.")
