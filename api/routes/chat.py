import asyncio
import os
import time

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from agents.supervisor.src.agent.supervisor_agent import SupervisorAgent
from api.schema import ChatRequest, ChatResponse
from api.security import verify_api_key
from shared.models.base import AgentState


# Semaphore untuk membatasi eksekusi LLM secara paralel (Heat Optimization)
# Jika ada lebih dari 3 permintaan, yang lain akan menunggu di antrean
MAX_CONCURRENT_REQUESTS = 3
llm_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

router = APIRouter(prefix="/v1", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: Request, body: ChatRequest, api_key: str = Depends(verify_api_key)
):
    """Unified Endpoint untuk ngobrol dengan Universe.
    Request akan diteruskan ke Supervisor Agent yang otomatis merutekan ke pakar.
    """
    start_time = time.time()

    # Override provider (optional, jika LLMManager mengambil dari env)
    if body.provider:
        os.environ["LLM_PROVIDER"] = body.provider
    if body.model:
        os.environ["LLM_MODEL"] = body.model

    supervisor = SupervisorAgent()
    initial_state = AgentState(messages=[{"role": "user", "content": body.query}])

    # Gunakan Semaphore agar tidak membuat CPU/GPU jebol
    async with llm_semaphore:
        try:
            # Panggil Supervisor Agent (yang otomatis merutekan dan mensintesis)
            final_state = await supervisor.arun(initial_state)

            meta = final_state.metadata
            selected_agents = meta.get("selected_agents", [])
            final_answer = meta.get("final_answer", "")

            elapsed = time.time() - start_time
            return ChatResponse(
                query=body.query,
                final_answer=final_answer,
                experts_consulted=selected_agents,
                execution_time=round(elapsed, 2),
            )
        except Exception as e:
            return JSONResponse(
                status_code=500, content={"detail": f"Internal Server Error: {e!s}"}
            )
