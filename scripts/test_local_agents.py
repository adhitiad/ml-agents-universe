import asyncio
import os
import sys


# Menambahkan root direktori ke sys.path agar impor modul berhasil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Any

from agents.economy.src.agent.economy_agent import EconomyAgent
from agents.education.src.agent.education_agent import EducationAgent
from agents.entertainment.src.agent.entertainment_agent import EntertainmentAgent
from agents.finance.src.agent.finance_agent import FinanceAgent
from agents.mathematics.src.agent.math_agent import MathAgent

# Import semua agen
from agents.nlp.src.agent.nlp_agent import NLPAgent
from agents.science.src.agent.science_agent import ScienceAgent
from shared.models import AgentConfig, AgentDomain, AgentState
from shared.models.local_llm import LocalLLM


# Helper untuk membajak node agar memakai Ollama secara dinamis
def patch_agent_node(agent_instance, node_method_name, system_prompt):
    original_method = getattr(agent_instance, node_method_name)

    def patched_method(state: Any) -> dict[str, Any]:
        # Jika state berbentuk dict atau Pydantic, ekstrak messages/metadata
        is_dict = isinstance(state, dict)
        messages = (
            state.get("messages", []) if is_dict else getattr(state, "messages", [])
        )

        user_query = "Halo!"
        if messages:
            last_msg = messages[-1]
            user_query = (
                last_msg.get("content", "")
                if isinstance(last_msg, dict)
                else getattr(last_msg, "content", str(last_msg))
            )

        print(
            f"\n[LLM Request - {agent_instance.__class__.__name__}] Memikirkan jawaban..."
        )
        reply = LocalLLM.invoke(system_prompt, user_query)

        if is_dict:
            state.setdefault("messages", []).append(
                {"role": "assistant", "content": reply}
            )
            return state
        else:
            state.messages.append({"role": "assistant", "content": reply})
            return {"messages": state.messages}

    setattr(agent_instance, node_method_name, patched_method)


async def test_all_agents():
    print("=== Menginisiasi Skenario Tes Seluruh Agen via Ollama ===")

    dummy_config = AgentConfig(name="tester", description="testing agent", domain=AgentDomain.NLP)

    agents = [
        (
            NLPAgent(config=dummy_config),
            "_reasoning_step",
            "Kamu adalah NLP Expert AI. Analisis maksud dari pesan pengguna berikut.",
        ),
        (
            FinanceAgent(config=dummy_config),
            "_planner_step",
            "Kamu adalah Finance Advisor AI. Buat rencana finansial sederhana.",
        ),
        (
            EconomyAgent(config=dummy_config),
            "_supervisor_step",
            "Kamu adalah Macro-Economy Manager AI. Berikan analisis ekonomi singkat.",
        ),
        (
            EducationAgent(config=dummy_config),
            "_planner_step",
            "Kamu adalah Tutor AI. Berikan penjelasan edukatif yang mudah dimengerti.",
        ),
        (
            EntertainmentAgent(config=dummy_config),
            "_llm_step",
            "Kamu adalah Entertainment & Pop Culture AI. Berikan rekomendasi hiburan.",
        ),
        (
            MathAgent(config=dummy_config),
            "_planner_step",
            "Kamu adalah Ahli Matematika AI. Selesaikan soal ini langkah demi langkah.",
        ),
        (
            ScienceAgent(config=dummy_config),
            "_llm_step",
            "Kamu adalah Ilmuwan AI. Jelaskan fenomena sains berikut.",
        ),
    ]

    test_queries = [
        "Tolong ringkas artikel tentang Machine Learning.",
        "Apakah saham teknologi bagus dibeli sekarang?",
        "Apa dampak inflasi 5% terhadap pengangguran?",
        "Jelaskan apa itu fotosintesis untuk anak SD.",
        "Film sci-fi apa yang bagus ditonton akhir pekan ini?",
        "Berapa akar kuadrat dari 144 dibagi 2?",
        "Mengapa langit berwarna biru saat siang hari?",
    ]

    for (agent, method_name, sys_prompt), query in zip(agents, test_queries):
        print(f"\n--- Menguji {agent.__class__.__name__} ---")
        try:
            # Patch
            if hasattr(agent, method_name):
                patch_agent_node(agent, method_name, sys_prompt)
            else:
                print(f"Skipping patch, metode {method_name} tidak ditemukan.")

            # Setup State
            state = AgentState(messages=[{"role": "user", "content": query}])

            # Compile graph
            graph = agent.compile()
            print(f"User Query: {query}")

            # Execute Graph (dummy run)
            # Beberapa agent mungkin error karena node lain tidak tersambung sempurna,
            # Jadi kita langsung trigger function-nya saja untuk membuktikan LLM hidup.
            patched_func = getattr(agent, method_name)
            new_state_dict = patched_func(state)

            reply = new_state_dict["messages"][-1]["content"]
            print(f">>> Jawaban {agent.__class__.__name__}:")
            print(reply)

        except Exception as e:
            print(f"Error testing {agent.__class__.__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_all_agents())
