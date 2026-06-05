"""Verification script untuk Phase 2 — Agent Core Framework."""

import sys


sys.path.insert(0, ".")


def main() -> None:
    print("=== VERIFIKASI PHASE 2: AGENT FRAMEWORK ===")
    print()

    try:
        # 1. Models Base
        # 2. Agent Base & Orchestrator
        from shared.agent.base import BaseAgent
        from shared.models import (
            AgentConfig,
            AgentDomain,
            AgentState,
            ComponentHealth,
            HealthStatus,
            HealthStatusEnum,
        )

        print("  [OK] shared.agent di-import dengan sukses")

        # 3. Tools System

        from shared.agent.tools.base import BaseTool, tool

        print("  [OK] shared.agent.tools di-import dengan sukses")

        # Create dummy tool
        @tool(name="calc", description="kalkulator")
        def calc(a: int, b: int) -> int:
            return a + b

        assert isinstance(calc, BaseTool)
        assert calc.run({"a": 2, "b": 3}) == 5
        print("  [OK] Tool decorator dan execution sukses")

        # 4. Memory System
        from langchain_core.messages import AIMessage, HumanMessage

        from shared.agent.memory.buffer import ConversationBufferMemory
        from shared.agent.memory.vector import VectorStoreMemory

        print("  [OK] shared.agent.memory di-import dengan sukses")

        # Test Buffer
        buf = ConversationBufferMemory(max_messages=2)
        buf.add_message(HumanMessage(content="Halo"))
        buf.add_message(AIMessage(content="Hai"))
        buf.add_message(HumanMessage(content="Berapa 1+1"))
        assert len(buf.get_messages()) == 2
        print("  [OK] ConversationBufferMemory berjalan")

        # Test VectorStore
        vec = VectorStoreMemory()
        vec.add_message(
            HumanMessage(content="Python adalah bahasa pemrograman yang mudah dibaca.")
        )
        docs = vec.search_relevant("bahasa pemrograman")
        assert len(docs) > 0
        print("  [OK] VectorStoreMemory (FAISS + SentenceTransformers) berjalan")

        # 5. Graph Templates
        from langgraph.graph import StateGraph

        from shared.agent.graphs.react import create_react_graph

        print("  [OK] shared.agent.graphs di-import dengan sukses")

        # Test Builder dummy
        class DummyAgent(BaseAgent):
            def build_graph(self) -> StateGraph:
                return create_react_graph(
                    state_schema=AgentState,
                    reasoning_node=lambda state: {"messages": ["reasoning"]},
                    action_node=lambda state: {"messages": ["action"]},
                    continue_condition=lambda state: "end",
                )

            def health_check(self) -> HealthStatus:
                return HealthStatus(
                    status=HealthStatusEnum.HEALTHY,
                    checks=[
                        ComponentHealth(name="dummy", status=HealthStatusEnum.HEALTHY)
                    ],
                )

        config = AgentConfig(name="dummy", domain=AgentDomain.NLP)
        agent = DummyAgent(config=config)
        agent.compile()
        print("  [OK] BaseAgent inheritance dan kompilasi StateGraph berjalan")

        print("=" * 50)
        print("=== SEMUA VERIFIKASI PHASE 2 BERHASIL! ===")
        print("=" * 50)

    except Exception as e:
        print(f"Error saat verifikasi: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
