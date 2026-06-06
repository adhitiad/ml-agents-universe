"""Egress Adapter untuk Omnichannel Messaging.

Modul ini bertanggung jawab untuk mengirimkan balasan kembali
ke platform asal pesan (seperti Telegram, Discord) secara asynchronous.
"""

import logging
import os

import httpx


logger = logging.getLogger(__name__)


class OmnichannelSender:
    """Kelas untuk menangani pengiriman balasan ke berbagai platform."""

    def __init__(self):
        # Mengambil token dari environment
        self.telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.discord_token = os.environ.get("DISCORD_BOT_TOKEN")

    async def send_reply(self, platform: str, chat_id: str, text: str) -> bool:
        """Kirim balasan ke platform tujuan secara asynchronous."""
        platform = platform.lower()

        try:
            if platform == "telegram":
                return await self._send_telegram(chat_id, text)
            elif platform == "discord":
                logger.warning(
                    "Pengiriman ke Discord belum diimplementasikan sepenuhnya."
                )
                return False
            else:
                logger.error(f"Platform tidak didukung untuk balasan: {platform}")
                return False
        except Exception as e:
            logger.error(f"Gagal mengirim pesan ke {platform} ({chat_id}): {e}")
            return False

    async def _send_telegram(self, chat_id: str, text: str) -> bool:
        if not self.telegram_token:
            logger.warning("TELEGRAM_BOT_TOKEN tidak dikonfigurasi.")
            return False

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)

            if response.status_code == 200:
                logger.info(f"Berhasil membalas ke Telegram chat {chat_id}")
                return True
            else:
                logger.error(f"Gagal membalas ke Telegram: {response.text}")
                return False


# Global instance
sender = OmnichannelSender()
