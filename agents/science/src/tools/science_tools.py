"""Tools khusus untuk Science Agent."""

from typing import Any

from pydantic import BaseModel, Field

from shared.agent.tools.base import BaseTool


# ==========================================
# Input Schemas
# ==========================================
class LitSearchInput(BaseModel):
    query: str = Field(..., description="Topik paper yang dicari.")


class ExpDesignInput(BaseModel):
    hypothesis: str = Field(..., description="Hipotesis eksperimen.")


class MolSimInput(BaseModel):
    smiles: str = Field(..., description="Molekul SMILES.")


class StatTestInput(BaseModel):
    experiment_id: str = Field(
        ..., description="ID Eksperimen untuk diuji secara statistik."
    )


# ==========================================
# Tool Implementations
# ==========================================
class LiteratureSearchTool(BaseTool):
    """Tool untuk mem-fetch literatur saintifik (mock PubMed/ArXiv)."""

    args_schema: type[BaseModel] | None = LitSearchInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="literature_search", description="Cari paper akademik.", **kwargs
        )

    def _run(self, query: str) -> dict[str, Any]:
        return {"query": query, "results": ["paper_1_doi", "paper_2_doi"]}


class ExperimentDesignerTool(BaseTool):
    """Tool untuk merancang variabel eksperimen."""

    args_schema: type[BaseModel] | None = ExpDesignInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="experiment_designer",
            description="Susun DOE dari hipotesis.",
            **kwargs,
        )

    def _run(self, hypothesis: str) -> dict[str, Any]:
        return {
            "hypothesis": hypothesis,
            "independent_vars": ["temp"],
            "dependent_vars": ["yield"],
        }


class MolecularSimTool(BaseTool):
    """Tool untuk memprediksi properti molekuler."""

    args_schema: type[BaseModel] | None = MolSimInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="molecular_sim", description="Prediksi properti dari SMILES.", **kwargs
        )

    def _run(self, smiles: str) -> dict[str, Any]:
        return {"smiles": smiles, "predicted_logS": -3.5, "toxicity_risk": 0.2}


class StatisticalTestTool(BaseTool):
    """Tool untuk menghitung signifikansi p-value."""

    args_schema: type[BaseModel] | None = StatTestInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="statistical_test", description="Uji p-value.", **kwargs)

    def _run(self, experiment_id: str) -> dict[str, Any]:
        if "invalid" in experiment_id.lower():
            return {"error": "Hypothesis belum diset. Gagal menjalankan uji statistik."}
        return {"experiment_id": experiment_id, "p_value": 0.03, "significant": True}
