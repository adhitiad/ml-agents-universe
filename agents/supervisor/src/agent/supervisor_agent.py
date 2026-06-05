"""Supervisor Agent untuk Multi-Agent Routing.

Bertugas menganalisa query pengguna, menentukan domain agent yang relevan,
menjalankan agen-agen tersebut, lalu menggabungkan hasilnya menjadi respon akhir.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from scripts.run_agent import _AGENT_REGISTRY
from shared.agent.base import BaseAgent
from shared.models.base import (
    AgentConfig,
    AgentDomain,
    HealthStatus,
    HealthStatusEnum,
)
from shared.models.llm_provider import LLMManager


logger = logging.getLogger(__name__)


class SupervisorState(TypedDict):
    """Skema internal StateGraph untuk Supervisor."""

    messages: list[Any]
    metadata: dict[str, Any]


class SupervisorAgent(BaseAgent):
    """Orchestrator untuk 7 Domain Agent."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        """Inisialisasi Supervisor Agent."""
        default_config = AgentConfig(
            name="SupervisorAgent",
            domain=AgentDomain.NLP,  # Supervisor essentially acts like a generic router
            description="Menganalisa dan mendistribusikan query ke domain agent yang tepat.",
        )
        super().__init__(config=config or default_config)

    async def analyze_node(self, state: SupervisorState) -> SupervisorState:
        """Node 1: Menganalisa query untuk menentukan agent yang dibutuhkan."""
        import re

        # Terapkan memory truncation (sisakan 10 pesan terakhir)
        if len(state["messages"]) > 10:
            logger.info(
                "Memotong riwayat pesan dari %d menjadi 10 pesan terakhir.",
                len(state["messages"]),
            )
            state["messages"] = state["messages"][-10:]

        query = state["messages"][-1]["content"] if state["messages"] else ""

        system_prompt = (
            "Kamu adalah Supervisor AI. Tugasmu adalah membaca query pengguna dan "
            "menentukan agen mana saja yang dibutuhkan untuk menjawabnya. "
            "Daftar agen yang tersedia:\n"
            "- nlp: Teks, sentimen, terjemahan\n"
            "- finance: Saham, pasar modal, portofolio\n"
            "- economy: Makro ekonomi, inflasi, GDP\n"
            "- education: Penjelasan konsep, tutor\n"
            "- entertainment: Rekomendasi film/musik\n"
            "- mathematics: Kalkulasi, rumus, teorema\n"
            "- science: Kimia, fisika, biologi\n"
            "- system: OS, file, terminal, eksekusi program. (Pilih ini jika user meminta operasi file santai seperti 'baca isinya', 'cek file', 'tulis ini', atau 'jalankan')\n\n"
            "Keluarkan output dalam format JSON array yang hanya berisi nama agen (huruf kecil). "
            'Contoh: ["finance", "economy", "system"]. Jangan ada teks lain.'
        )

        logger.info("[Supervisor] Menganalisa query: %s", query)
        response_text = await LLMManager.ainvoke(system_prompt, query)

        try:
            # Gunakan Regex untuk mengekstrak array JSON jika terbungkus markdown ```json ... ```
            match = re.search(r"\[.*?\]", response_text, re.DOTALL)
            if match:
                json_str = match.group(0)
                selected_agents = json.loads(json_str)
                # Validasi terhadap registry
                selected_agents = [
                    a
                    for a in selected_agents
                    if isinstance(a, str) and a.lower() in _AGENT_REGISTRY
                ]
            else:
                selected_agents = ["nlp"]
        except Exception as e:
            logger.warning(
                "[Supervisor] Gagal parsing JSON LLM, fallback ke NLP: %s", e
            )
            selected_agents = ["nlp"]

        if not selected_agents:
            selected_agents = ["nlp"]

        logger.info("[Supervisor] Agent terpilih: %s", selected_agents)

        if "metadata" not in state:
            state["metadata"] = {}
        state["metadata"]["selected_agents"] = selected_agents
        state["metadata"]["agent_responses"] = {}

        return state

    async def execute_node(self, state: SupervisorState) -> SupervisorState:
        """Node 2: Mengeksekusi agent yang terpilih secara paralel (AsyncIO)."""
        import asyncio

        from scripts.run_agent import arun_single_agent

        query = state["messages"][-1]["content"] if state["messages"] else ""
        selected_agents = state["metadata"].get("selected_agents", ["nlp"])
        agent_responses = {}

        logger.info(
            "[Supervisor] Memulai eksekusi agen secara ASYNC PARALEL: %s",
            selected_agents,
        )

        async def _run(agent: str) -> tuple[str, dict[str, Any]]:
            logger.info("[Supervisor] -> Menjalankan %s...", agent.upper())
            res = await arun_single_agent(agent_name=agent, query=query)
            return agent, res

        tasks = [_run(agent) for agent in selected_agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for idx, result in enumerate(results):
            agent = selected_agents[idx]
            if isinstance(result, BaseException):
                logger.error(
                    "[Supervisor] Agen %s menghasilkan exception: %s", agent, result
                )
                agent_responses[agent] = f"Error: Exception {result}"
            else:
                agent_name, res = result
                if res["status"] == "OK":
                    agent_responses[agent_name] = res["response"]
                else:
                    agent_responses[agent_name] = f"Error: {res['response']}"

        state["metadata"]["agent_responses"] = agent_responses
        return state

    async def synthesize_node(self, state: SupervisorState) -> SupervisorState:
        """Node 3: Menggabungkan jawaban dari semua agen yang dieksekusi."""
        query = state["messages"][-1]["content"] if state["messages"] else ""
        responses = state["metadata"].get("agent_responses", {})

        if len(responses) == 1:
            final_answer = list(responses.values())[0]
        else:
            system_prompt = (
                "Kamu adalah Supervisor AI. Gabungkan jawaban dari beberapa pakar (agen) "
                "berikut menjadi satu laporan akhir yang padu, mudah dibaca, dan komprehensif. "
                "Jangan sebutkan 'Agen A berkata...', langsung gabungkan substansinya dengan rapi."
            )

            combined_context = "\n\n".join(
                [f"--- Dari Pakar {k.upper()} ---\n{v}" for k, v in responses.items()]
            )

            user_prompt = f"Pertanyaan awal pengguna:\n{query}\n\nJawaban para pakar:\n{combined_context}"

            logger.info(
                "[Supervisor] Mensintesis jawaban dari %d agen...", len(responses)
            )
            final_answer = await LLMManager.ainvoke(system_prompt, user_prompt)

        state["messages"].append({"role": "ai", "content": final_answer})
        state["metadata"]["final_answer"] = final_answer
        return state

    def build_graph(self) -> StateGraph:
        """Bangun StateGraph untuk Supervisor."""
        # Menggunakan dict biasa sebagai internal state LangGraph agar fleksibel,
        # sesuai dengan yang dibutuhkan oleh Pydantic AgentState saat didump.
        workflow = StateGraph(SupervisorState)  # type: ignore

        # Tambahkan nodes
        workflow.add_node("analyze", self.analyze_node)
        workflow.add_node("execute", self.execute_node)
        workflow.add_node("synthesize", self.synthesize_node)

        # Definisikan edges
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "execute")
        workflow.add_edge("execute", "synthesize")
        workflow.add_edge("synthesize", END)

        return workflow

    def health_check(self) -> HealthStatus:
        """Cek status agen."""
        return HealthStatus(
            status=HealthStatusEnum.HEALTHY
        )
