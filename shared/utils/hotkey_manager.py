import logging
from collections.abc import Callable


logger = logging.getLogger(__name__)


class HotkeyManager:
    """Manajer untuk Global Hotkeys menggunakan library 'keyboard'."""

    def __init__(self):
        self._is_running = False
        self._keyboard = None

        # Coba import keyboard secara dinamis agar tidak error jika belum diinstal
        try:
            import keyboard

            self._keyboard = keyboard
        except ImportError:
            logger.warning(
                "Library 'keyboard' belum diinstal. Global Hotkey dinonaktifkan."
            )

    def register_hotkey(self, hotkey_str: str, callback: Callable) -> bool:
        """Mendaftarkan kombinasi tombol global (misal: 'alt+space')."""
        if not self._keyboard:
            return False

        try:
            self._keyboard.add_hotkey(hotkey_str, callback, suppress=True)
            logger.info(f"Berhasil mendaftarkan hotkey: {hotkey_str}")
            return True
        except Exception as e:
            logger.error(f"Gagal mendaftarkan hotkey {hotkey_str}: {e}")
            return False

    def unregister_all(self):
        """Menghapus semua hotkey."""
        if self._keyboard:
            try:
                self._keyboard.unhook_all()
            except Exception as e:
                logger.error(f"Gagal melepas hook hotkey: {e}")
