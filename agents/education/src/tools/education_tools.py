"""Tools khusus untuk Education Agent (IRT dan BKT)."""

import math
from typing import Any

from pydantic import BaseModel, Field

from shared.agent.tools.base import BaseTool


# ==========================================
# Input Schemas
# ==========================================
class IRTInput(BaseModel):
    ability: float = Field(..., description="Kemampuan siswa (theta).")
    difficulty: float = Field(..., description="Tingkat kesulitan soal (b).")
    discrimination: float = Field(default=1.0, description="Daya beda soal (a).")

class BKTInput(BaseModel):
    prior_prob: float = Field(..., description="Probabilitas awal penguasaan.")
    correct_answer: bool = Field(..., description="Apakah jawaban murid benar?")

class RecommendInput(BaseModel):
    topic: str = Field(..., description="Topik saat ini.")

class AssessmentInput(BaseModel):
    difficulty_target: float = Field(..., description="Target rata-rata kesulitan assessment.")


# ==========================================
# Tool Implementations
# ==========================================
class IRTCalculatorTool(BaseTool):
    """Tool untuk menghitung probabilitas siswa menjawab benar (Model IRT 2PL)."""

    args_schema: type[BaseModel] | None = IRTInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="irt_calculator", description="Hitung probabilitas benar via IRT.", **kwargs)

    def _run(self, ability: float, difficulty: float, discrimination: float = 1.0) -> dict[str, Any]:
        # Rumus standar IRT 2PL
        exponent = -1.7 * discrimination * (ability - difficulty)
        # Cegah overflow
        if exponent > 500:
            prob = 0.0
        elif exponent < -500:
            prob = 1.0
        else:
            prob = 1.0 / (1.0 + math.exp(exponent))

        return {"prob_correct": prob}


class KnowledgeTracerTool(BaseTool):
    """Tool untuk update model BKT (Bayesian Knowledge Tracing)."""

    args_schema: type[BaseModel] | None = BKTInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="knowledge_tracer", description="Update Bayesian probability penguasaan.", **kwargs)

    def _run(self, prior_prob: float, correct_answer: bool) -> dict[str, Any]:
        # Parameter standar (Mock)
        p_guess = 0.2
        p_slip = 0.1

        if correct_answer:
            p_obs = prior_prob * (1 - p_slip) + (1 - prior_prob) * p_guess
            new_prob = (prior_prob * (1 - p_slip)) / p_obs if p_obs > 0 else 0
        else:
            p_obs = prior_prob * p_slip + (1 - prior_prob) * (1 - p_guess)
            new_prob = (prior_prob * p_slip) / p_obs if p_obs > 0 else 0

        return {"new_knowledge_prob": new_prob}


class ContentRecommenderTool(BaseTool):
    """Tool untuk merekomendasikan topik materi berikutnya."""

    args_schema: type[BaseModel] | None = RecommendInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="content_recommender", description="Rekomendasi adaptif.", **kwargs)

    def _run(self, topic: str) -> dict[str, Any]:
        return {"recommended_topic": f"{topic}_advanced"}


class AssessmentGeneratorTool(BaseTool):
    """Tool untuk membuat soal assessment."""

    args_schema: type[BaseModel] | None = AssessmentInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="assessment_generator", description="Buat kuis berdasarkan target kesulitan.", **kwargs)

    def _run(self, difficulty_target: float) -> dict[str, Any]:
        return {
            "questions": 10,
            "avg_difficulty": difficulty_target,
            "status": "generated"
        }
