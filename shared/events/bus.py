"""Asynchronous Event Bus berbasis RabbitMQ (aio-pika).

Digunakan untuk delegasi tugas asinkron antar agen di dalam ML Agents Universe.
Menggunakan konsep pertukaran pesan berbasis topik atau direct.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable, Coroutine
from typing import Any

import aio_pika

from shared.env.settings import DatabaseSettings


logger = logging.getLogger(__name__)


class EventBus:
    """Manajer Event Bus menggunakan RabbitMQ."""

    _instance = None
    _connection: aio_pika.RobustConnection | None = None
    _channel: aio_pika.RobustChannel | None = None

    def __new__(cls) -> EventBus:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        """Membuat koneksi ke RabbitMQ."""
        if self._connection and not self._connection.is_closed:
            return

        settings = DatabaseSettings()
        # Fallback default ke localhost jika tidak didefinisikan
        # Anda dapat menambahkan rabbitmq_url ke .env dan settings.py
        rabbitmq_url = getattr(
            settings, "rabbitmq_url", "amqp://guest:guest@localhost/"
        )

        try:
            self._connection = await aio_pika.connect_robust(rabbitmq_url)
            self._channel = await self._connection.channel()
            logger.info("Terhubung ke RabbitMQ Event Bus.")
        except Exception as e:
            logger.error(f"Gagal terhubung ke RabbitMQ: {e}")
            raise

    async def publish_task(self, target_agent: str, payload: dict[str, Any]) -> None:
        """Mempublikasikan tugas ke queue/agen spesifik."""
        if not self._channel:
            await self.connect()

        assert self._channel is not None

        queue_name = f"agent_{target_agent}_tasks"
        # Deklarasi antrean agar dijamin ada
        await self._channel.declare_queue(queue_name, durable=True)

        message_body = json.dumps(payload).encode("utf-8")
        message = aio_pika.Message(
            body=message_body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await self._channel.default_exchange.publish(
            message,
            routing_key=queue_name,
        )
        logger.info(f"Tugas berhasil dikirim ke agen '{target_agent}'.")

    async def consume_tasks(
        self,
        agent_name: str,
        callback: Callable[[dict[str, Any]], Coroutine[Any, Any, None]],
    ) -> None:
        """Mendengarkan tugas yang masuk untuk agen ini."""
        if not self._channel:
            await self.connect()

        assert self._channel is not None

        queue_name = f"agent_{agent_name}_tasks"
        queue = await self._channel.declare_queue(queue_name, durable=True)

        async def process_message(
            message: aio_pika.abc.AbstractIncomingMessage,
        ) -> None:
            async with message.process():
                try:
                    payload = json.loads(message.body.decode("utf-8"))
                    logger.info(f"[{agent_name}] Menerima tugas baru.")
                    await callback(payload)
                except Exception as e:
                    logger.error(f"[{agent_name}] Gagal memproses tugas: {e}")

        await queue.consume(process_message)
        logger.info(f"[{agent_name}] Mendengarkan antrean '{queue_name}'...")

    async def close(self) -> None:
        """Menutup koneksi."""
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("Koneksi RabbitMQ ditutup.")


event_bus = EventBus()
