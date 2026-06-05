"""Base class untuk tools dalam Agent Framework.

Module ini menyediakan `BaseTool` yang merupakan turunan dari
pydantic.BaseModel untuk mendefinisikan interface tool yang konsisten,
lengkap dengan input validation dan output formatting.
"""

from __future__ import annotations

import inspect
import logging
from collections.abc import Callable
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, create_model


logger = logging.getLogger(__name__)

# Generic type variable untuk input/output Pydantic schemas
T_In = TypeVar("T_In", bound=BaseModel)
T_Out = TypeVar("T_Out")


class BaseTool(BaseModel, Generic[T_In]):
    """Base class untuk semua Agent Tools.

    Attributes:
        name: Nama tool (huruf kecil, tanpa spasi).
        description: Deskripsi lengkap tentang fungsi tool ini (penting untuk LLM).
        args_schema: Pydantic model class yang mendefinisikan skema input.
        return_direct: Jika True, kembalikan output langsung ke user (stop agent loop).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., description="Nama tool, e.g., 'calculator'")
    description: str = Field(..., description="Deskripsi lengkap untuk prompt LLM")
    args_schema: type[BaseModel] | None = Field(default=None)
    return_direct: bool = Field(default=False)

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Eksekusi logika sinkron dari tool. Harus di-override subclass."""
        raise NotImplementedError("Tool ini tidak mendukung eksekusi sinkron.")

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Eksekusi logika asinkron dari tool (opsional)."""
        raise NotImplementedError("Tool ini tidak mendukung eksekusi asinkron.")

    def run(self, input_data: Any) -> Any:
        """Jalankan tool dengan validasi input.

        Args:
            input_data: Input berupa dict, Pydantic model, atau single value.

        Returns:
            Hasil eksekusi tool.
        """
        parsed_args, parsed_kwargs = self._parse_input(input_data)
        logger.debug("Menjalankan tool '%s' dengan input: %s", self.name, input_data)
        try:
            return self._run(*parsed_args, **parsed_kwargs)
        except Exception as e:
            logger.error("Error pada tool '%s': %s", self.name, str(e))
            return f"Error eksekusi tool '{self.name}': {e!s}"

    async def arun(self, input_data: Any) -> Any:
        """Jalankan tool asinkron dengan validasi input."""
        parsed_args, parsed_kwargs = self._parse_input(input_data)
        logger.debug(
            "Menjalankan (async) tool '%s' dengan input: %s", self.name, input_data
        )
        try:
            # Fallback ke sinkron jika _arun tidak diimplementasikan
            try:
                return await self._arun(*parsed_args, **parsed_kwargs)
            except NotImplementedError:
                return self._run(*parsed_args, **parsed_kwargs)
        except Exception as e:
            logger.error("Error pada async tool '%s': %s", self.name, str(e))
            return f"Error eksekusi tool '{self.name}': {e!s}"

    def _parse_input(self, input_data: Any) -> tuple[tuple[Any, ...], dict[str, Any]]:
        """Parse input_data menggunakan args_schema (jika ada)."""
        if self.args_schema is None:
            # Jika tidak ada schema yang ketat
            if isinstance(input_data, dict):
                return (), input_data
            if isinstance(input_data, tuple):
                return input_data, {}
            return (input_data,), {}

        # Jika input sudah berupa instance dari args_schema
        if isinstance(input_data, self.args_schema):
            return (), input_data.model_dump()

        # Validasi dict menggunakan args_schema
        if isinstance(input_data, dict):
            validated = self.args_schema(**input_data)
            return (), validated.model_dump()

        # Input adalah single value, mencoba map ke single field schema
        if len(self.args_schema.model_fields) == 1:
            field_name = next(iter(self.args_schema.model_fields))
            validated = self.args_schema(**{field_name: input_data})
            return (), validated.model_dump()

        raise ValueError(
            f"Input tidak cocok dengan schema tool '{self.name}'. "
            f"Diharapkan mapping untuk: {list(self.args_schema.model_fields.keys())}"
        )

    def to_openai_function(self) -> dict[str, Any]:
        """Konversi tool definition ke format OpenAI function calling."""
        func_dict: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
        }
        if self.args_schema:
            schema = self.args_schema.model_json_schema()
            # Bersihkan properti internal yang tidak didukung LLM
            schema.pop("title", None)
            schema.pop("description", None)
            func_dict["parameters"] = schema
        else:
            func_dict["parameters"] = {"type": "object", "properties": {}}
        return func_dict


def tool(name: str, description: str) -> Callable[[Callable[..., Any]], BaseTool]:
    """Decorator pembantu untuk mengubah fungsi Python biasa menjadi BaseTool.

    Args:
        name: Nama tool.
        description: Deskripsi fungsi tool.
    """

    def decorator(func: Callable[..., Any]) -> BaseTool:
        # Generate Pydantic schema dari function signature
        sig = inspect.signature(func)
        fields: dict[str, Any] = {}
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            annotation = (
                param.annotation
                if param.annotation is not inspect.Parameter.empty
                else Any
            )
            default = (
                param.default if param.default is not inspect.Parameter.empty else ...
            )
            fields[param_name] = (annotation, default)

        schema_class = create_model(f"{name.capitalize()}Schema", **fields)

        class FunctionalTool(BaseTool):
            def _run(self, *args: Any, **kwargs: Any) -> Any:
                return func(*args, **kwargs)

            # Jika fungsi tersebut coroutine
            if inspect.iscoroutinefunction(func):

                async def _arun(self, *args: Any, **kwargs: Any) -> Any:
                    return await func(*args, **kwargs)

        return FunctionalTool(
            name=name, description=description, args_schema=schema_class
        )

    return decorator
