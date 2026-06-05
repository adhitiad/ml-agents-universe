import os
import sys


# Memastikan direktori root berada dalam PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtWidgets import QApplication

from shared.utils.hotkey_manager import HotkeyManager
from ui.main_window import MainWindow
from ui.setup_wizard import SetupWizard
from ui.tray_icon import SystemTrayManager


def main():
    app = QApplication(sys.argv)

    # Check if config exists
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
    config_path = os.path.join(data_dir, "desktop_config.json")

    if not os.path.exists(config_path):
        wizard = SetupWizard()
        if wizard.exec() == 0:  # 0 means Rejected (closed without saving)
            sys.exit(0)

    # Inisialisasi dan tampilkan jendela utama
    window = MainWindow()
    window.show()

    # Inisialisasi System Tray
    tray_manager = SystemTrayManager(window)
    tray_manager.show_tray()

    # Inisialisasi Global Hotkeys (Alt+Space)
    hotkey_manager = HotkeyManager()
    hotkey_manager.register_hotkey("alt+space", tray_manager.toggle_window)

    # Memulai event loop Qt
    exit_code = app.exec()

    # Cleanup saat aplikasi tertutup (melalui tombol Keluar di System Tray)
    hotkey_manager.unregister_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
