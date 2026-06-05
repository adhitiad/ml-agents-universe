"""Composite tools untuk mengeksekusi rangkaian tool.

Module ini menyediakan `CompositeTool`, sebuah tool khusus yang terdiri dari
rangkaian eksekusi beberapa tools lain secara sekuensial (tool chains).
Berguna untuk membungkus multi-step operation menjadi satu fungsi yang dipanggil LLM.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from shared.agent.tools.base import BaseTool


logger = logging.getLogger(__name__)


class CompositeInputSchema(BaseModel):
    """Input generik untuk composite tool. Menampung payload awal."""

    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary payload masukan utama untuk rantai tool.",
    )


class CompositeTool(BaseTool):
    """Sebuah tool yang secara internal memanggil chain dari tools lain.

    Output dari satu tool (harus berupa dict) akan digabungkan atau di-pass
    ke tool berikutnya.
    """

    args_schema: type[BaseModel] | None = CompositeInputSchema
    _tools_chain: list[BaseTool] = []

    def __init__(
        self, name: str, description: str, tools_chain: list[BaseTool], **kwargs: Any
    ) -> None:
        super().__init__(name=name, description=description, **kwargs)
        self._tools_chain = tools_chain

    def _run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Jalankan tool chain secara sekuensial.

        Output tiap step diharapkan merupakan dict yang akan di-update ke payload state.
        """
        current_state = dict(payload)
        logger.info(
            "Memulai eksekusi CompositeTool '%s' dengan %d langkah",
            self.name,
            len(self._tools_chain),
        )

        for step_idx, step_tool in enumerate(self._tools_chain):
            logger.debug(
                "Composite step %d: Menjalankan '%s'", step_idx + 1, step_tool.name
            )

            try:
                # Mengandalkan alat untuk mengekstrak param yang dibutuhkan dari current_state.
                # Asumsi step_tool bisa menerima sisa parameter yang tidak dibutuhkan (atau kita filter).
                result = step_tool.run(current_state)

                # Update current state
                if isinstance(result, dict):
                    current_state.update(result)
                else:
                    current_state[f"{step_tool.name}_result"] = result

            except Exception as e:
                logger.error(
                    "CompositeTool '%s' terhenti di langkah '%s': %s",
                    self.name,
                    step_tool.name,
                    str(e),
                )
                current_state["error"] = f"Terhenti di langkah {step_tool.name}: {e!s}"
                break

        return current_state
