"""Agent Orchestrator untuk multi-agent coordination.

Modul ini bertanggung jawab untuk menemukan agen secara dinamis, mengelola
pola koordinasi (sekuensial, paralel, supervisor/hierarkis), dan
mencegah serta meresolusi deadlock antar-agen.
"""

from __future__ import annotations

import logging
from enum import Enum

from shared.agent.base import BaseAgent
from shared.models import AgentState


logger = logging.getLogger(__name__)


class CoordinationPattern(str, Enum):
    """Pola eksekusi multi-agen."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"


class AgentOrchestrator:
    """Mengelola siklus hidup, registrasi, dan komunikasi antar beberapa agen."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register_agent(self, name: str, agent: BaseAgent) -> None:
        """Daftarkan agen ke orchestrator."""
        if name in self._agents:
            logger.warning("Agent '%s' sudah terdaftar. Menimpa yang lama.", name)
        self._agents[name] = agent
        logger.info("Agent '%s' berhasil didaftarkan ke Orchestrator.", name)

    def get_agent(self, name: str) -> BaseAgent:
        """Mengambil agen berdasarkan nama. Melempar KeyError jika tidak ada."""
        if name not in self._agents:
            raise KeyError(f"Agent '{name}' tidak ditemukan di registry.")
        return self._agents[name]

    def run_sequential(
        self, agent_names: list[str], initial_state: AgentState
    ) -> AgentState:
        """Menjalankan beberapa agen secara berurutan, passing state berantai."""
        logger.info("Menjalankan orkestrasi SEQUENTIAL untuk agen: %s", agent_names)

        current_state = initial_state
        for name in agent_names:
            agent = self.get_agent(name)
            current_state.current_agent = name
            logger.debug("--- Memulai giliran: %s ---", name)

            # Deteksi potensi deadlock (misal agen yang sama berulang-ulang tanpa kemajuan)
            # Di sini bisa disisipkan logika watchdog.

            current_state = agent.run(current_state)

            # Jika ada error kritis, resolusi dengan fallback atau break
            if current_state.errors:
                logger.error("Orkestrasi terhenti di agen '%s' karena error.", name)
                break

        return current_state

    async def run_parallel(
        self, agent_names: list[str], initial_state: AgentState
    ) -> dict[str, AgentState]:
        """Menjalankan beberapa agen secara paralel (async)."""
        import asyncio

        logger.info("Menjalankan orkestrasi PARALLEL untuk agen: %s", agent_names)

        async def _run_agent(name: str, state: AgentState) -> tuple[str, AgentState]:
            agent = self.get_agent(name)
            state_copy = state.model_copy(deep=True)
            state_copy.current_agent = name
            result_state = await agent.arun(state_copy)
            return name, result_state

        tasks = [_run_agent(name, initial_state) for name in agent_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output_states = {}
        for res in results:
            if isinstance(res, Exception):
                logger.error("Eksekusi agen paralel gagal: %s", str(res))
            else:
                name, state = res
                output_states[name] = state

        return output_states
