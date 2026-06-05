import logging

from langchain_core.runnables import RunnableConfig

from agents.system.src.agent.system_agent import SystemAgent
from shared.models.base import AgentConfig, AgentDomain


logger = logging.getLogger(__name__)


class AgentController:
    """Controller untuk menghubungkan UI PySide6 dengan LangGraph SystemAgent."""

    def __init__(self, provider: str = "ollama", model: str = "uis_quan"):
        self.provider = provider
        self.model = model
        self.agent: SystemAgent | None = None
        self.thread_id = "desktop_main_session"

        self._initialize_agent()

    def _initialize_agent(self):
        """Membuat instance agen beserta graph-nya."""
        config = AgentConfig(
            name="System Agent",
            domain=AgentDomain.SYSTEM,
            metadata={
                "llm_provider": self.provider,
                "llm_model": self.model,
                "max_loops": 3,
            }
        )
        try:
            self.agent = SystemAgent(config=config)
            # Compile graph yang otomatis mengaktifkan SQLite checkpointer
            self.agent.compile()
            logger.info(
                "AgentController: SystemAgent dan Graph berhasil diinisialisasi."
            )
        except Exception as e:
            logger.error(f"Gagal menginisialisasi SystemAgent: {e}")
            raise

    def get_chat_history(self) -> list[tuple[str, str]]:
        """Mengambil riwayat obrolan dari SQLite database untuk thread_id aktif."""
        if not self.agent or not self.agent.compiled_graph:
            return []

        config: RunnableConfig = {"configurable": {"thread_id": self.thread_id}}
        state = self.agent.compiled_graph.get_state(config)

        if not state or not state.values:
            return []

        messages = state.values.get("messages", [])
        history = []

        for msg in messages:
            # LangChain messages: HumanMessage, AIMessage, ToolMessage
            msg_type = getattr(msg, "type", "")
            if msg_type == "human" or getattr(msg, "role", "") == "user":
                history.append(("user", msg.content))
            elif msg_type == "ai" or getattr(msg, "role", "") == "assistant":
                if (
                    msg.content
                ):  # Kadang AIMessage hanya berisi tool_calls tanpa content
                    history.append(("agent", msg.content))
            elif msg_type == "tool":
                # Kita bisa sembunyikan atau tampilkan output tool
                pass

        return history

    def run_query(self, query: str) -> str:
        """Menjalankan query dan menyimpannya secara persisten via SQLite Checkpointer."""
        if not self.agent or not self.agent.compiled_graph:
            return "Error: Agent graph belum diinisialisasi."

        # Kita hanya perlu mengirim input baru, LangGraph akan menggabungkannya
        # dengan state riwayat yang ada di database.
        inputs = {"messages": [("user", query)]}

        config: RunnableConfig = {"configurable": {"thread_id": self.thread_id}}

        try:
            logger.info(f"AgentController memproses query: {query}")
            # Menjalankan graph (ini bisa makan waktu beberapa detik)
            result = self.agent.compiled_graph.invoke(inputs, config=config)

            # Mengambil pesan terakhir dari agent
            messages = result.get("messages", [])
            if messages:
                last_msg = messages[-1]
                return last_msg.content
            return "Tidak ada respon dari agen."
        except Exception as e:
            logger.error(f"Error saat mengeksekusi agent: {e}")
            return f"Terjadi kesalahan internal agen:\n{e!s}"
