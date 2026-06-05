import logging
import os
import sys
import winreg


logger = logging.getLogger(__name__)


class StartupManager:
    """Manajer untuk menambahkan/menghapus aplikasi dari Windows Startup."""

    APP_NAME = "ML_Agents_Universe"

    @staticmethod
    def get_executable_path() -> str:
        """Mengembalikan jalur absolut ke executable atau script."""
        # Jika dikompilasi dengan Nuitka, sys.executable adalah path ke .exe
        if getattr(sys, "frozen", False) or (
            sys.executable.endswith(".exe") and "python" not in sys.executable.lower()
        ):
            return sys.executable

        # Fallback untuk mode development
        return os.path.abspath(sys.argv[0])

    @staticmethod
    def is_auto_start_enabled() -> bool:
        """Mengecek apakah aplikasi sudah ada di registry startup."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ,
            )
            value, _ = winreg.QueryValueEx(key, StartupManager.APP_NAME)
            winreg.CloseKey(key)
            return value == StartupManager.get_executable_path()
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Gagal membaca registry startup: {e}")
            return False

    @staticmethod
    def enable_auto_start() -> bool:
        """Menambahkan aplikasi ke registry startup."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            winreg.SetValueEx(
                key,
                StartupManager.APP_NAME,
                0,
                winreg.REG_SZ,
                StartupManager.get_executable_path(),
            )
            winreg.CloseKey(key)
            logger.info("Berhasil mendaftarkan ML Agents Universe ke Windows Startup.")
            return True
        except Exception as e:
            logger.error(f"Gagal mendaftarkan ke startup: {e}")
            return False

    @staticmethod
    def disable_auto_start() -> bool:
        """Menghapus aplikasi dari registry startup."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            winreg.DeleteValue(key, StartupManager.APP_NAME)
            winreg.CloseKey(key)
            logger.info("Berhasil menghapus ML Agents Universe dari Windows Startup.")
            return True
        except FileNotFoundError:
            return True  # Sudah tidak ada
        except Exception as e:
            logger.error(f"Gagal menghapus dari startup: {e}")
            return False
