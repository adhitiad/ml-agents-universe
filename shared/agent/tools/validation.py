"""Sistem validasi Tool inputs dan outputs.

Validation engine ini bertindak sebagai safeguard untuk memastikan
bahwa output LLM cocok dengan schema input tool, dan output dari tool
valid sesuai schema yang dijanjikan.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from shared.agent.tools.base import BaseTool


logger = logging.getLogger(__name__)


class ToolValidator:
    """Engine untuk memvalidasi pemanggilan fungsi dan input schema LLM."""

    @staticmethod
    def validate_input(tool: BaseTool, input_data: Any) -> bool:
        """Periksa apakah input_data sah untuk argument tool.

        Args:
            tool: BaseTool yang akan dipanggil.
            input_data: Argumen dari LLM (biasanya dict hasil parsing JSON).

        Returns:
            True jika valid, False jika gagal.
        """
        if tool.args_schema is None:
            # Tidak ada skema ketat, bebas.
            return True

        try:
            # Coba bind input ke skema Pydantic
            if isinstance(input_data, dict):
                tool.args_schema(**input_data)
            elif isinstance(input_data, tool.args_schema):
                pass
            elif len(tool.args_schema.model_fields) == 1:
                field_name = next(iter(tool.args_schema.model_fields))
                tool.args_schema(**{field_name: input_data})
            else:
                return False
            return True

        except PydanticValidationError as e:
            logger.warning("ToolValidation gagal untuk tool '%s': %s", tool.name, e)
            return False
        except Exception:
            return False

    @staticmethod
    def format_validation_error(tool: BaseTool, input_data: Any) -> str:
        """Mengembalikan pesan error ramah LLM jika validasi input gagal.

        Ini sangat berguna dalam pattern self-correction, di mana LLM akan
        menerima pesan error ini lalu memperbaiki struktur JSON panggilannya.
        """
        if tool.args_schema is None:
            return "Input type error."

        try:
            if isinstance(input_data, dict):
                tool.args_schema(**input_data)
            else:
                return f"Format input salah. Harus berupa JSON/dict. Diberikan: {type(input_data)}"
        except PydanticValidationError as e:
            errors = e.errors()
            error_msgs = []
            for err in errors:
                loc = ".".join(map(str, err["loc"]))
                msg = err["msg"]
                error_msgs.append(f"- Field '{loc}': {msg}")

            return (
                f"Validasi argumen gagal untuk fungsi '{tool.name}':\n"
                + "\n".join(error_msgs)
                + f"\nHarap sesuaikan dengan schema: {list(tool.args_schema.model_fields.keys())}"
            )

        return "Unknown validation error."
