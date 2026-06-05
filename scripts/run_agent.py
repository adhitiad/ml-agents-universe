"""CLI untuk menjalankan ML Agents Universe.

Mendukung menjalankan agent individual atau semua agent sekaligus,
dengan pilihan 9 provider AI berbeda.

Usage:
    # Jalankan satu agent (default: Ollama)
    python scripts/run_agent.py --agent nlp --query "Analisis sentimen: Hari ini indah"

    # Dengan provider tertentu
    python scripts/run_agent.py --agent finance --provider openai --query "Analisis saham AAPL"

    # Mode interaktif (chat loop)
    python scripts/run_agent.py --agent nlp --interactive

    # Jalankan semua agent sekaligus
    python scripts/run_agent.py --all --query "Perkenalkan dirimu"

    # List semua provider
    python scripts/run_agent.py --list-providers

    # List semua agent
    python scripts/run_agent.py --list-agents
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from typing import Any


# Menambahkan root direktori ke sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Force UTF-8 output di Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

from shared.models import AgentConfig, AgentDomain, AgentState
from shared.models.llm_provider import (
    _DEFAULT_MODELS,
    LLMManager,
    LLMProvider,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("run_agent")

# ============================================================
# Agent Registry
# ============================================================

_AGENT_REGISTRY: dict[str, dict[str, str]] = {
    "nlp": {
        "module": "agents.nlp.src.agent.nlp_agent",
        "class": "NLPAgent",
        "domain": "nlp",
        "description": "Natural Language Processing — analisis teks, sentimen, NER",
        "system_prompt": (
            "Kamu adalah NLP Expert AI Agent. Tugasmu menganalisis teks, "
            "mendeteksi sentimen, mengekstrak entitas, dan meringkas dokumen. "
            "Jawab dalam bahasa Indonesia yang jelas dan terstruktur."
        ),
    },
    "finance": {
        "module": "agents.finance.src.agent.finance_agent",
        "class": "FinanceAgent",
        "domain": "finance",
        "description": "Finance — analisis pasar, portofolio, risiko",
        "system_prompt": (
            "Kamu adalah Finance Advisor AI Agent. Tugasmu menganalisis data pasar, "
            "menghitung risiko, dan memberikan rekomendasi investasi. "
            "Gunakan data dan indikator teknikal dalam analisismu."
        ),
    },
    "economy": {
        "module": "agents.economy.src.agent.economy_agent",
        "class": "EconomyAgent",
        "domain": "economy",
        "description": "Economy — analisis makroekonomi, GDP, inflasi",
        "system_prompt": (
            "Kamu adalah Macro-Economy Analyst AI Agent. Tugasmu menganalisis "
            "indikator ekonomi makro seperti GDP, inflasi, dan pengangguran. "
            "Berikan analisis yang berdasarkan data dan teori ekonomi."
        ),
    },
    "education": {
        "module": "agents.education.src.agent.education_agent",
        "class": "EducationAgent",
        "domain": "education",
        "description": "Education — tutor adaptif, knowledge tracing",
        "system_prompt": (
            "Kamu adalah Tutor AI Agent yang sabar dan adaptif. "
            "Jelaskan konsep dengan bahasa sederhana dan berikan contoh konkret. "
            "Sesuaikan tingkat kesulitan dengan pemahaman siswa."
        ),
    },
    "entertainment": {
        "module": "agents.entertainment.src.agent.entertainment_agent",
        "class": "EntertainmentAgent",
        "domain": "entertainment",
        "description": "Entertainment — rekomendasi film, musik, konten",
        "system_prompt": (
            "Kamu adalah Entertainment Recommender AI Agent. "
            "Berikan rekomendasi film, musik, dan konten hiburan yang personal. "
            "Pertimbangkan preferensi dan mood pengguna."
        ),
    },
    "mathematics": {
        "module": "agents.mathematics.src.agent.math_agent",
        "class": "MathAgent",
        "domain": "mathematics",
        "description": "Mathematics — pembuktian teorema, kalkulasi",
        "system_prompt": (
            "Kamu adalah Mathematician AI Agent. Selesaikan masalah matematika "
            "langkah demi langkah dengan penjelasan yang jelas. "
            "Tunjukkan proses pemikiranmu secara runtut."
        ),
    },
    "science": {
        "module": "agents.science.src.agent.science_agent",
        "class": "ScienceAgent",
        "domain": "science",
        "description": "Science — analisis molekuler, eksperimen, literatur",
        "system_prompt": (
            "Kamu adalah Scientist AI Agent. Jelaskan fenomena sains "
            "dengan akurat dan mudah dipahami. Gunakan analogi dan "
            "referensi ilmiah yang relevan."
        ),
    },
    "system": {
        "module": "agents.system.src.agent.system_agent",
        "class": "SystemAgent",
        "domain": "system",
        "description": "System — otomatisasi OS, baca/tulis file, eksekusi shell",
        "system_prompt": (
            "Kamu adalah System Automation AI Agent. Tugasmu adalah mengeksekusi "
            "perintah sistem operasi, mengelola file, dan mengotomasi tugas desktop "
            "sesuai instruksi pengguna secara akurat dan aman."
        ),
    },
}


def list_providers() -> None:
    """Tampilkan daftar semua provider AI yang tersedia."""
    providers = LLMManager.list_providers()

    print("\n" + "=" * 95)
    print("  9 MODE AI PROVIDER — ML Agents Universe")
    print("=" * 95)
    print(
        f"  {'#':<4} {'Provider':<18} {'Model Default':<35} {'Biaya':<18} {'API Key':<10}"
    )
    print("-" * 95)

    for i, p in enumerate(providers, 1):
        print(
            f"  {i:<4} {p['name']:<18} {p['default_model']:<35} "
            f"{p['cost']:<18} {p['api_key_configured']:<10}"
        )

    print("=" * 95)
    print("\n  Cara menggunakan:")
    print("    python scripts/run_agent.py --agent nlp --provider ollama")
    print("    python scripts/run_agent.py --agent nlp --provider openai")
    print("    LLM_PROVIDER=groq python scripts/run_agent.py --agent nlp\n")


def list_agents() -> None:
    """Tampilkan daftar semua agent yang tersedia."""
    print("\n" + "=" * 75)
    print("  8 DOMAIN AGENTS — ML Agents Universe")
    print("=" * 75)
    print(f"  {'#':<4} {'Agent':<18} {'Deskripsi':<50}")
    print("-" * 75)

    for i, (name, info) in enumerate(_AGENT_REGISTRY.items(), 1):
        print(f"  {i:<4} {name:<18} {info['description']:<50}")

    print("=" * 75)
    print("\n  Cara menggunakan:")
    print('    python scripts/run_agent.py --agent nlp --query "Halo dunia"')
    print('    python scripts/run_agent.py --all --query "Perkenalkan dirimu"\n')


def run_single_agent(
    agent_name: str,
    query: str,
    provider: str = "ollama",
    model: str = "",
) -> dict[str, Any]:
    """Jalankan satu agent dengan query tertentu."""
    import importlib

    info = _AGENT_REGISTRY[agent_name]

    # Buat config
    config = AgentConfig(
        name=f"{agent_name}_agent",
        domain=AgentDomain(info["domain"]),
        description=info["description"],
    )

    # Import dan instantiate agent
    module = importlib.import_module(info["module"])
    agent_class = getattr(module, info["class"])
    agent = agent_class(config=config)

    # Override environment variables agar agent memakai provider yang diminta
    os.environ["LLM_PROVIDER"] = provider
    if model:
        os.environ["LLM_MODEL"] = model

    start_time = time.time()
    try:
        initial_state = AgentState(messages=[{"role": "user", "content": query}])
        final_state = agent.run(initial_state)

        response = ""
        if final_state.messages:
            last_msg = final_state.messages[-1]
            response = (
                last_msg.get("content", "")
                if isinstance(last_msg, dict)
                else getattr(last_msg, "content", str(last_msg))
            )

        elapsed = time.time() - start_time

        return {
            "agent": agent_name,
            "provider": provider,
            "model": model or _DEFAULT_MODELS.get(LLMProvider(provider), ""),
            "query": query,
            "response": response,
            "time_sec": round(elapsed, 2),
            "status": "OK",
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "agent": agent_name,
            "provider": provider,
            "model": model,
            "query": query,
            "response": str(e),
            "time_sec": round(elapsed, 2),
            "status": "ERROR",
        }


async def arun_single_agent(
    agent_name: str,
    query: str,
    provider: str = "ollama",
    model: str = "",
) -> dict[str, Any]:
    """Jalankan satu agent secara asinkron."""
    import importlib

    info = _AGENT_REGISTRY[agent_name]

    # Buat config
    config = AgentConfig(
        name=f"{agent_name}_agent",
        domain=AgentDomain(info["domain"]),
        description=info["description"],
    )

    # Import dan instantiate agent
    module = importlib.import_module(info["module"])
    agent_class = getattr(module, info["class"])
    agent = agent_class(config=config)

    # Override environment variables agar agent memakai provider yang diminta
    os.environ["LLM_PROVIDER"] = provider
    if model:
        os.environ["LLM_MODEL"] = model

    start_time = time.time()
    try:
        initial_state = AgentState(messages=[{"role": "user", "content": query}])
        final_state = await agent.arun(initial_state)

        response = ""
        if final_state.messages:
            last_msg = final_state.messages[-1]
            response = (
                last_msg.get("content", "")
                if isinstance(last_msg, dict)
                else getattr(last_msg, "content", str(last_msg))
            )

        elapsed = time.time() - start_time

        return {
            "agent": agent_name,
            "provider": provider,
            "model": model or _DEFAULT_MODELS.get(LLMProvider(provider), ""),
            "query": query,
            "response": response,
            "time_sec": round(elapsed, 2),
            "status": "OK",
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "agent": agent_name,
            "provider": provider,
            "model": model,
            "query": query,
            "response": str(e),
            "time_sec": round(elapsed, 2),
            "status": "ERROR",
        }


def run_interactive(agent_name: str, provider: str = "ollama", model: str = "") -> None:
    """Mode interaktif: chat loop dengan satu agent."""
    info = _AGENT_REGISTRY[agent_name]
    model_display = model or _DEFAULT_MODELS.get(LLMProvider(provider), "")

    print(f"\n{'=' * 60}")
    print(f"  Mode Interaktif: {agent_name.upper()} Agent")
    print(f"  Provider: {provider} | Model: {model_display}")
    print("  Ketik 'quit' atau 'exit' untuk keluar.")
    print(f"{'=' * 60}\n")

    while True:
        try:
            user_input = input("Kamu > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSampai jumpa!")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("\nSampai jumpa!")
            break

        if not user_input:
            continue

        result = run_single_agent(agent_name, user_input, provider, model)

        if result["status"] == "OK":
            print(f"\n{agent_name.upper()} Agent > {result['response']}")
            print(
                f"  [{result['time_sec']}s | {result['provider']}:{result['model']}]\n"
            )
        else:
            print(f"\n[ERROR] {result['response']}\n")


def run_all_agents(query: str, provider: str = "ollama", model: str = "") -> None:
    """Jalankan semua 8 agent dengan query yang sama."""
    model_display = model or _DEFAULT_MODELS.get(LLMProvider(provider), "")

    print(f"\n{'=' * 80}")
    print(
        f"  Menjalankan SEMUA 8 Agent | Provider: {provider} | Model: {model_display}"
    )
    print(f'  Query: "{query}"')
    print(f"{'=' * 80}\n")

    results: list[dict[str, Any]] = []
    for agent_name in _AGENT_REGISTRY:
        print(f"  [{agent_name.upper()}] Memproses...")
        result = run_single_agent(agent_name, query, provider, model)
        results.append(result)

        if result["status"] == "OK":
            # Truncate response untuk tampilan ringkas
            resp = result["response"]
            display = resp[:120] + "..." if len(resp) > 120 else resp
            print(f"    -> {display}")
            print(f"    [{result['time_sec']}s]\n")
        else:
            print(f"    -> [ERROR] {result['response'][:80]}\n")

    # Ringkasan
    print(f"\n{'=' * 80}")
    print(f"  {'Agent':<18} {'Status':<10} {'Waktu':>8}   {'Cuplikan Jawaban':<40}")
    print(f"  {'-' * 76}")
    for r in results:
        resp_preview = (
            r["response"][:40].replace("\n", " ") if r["status"] == "OK" else "ERROR"
        )
        print(
            f"  {r['agent']:<18} {r['status']:<10} {r['time_sec']:>6.2f}s   {resp_preview}"
        )

    ok = sum(1 for r in results if r["status"] == "OK")
    print(f"  {'-' * 76}")
    print(f"  Total: {ok}/{len(results)} berhasil")
    print(f"{'=' * 80}\n")


async def async_run_supervisor(
    query: str, provider: str = "ollama", model: str = ""
) -> None:
    """Jalankan Supervisor Agent secara asinkron."""
    import time

    from agents.supervisor.src.agent.supervisor_agent import SupervisorAgent

    os.environ["LLM_PROVIDER"] = provider
    if model:
        os.environ["LLM_MODEL"] = model

    model_display = model or _DEFAULT_MODELS.get(LLMProvider(provider), "")

    print(f"\n{'=' * 80}")
    print(
        f"  🤖 AUTO-ROUTING (ASYNC SUPERVISOR) | Provider: {provider} | Model: {model_display}"
    )
    print(f'  Query: "{query}"')
    print(f"{'=' * 80}\n")

    start_time = time.time()

    supervisor = SupervisorAgent()
    initial_state = AgentState(messages=[{"role": "user", "content": query}])

    try:
        print("  [1/3] Supervisor sedang menganalisa query (Async)...")
        final_state = await supervisor.arun(initial_state)

        meta = final_state.metadata
        selected = meta.get("selected_agents", [])
        responses = meta.get("agent_responses", {})
        final_answer = meta.get("final_answer", "")

        elapsed = time.time() - start_time

        print(
            f"  [2/3] Pakar yang dilibatkan: {', '.join([s.upper() for s in selected])}"
        )
        for agent, res in responses.items():
            status = "✅" if not res.startswith("Error:") else "❌"
            print(f"        {status} {agent.upper()} merespon.")

        print("  [3/3] Mensintesis jawaban akhir...\n")
        print(f"{'-' * 80}")
        print(f"{final_answer}")
        print(f"{'-' * 80}")
        print(f"\n  ⏱️ Waktu total: {elapsed:.2f} detik\n")

    except Exception as e:
        print(f"\n[ERROR] Supervisor gagal mengeksekusi tugas: {e}\n")


def run_supervisor(query: str, provider: str = "ollama", model: str = "") -> None:
    """Entry point sinkron yang menjalankan event loop asyncio."""
    import asyncio

    asyncio.run(async_run_supervisor(query, provider, model))


def main() -> None:
    """Entry point CLI."""
    parser = argparse.ArgumentParser(
        description="ML Agents Universe — Agent Runner CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python scripts/run_agent.py --auto --query "Analisis sentimen dan hitung ROI saham AAPL"
  python scripts/run_agent.py --agent nlp --query "Analisis sentimen: Hari ini indah"
  python scripts/run_agent.py --agent finance --provider openai --query "Analisis AAPL"
  python scripts/run_agent.py --agent nlp --interactive
  python scripts/run_agent.py --all --query "Perkenalkan dirimu"
  python scripts/run_agent.py --list-providers
  python scripts/run_agent.py --list-agents
        """,
    )

    # Actions
    parser.add_argument(
        "--list-providers", action="store_true", help="Tampilkan semua AI provider"
    )
    parser.add_argument(
        "--list-agents", action="store_true", help="Tampilkan semua agent"
    )
    parser.add_argument(
        "--all", action="store_true", help="Jalankan semua 8 agent sekaligus"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Gunakan Supervisor Agent untuk Auto-Routing",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Mode chat interaktif"
    )

    # Parameters
    parser.add_argument(
        "--agent", "-a", choices=list(_AGENT_REGISTRY.keys()), help="Nama agent"
    )
    parser.add_argument(
        "--query", "-q", type=str, default="", help="Pertanyaan untuk agent"
    )
    parser.add_argument(
        "--provider",
        "-p",
        type=str,
        default=os.getenv("LLM_PROVIDER", "ollama"),
        help="AI provider (default: dari env LLM_PROVIDER atau 'ollama')",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default=os.getenv("LLM_MODEL", ""),
        help="Nama model spesifik (default: auto per provider)",
    )

    args = parser.parse_args()

    # Handle actions
    if args.list_providers:
        list_providers()
        return

    if args.list_agents:
        list_agents()
        return

    if args.auto:
        if not args.query:
            parser.error("--auto membutuhkan --query")
        run_supervisor(args.query, args.provider, args.model)
        return

    if args.all:
        if not args.query:
            args.query = (
                "Halo, perkenalkan dirimu dan jelaskan kemampuanmu secara singkat."
            )
        run_all_agents(args.query, args.provider, args.model)
        return

    if args.interactive:
        if not args.agent:
            parser.error("--interactive membutuhkan --agent")
        run_interactive(args.agent, args.provider, args.model)
        return

    if args.agent:
        if not args.query:
            parser.error("--agent membutuhkan --query (atau gunakan --interactive)")
        result = run_single_agent(args.agent, args.query, args.provider, args.model)

        print(f"\n{'=' * 60}")
        print(f"  Agent: {result['agent'].upper()}")
        print(f"  Provider: {result['provider']} | Model: {result['model']}")
        print(f"  Status: {result['status']} | Waktu: {result['time_sec']}s")
        print(f"{'=' * 60}")
        print(f"\n  Query: {result['query']}")
        print(f"\n  Jawaban:\n  {result['response']}\n")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
