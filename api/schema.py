from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., description="Pertanyaan atau perintah dari pengguna")
    provider: str = Field(
        default="ollama", description="LLM Provider (ollama, openai, dll)"
    )
    model: str = Field(default="", description="Nama model spesifik (opsional)")


class ChatResponse(BaseModel):
    query: str = Field(..., description="Pertanyaan asli")
    final_answer: str = Field(..., description="Jawaban hasil sintesis Supervisor")
    experts_consulted: list[str] = Field(
        default_factory=list, description="Daftar pakar yang dilibatkan"
    )
    execution_time: float = Field(..., description="Waktu eksekusi dalam detik")
