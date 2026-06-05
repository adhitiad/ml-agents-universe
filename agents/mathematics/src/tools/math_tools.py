"""Tools khusus untuk Mathematics Agent."""

from typing import Any

from pydantic import BaseModel, Field

from shared.agent.tools.base import BaseTool


# ==========================================
# Input Schemas
# ==========================================
class SolverInput(BaseModel):
    equation: str = Field(..., description="Persamaan matematis untuk diselesaikan.")


class ProofCheckerInput(BaseModel):
    statement: str = Field(..., description="Pernyataan logis.")
    justification: str = Field(..., description="Alasan logis.")


class LatexInput(BaseModel):
    math_text: str = Field(..., description="Teks matematika biasa.")


class MathSearchInput(BaseModel):
    concept: str = Field(..., description="Konsep atau teorema yang dicari.")


# ==========================================
# Tool Implementations
# ==========================================
class SymbolicSolverTool(BaseTool):
    """Tool untuk memecahkan persamaan simbolik (mock sympy)."""

    args_schema: type[BaseModel] | None = SolverInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="symbolic_solver",
            description="Selesaikan persamaan aljabar.",
            **kwargs,
        )

    def _run(self, equation: str) -> dict[str, Any]:
        # Mock eval sederhana
        res = "x = 0"
        if "x+1=2" in equation.replace(" ", ""):
            res = "x = 1"
        return {"equation": equation, "solution": res}


class ProofCheckerTool(BaseTool):
    """Tool untuk memverifikasi validitas logika suatu langkah."""

    args_schema: type[BaseModel] | None = ProofCheckerInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="proof_checker", description="Verifikasi langkah pembuktian.", **kwargs
        )

    def _run(self, statement: str, justification: str) -> dict[str, Any]:
        if "invalid" in statement.lower() or "invalid" in justification.lower():
            return {"is_valid": False, "reason": "Logika tidak terbukti."}
        return {"is_valid": True, "reason": "Tervalidasi secara aksiomatik."}


class LaTeXConverterTool(BaseTool):
    """Tool untuk mengubah teks ke format LaTeX."""

    args_schema: type[BaseModel] | None = LatexInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="latex_converter", description="Format ke LaTeX.", **kwargs
        )

    def _run(self, math_text: str) -> dict[str, Any]:
        return {"latex": f"\\begin{{equation}} {math_text} \\end{{equation}}"}


class MathSearchTool(BaseTool):
    """Tool untuk mencari literatur atau aksioma matematika."""

    args_schema: type[BaseModel] | None = MathSearchInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="math_search", description="Cari definisi teorema.", **kwargs
        )

    def _run(self, concept: str) -> dict[str, Any]:
        return {"concept": concept, "definition": f"Definisi standar untuk {concept}."}
