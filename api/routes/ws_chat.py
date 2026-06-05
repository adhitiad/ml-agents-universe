import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agents.supervisor.src.agent.supervisor_agent import SupervisorAgent
from api.routes.chat import llm_semaphore
from shared.models.base import AgentState


router = APIRouter(prefix="/ws/v1", tags=["WebSocket Chat"])


@router.websocket("/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """Endpoint WebSocket untuk Chat Streaming secara Real-Time.
    Ini tidak di-rate limit secara IP secara default, tapi menggunakan Semaphore global.
    """
    await websocket.accept()

    # Untuk keamanan di WS, kita bisa minta auth via pesan pertama,
    # tapi demi kesederhanaan POC, kita langsung dengarkan pesan
    try:
        data = await websocket.receive_text()
        request_json = json.loads(data)
        query = request_json.get("query", "")

        if not query:
            await websocket.send_json({"error": "Query kosong"})
            await websocket.close()
            return

        await websocket.send_json(
            {"status": "queued", "message": "Menunggu giliran (Heat Optimizer)..."}
        )

        # Masuk antrean Semaphore (Heat Optimization)
        async with llm_semaphore:
            await websocket.send_json(
                {
                    "status": "analyzing",
                    "message": "Supervisor sedang menganalisa pertanyaan...",
                }
            )

            supervisor = SupervisorAgent()
            supervisor.compile()
            assert supervisor.compiled_graph is not None, "Gagal mengkompilasi graf LangGraph"
            initial_state = AgentState(messages=[{"role": "user", "content": query}])

            # Kita gunakan astream untuk mengirim notifikasi setiap kali Node selesai bekerja
            async for step in supervisor.compiled_graph.astream(
                initial_state.model_dump()
            ):
                if "analyze" in step:
                    state = step["analyze"]
                    meta = state.get("metadata", {})
                    agents = meta.get("selected_agents", [])
                    await websocket.send_json(
                        {
                            "status": "executing",
                            "message": f"Melibatkan pakar: {', '.join([a.upper() for a in agents])}...",
                            "agents": agents,
                        }
                    )

                elif "execute" in step:
                    await websocket.send_json(
                        {
                            "status": "synthesizing",
                            "message": "Pakar selesai. Supervisor mensintesis kesimpulan akhir...",
                        }
                    )

                elif "synthesize" in step:
                    state = step["synthesize"]
                    final_answer = state.get("metadata", {}).get("final_answer", "")
                    await websocket.send_json(
                        {
                            "status": "done",
                            "message": "Selesai",
                            "response": final_answer,
                        }
                    )

    except WebSocketDisconnect:
        print("[WS] Client disconnected")
    except Exception as e:
        await websocket.send_json({"error": f"Internal Error: {e!s}"})
        await websocket.close()
