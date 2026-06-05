"""Base Agent Class.

Module ini menyediakan `BaseAgent` yang merupakan kelas abstrak untuk semua domain agent.
BaseAgent mendefinisikan interface yang seragam, lifecycle hooks (on_start, on_action, dll),
serta integrasi dengan sistem memori dan tools.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from abc import ABC, abstractmethod
from typing import Any

import redis
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from shared.agent.memory.base import BaseMemory
from shared.agent.memory.buffer import ConversationBufferMemory
from shared.agent.tools.registry import ToolRegistry
from shared.models import AgentConfig, AgentState, HealthStatus


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Kelas dasar abstrak (Abstract Base Class) untuk semua Agen dalam Universe.

    Semua agen domain (NLP, Finance, dll) harus mewarisi kelas ini dan
    mengimplementasikan metode abstrak `build_graph()` dan `health_check()`.
    """

    def __init__(
        self,
        config: AgentConfig,
        tools: ToolRegistry | None = None,
        memory: BaseMemory | None = None,
    ) -> None:
        """Inisialisasi BaseAgent.

        Args:
            config: Konfigurasi agent dari Pydantic model.
            tools: Registry tool (opsional). Jika None, akan dibuatkan registry kosong.
            memory: Sistem memori (opsional). Jika None, akan menggunakan ConversationBufferMemory.
        """
        self.config = config
        self.tools = tools or ToolRegistry()
        self.memory = memory or ConversationBufferMemory(max_messages=50)

        # StateGraph yang akan dikompilasi oleh subclass
        self.graph: StateGraph | None = None
        self.compiled_graph: CompiledStateGraph | None = None
        self._sqlite_conn = None

    def on_start(self, state: AgentState) -> AgentState:
        """Lifecycle Hook: Dipanggil saat agen mulai mengeksekusi request."""
        logger.info(
            "[%s] Memulai eksekusi agent. Trace ID: %s",
            self.config.name,
            state.trace_id,
        )
        return state

    def on_action(self, state: AgentState, action_name: str, payload: Any) -> None:
        """Lifecycle Hook: Dipanggil sebelum mengeksekusi tool/aksi."""
        logger.debug("[%s] Mengeksekusi aksi: %s", self.config.name, action_name)

    def on_observe(self, state: AgentState, action_name: str, result: Any) -> None:
        """Lifecycle Hook: Dipanggil setelah tool/aksi mengembalikan hasil."""
        logger.debug("[%s] Menerima observasi dari %s", self.config.name, action_name)

    def on_finish(self, state: AgentState, final_response: str) -> None:
        """Lifecycle Hook: Dipanggil saat agen selesai dan menghasilkan respon akhir."""
        logger.info("[%s] Eksekusi selesai.", self.config.name)
        # Menyimpan respon AI ke memori
        self.memory.add_message(AIMessage(content=final_response))

    def on_error(self, state: AgentState, error: Exception) -> AgentState:
        """Lifecycle Hook: Dipanggil saat terjadi error kritis pada StateGraph."""
        logger.error("[%s] Terjadi error: %s", self.config.name, str(error))
        state.errors.append(str(error))
        return state

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """Membangun topologi LangGraph (StateGraph) untuk agen ini.

        Subclass harus mendefinisikan node, edge, dan mengembalikan objek StateGraph.
        """
        pass

    def compile(self) -> None:
        """Kompilasi graf LangGraph menjadi executable application dengan Checkpointer dinamis."""
        if not self.graph:
            self.graph = self.build_graph()

        data_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "data")
        )
        config_path = os.path.join(data_dir, "desktop_config.json")

        checkpointer = None
        db_type = "AUTO"
        redis_url = None
        ram_gb = 0

        if os.path.exists(config_path):
            with open(config_path) as f:
                config_data = json.load(f)
                db_type = config_data.get("database_type", "AUTO")
                redis_url = config_data.get("redis_url")
                ram_gb = config_data.get("system_ram_gb", 0)

        if "REDIS" in db_type and redis_url:
            try:
                # Karena RedisSaver seringkali digunakan sebagai context manager (with RedisSaver.from_conn_info(...) as checkpointer:),
                # Kita akan pass connection pool secara eksplisit untuk menyimpannya di memory BaseAgent.
                # Namun untuk simpelnya (jika tidak ada context manager requirements yang strict),
                # kita gunakan conn dari library standard redis.
                self._redis_conn = redis.Redis.from_url(redis_url)
                checkpointer = RedisSaver(redis_client=self._redis_conn)
                logger.info(
                    "[%s] Menggunakan RedisSaver Checkpointer.", self.config.name
                )
            except Exception as e:
                logger.error(
                    "Gagal terhubung ke Redis: %s. Fallback ke Memory/SQLite.", e
                )
                db_type = "AUTO"

        if not checkpointer:
            if db_type == "AUTO":
                if ram_gb > 6:
                    checkpointer = MemorySaver()
                    logger.info(
                        "[%s] RAM > 6GB. Menggunakan MemorySaver Checkpointer (Sementara).",
                        self.config.name,
                    )
                else:
                    db_path = os.path.join(data_dir, "checkpoints.sqlite")
                    os.makedirs(os.path.dirname(db_path), exist_ok=True)
                    self._sqlite_conn = sqlite3.connect(
                        db_path, check_same_thread=False
                    )
                    checkpointer = SqliteSaver(self._sqlite_conn)
                    logger.info(
                        "[%s] RAM <= 6GB. Menggunakan SqliteSaver Checkpointer.",
                        self.config.name,
                    )
            else:
                checkpointer = MemorySaver()

        self.compiled_graph = self.graph.compile(checkpointer=checkpointer)
        logger.info("[%s] Graf berhasil dikompilasi.", self.config.name)

    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Melakukan pengecekan kesehatan agen.

        Returns:
            Status kesehatan (HEALTHY, DEGRADED, UNHEALTHY).
        """
        pass

    def run(self, initial_state: AgentState) -> AgentState:
        """Menjalankan agen menggunakan graf yang sudah dikompilasi.

        Penting: error handling agar agen tidak crash melainkan fallback ke safe state.
        """
        if not self.compiled_graph:
            self.compile()

        assert self.compiled_graph is not None, "Graf gagal dikompilasi"

        self.on_start(initial_state)

        try:
            # langgraph execution dengan konfigurasi thread_id
            config: RunnableConfig = {
                "configurable": {"thread_id": initial_state.trace_id}
            }
            final_state_dict = self.compiled_graph.invoke(
                initial_state.model_dump(), config=config
            )
            final_state = AgentState(**final_state_dict)
            return final_state
        except Exception as e:
            return self.on_error(initial_state, e)

    async def arun(self, initial_state: AgentState) -> AgentState:
        """Menjalankan agen secara asinkron."""
        if not self.compiled_graph:
            self.compile()

        assert self.compiled_graph is not None, "Graf gagal dikompilasi"

        self.on_start(initial_state)

        try:
            config: RunnableConfig = {
                "configurable": {"thread_id": initial_state.trace_id}
            }
            final_state_dict = await self.compiled_graph.ainvoke(
                initial_state.model_dump(), config=config
            )
            final_state = AgentState(**final_state_dict)
            return final_state
        except Exception as e:
            return self.on_error(initial_state, e)
