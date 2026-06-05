"""Tools khusus untuk Entertainment Agent (Sistem Rekomendasi)."""

from typing import Any

from pydantic import BaseModel, Field

from shared.agent.tools.base import BaseTool


# ==========================================
# Input Schemas
# ==========================================
class UserProfileInput(BaseModel):
    user_id: str = Field(..., description="ID Pengguna.")


class ContentBasedInput(BaseModel):
    genre: str = Field(..., description="Genre target.")


class CollabFilterInput(BaseModel):
    user_id: str = Field(..., description="ID Pengguna untuk collaborative filtering.")


class TrendInput(BaseModel):
    category: str = Field(default="movies", description="Kategori tren.")


# ==========================================
# Tool Implementations
# ==========================================
class UserProfileTool(BaseTool):
    """Tool untuk mem-fetch profil dan histori user."""

    args_schema: type[BaseModel] | None = UserProfileInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="user_profile", description="Ambil histori pengguna.", **kwargs
        )

    def _run(self, user_id: str) -> dict[str, Any]:
        # Mock fetch (deteksi cold start)
        if user_id.startswith("new_"):
            return {"user_id": user_id, "history": []}
        return {"user_id": user_id, "history": ["item_1", "item_2"]}


class ContentBasedFilterTool(BaseTool):
    """Tool untuk rekomendasi berdasarkan konten/genre (cocok untuk cold-start)."""

    args_schema: type[BaseModel] | None = ContentBasedInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="content_based_filter",
            description="Rekomendasi berdasar genre.",
            **kwargs,
        )

    def _run(self, genre: str) -> dict[str, Any]:
        return {"recommended": [f"{genre}_top1", f"{genre}_top2"]}


class CollaborativeFilterTool(BaseTool):
    """Tool untuk rekomendasi berdasarkan user-item matrix."""

    args_schema: type[BaseModel] | None = CollabFilterInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="collaborative_filter",
            description="Rekomendasi kolaboratif.",
            **kwargs,
        )

    def _run(self, user_id: str) -> dict[str, Any]:
        if user_id.startswith("new_"):
            return {"error": "Cold start: Not enough data for collaborative filtering."}
        return {"recommended": ["item_3", "item_4"]}


class TrendAnalyzerTool(BaseTool):
    """Tool untuk mendeteksi tren saat ini."""

    args_schema: type[BaseModel] | None = TrendInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="trend_analyzer", description="Cek apa yang sedang populer.", **kwargs
        )

    def _run(self, category: str) -> dict[str, Any]:
        return {"category": category, "trending": ["trend_1", "trend_2"]}
