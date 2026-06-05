import logging

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget


logger = logging.getLogger(__name__)


class SystemTrayManager:
    """Manajer untuk System Tray Icon Windows."""

    def __init__(self, main_window: QWidget):
        self.main_window = main_window
        self.app = QApplication.instance()

        # Inisialisasi QSystemTrayIcon
        # Gunakan icon default dari style aplikasi jika belum ada file .ico khusus
        default_icon = self.main_window.style().standardIcon(
            self.main_window.style().StandardPixmap.SP_ComputerIcon
        )
        self.tray_icon = QSystemTrayIcon(default_icon, self.main_window)
        self.tray_icon.setToolTip("ML Agents Universe - Asisten AI")

        # Menu Konteks (Klik Kanan)
        self.tray_menu = QMenu(self.main_window)

        # Action: Tampilkan
        self.show_action = QAction("Tampilkan Asisten (Alt+Space)", self.main_window)
        self.show_action.triggered.connect(self.toggle_window)
        self.tray_menu.addAction(self.show_action)

        self.tray_menu.addSeparator()

        # Action: Keluar
        self.quit_action = QAction("Keluar", self.main_window)
        self.quit_action.triggered.connect(self.quit_app)
        self.tray_menu.addAction(self.quit_action)

        # Pasangkan menu ke Tray Icon
        self.tray_icon.setContextMenu(self.tray_menu)

        # Hubungkan sinyal klik
        self.tray_icon.activated.connect(self.on_tray_activated)

    def show_tray(self):
        """Menampilkan ikon di System Tray."""
        self.tray_icon.show()
        # Jika sistem tray berhasil ditampilkan, ubah behavior main window
        # agar tidak langsung mati saat jendela ditutup (close)
        if self.app:
            self.app.setQuitOnLastWindowClosed(False)  # type: ignore

    def on_tray_activated(self, reason):
        """Handler saat ikon tray diklik."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Klik kiri biasa -> toggle window
            self.toggle_window()

    def toggle_window(self):
        """Memunculkan atau menyembunyikan main window."""
        if self.main_window.isVisible():
            if self.main_window.isActiveWindow():
                self.main_window.hide()
            else:
                # Jika terlihat tapi di belakang, bawa ke depan
                self.main_window.activateWindow()
                self.main_window.raise_()
        else:
            self.main_window.showNormal()
            self.main_window.activateWindow()
            self.main_window.raise_()

    def quit_app(self):
        """Menutup aplikasi sepenuhnya."""
        # Kembalikan ke normal agar app bisa mati
        if self.app:
            self.app.setQuitOnLastWindowClosed(True)  # type: ignore
        self.tray_icon.hide()
        if self.app:
            self.app.quit()
