from __future__ import annotations

import logging
import os
from typing import Any

from langgraph.graph import END, StateGraph

from shared.agent.base import BaseAgent
from shared.models.base import AgentConfig, AgentState, HealthStatus, HealthStatusEnum
from shared.models.llm_provider import LLMManager


logger = logging.getLogger(__name__)


class RagAgent(BaseAgent):
    """Agen khusus untuk Local Document Scanner (RAG) tanpa akses internet."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        if config is None:
            # Fallback default configuration
            from shared.models.base import AgentDomain

            config = AgentConfig(
                name="rag_agent", domain=AgentDomain.SCIENCE
            )  # Menggunakan Science sementara jika tidak ada domain RAG

        super().__init__(config=config)
        self.llm = LLMManager.from_env()
        self.vector_store = None

        # Lazy load embeddings untuk mempercepat startup awal
        from langchain_community.embeddings import HuggingFaceEmbeddings

        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.db_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "data", "vector_db"
        )

    def init_vector_store(self):
        """Memuat ulang database FAISS dari disk."""
        if os.path.exists(self.db_path) and os.listdir(self.db_path):
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings
                from langchain_community.vectorstores import FAISS

                if not hasattr(self, "embeddings"):
                    self.embeddings = HuggingFaceEmbeddings(
                        model_name="all-MiniLM-L6-v2"
                    )

                self.vector_store = FAISS.load_local(
                    self.db_path, self.embeddings, allow_dangerous_deserialization=True
                )
                logger.info(f"Berhasil memuat database FAISS dari {self.db_path}")
            except Exception as e:
                logger.error(f"Gagal memuat FAISS: {e}")
        else:
            logger.info("Database vektor FAISS belum tersedia.")

    def _process_rag(self, state: Any) -> dict[str, Any]:
        """Node graph untuk memproses RAG."""
        messages = (
            state.get("messages", [])
            if isinstance(state, dict)
            else getattr(state, "messages", [])
        )
        if not messages:
            return state

        last_message = messages[-1]
        query = (
            last_message.content
            if hasattr(last_message, "content")
            else str(last_message)
        )

        # Inisialisasi vector store jika belum
        if not self.vector_store:
            self.init_vector_store()

        context = ""
        if self.vector_store:
            docs = self.vector_store.similarity_search(query, k=3)
            context = "\n".join([d.page_content for d in docs])

        if not context:
            response = "Saya belum memindai dokumen apapun di database FAISS."
        else:
            prompt = f"Berdasarkan dokumen berikut, jawab pertanyaan pengguna:\n\n{context}\n\nPertanyaan: {query}"
            ai_msg = self.llm.invoke(prompt)
            response = ai_msg.content if hasattr(ai_msg, "content") else str(ai_msg)

        new_msg = {"role": "assistant", "content": response}
        return {"messages": [*messages, new_msg]}

    def build_graph(self) -> StateGraph:
        """Membangun computational graph untuk RAG Agent."""
        # Menggunakan AgentState dan type ignore untuk kompatibilitas Pyright
        workflow = StateGraph(AgentState)  # type: ignore
        workflow.add_node("process_rag", self._process_rag)
        workflow.set_entry_point("process_rag")
        workflow.add_edge("process_rag", END)
        return workflow

    def health_check(self) -> HealthStatus:
        """Cek status agen RAG."""
        status = (
            HealthStatusEnum.HEALTHY if self.vector_store else HealthStatusEnum.DEGRADED
        )
        return HealthStatus(status=status)
