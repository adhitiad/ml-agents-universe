import asyncio
import logging
from datetime import datetime
from pathlib import Path

import polars as pl
from fastapi import APIRouter, BackgroundTasks, HTTPException
from langchain_core.messages import HumanMessage

from api.router import UniverseState
from api.router import app as orchestrator_app
from shared.adapters.sender import sender
from shared.data.schema import NormalizedMessage


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook/omnichannel", tags=["Omnichannel"])

# Direktori data raw untuk penyimpanan pesan masuk
DATA_DIR = Path("data/raw/omnichannel")
DATA_DIR.mkdir(parents=True, exist_ok=True)
PARQUET_FILE = DATA_DIR / "messages.parquet"


async def process_message_background(message: NormalizedMessage):
    """Background task untuk memproses pesan secara asinkron."""
    try:
        # 1. Simpan ke Polars (Log OSINT/Data Eng)
        df_new = pl.DataFrame([message.model_dump()])
        if PARQUET_FILE.exists():
            df_existing = pl.read_parquet(PARQUET_FILE)
            df_combined = pl.concat([df_existing, df_new], how="vertical_relaxed")
            df_combined.write_parquet(PARQUET_FILE)
        else:
            df_new.write_parquet(PARQUET_FILE)

        logger.info(
            f"Pesan {message.message_id} dari {message.platform} disimpan ke data lake."
        )

        # 2. Teruskan ke Orchestrator LangGraph (di-wrap dengan to_thread agar non-blocking)
        logger.info("Merutekan pesan ke Orchestrator...")
        initial_state = UniverseState(messages=[HumanMessage(content=message.content)])

        result = await asyncio.to_thread(orchestrator_app.invoke, initial_state)

        # 3. Ambil balasan akhir dari agen dan kirim ke platform asal
        if isinstance(result, dict) and result.get("messages"):
            final_answer = result["messages"][-1].content
            logger.info(
                f"Orchestrator merespons. Mengirim balik ke {message.platform}..."
            )

            await sender.send_reply(
                platform=message.platform, chat_id=message.chat_id, text=final_answer
            )

    except Exception as e:
        logger.error(f"Gagal memproses pesan background: {e}")


@router.post("/")
async def receive_webhook(payload: dict, background_tasks: BackgroundTasks):
    """Menerima webhook payload dari berbagai platform dan menormalisasinya."""
    try:
        # Deteksi format payload Telegram secara heuristik
        if "update_id" in payload and "message" in payload:
            platform = "telegram"
            msg = payload["message"]
            chat_id = str(msg["chat"]["id"])
            sender_id = str(msg["from"]["id"])
            content = msg.get("text", "")
            message_id = str(msg["message_id"])
            timestamp = datetime.now().isoformat()
        else:
            # Fallback untuk format payload generic / platform lain
            platform = payload.get("platform", "unknown")
            chat_id = str(payload.get("chat_id", ""))
            sender_id = str(payload.get("sender_id", ""))
            content = payload.get("content", "")
            message_id = str(
                payload.get("message_id", f"gen-{datetime.now().timestamp()}")
            )
            timestamp = datetime.now().isoformat()

        # Abaikan pesan kosong
        if not content:
            return {"status": "ignored", "reason": "empty content"}

        # Normalisasi menggunakan Pydantic Model
        normalized = NormalizedMessage(
            message_id=message_id,
            platform=platform,
            chat_id=chat_id,
            sender_id=sender_id,
            content=content,
            timestamp=timestamp,
            metadata=payload,
        )

        # Jadwalkan eksekusi pemrosesan secara background (Non-blocking)
        background_tasks.add_task(process_message_background, normalized)

        return {"status": "accepted", "message_id": message_id}

    except Exception as e:
        logger.error(f"Kesalahan struktur webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload format") from e
