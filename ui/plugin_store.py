from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from shared.utils.plugin_manager import PluginManager


class PluginStoreDialog(QDialog):
    """Jendela UI untuk mengelola dan mengunduh ekstensi Agen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ML Agents - Plugin Store")
        self.setFixedSize(600, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QLabel {
                font-family: 'Segoe UI', Arial;
                color: #d4d4d4;
            }
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 5px;
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #444;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton#btn_install {
                background-color: #28a745;
            }
            QPushButton#btn_install:hover {
                background-color: #218838;
            }
        """)

        self.plugin_manager = PluginManager()
        self.setup_ui()
        self.load_local_plugins()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(
            "<b>Agent Plugin Store</b><br>Kelola dan instal kemampuan baru untuk asisten Anda."
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # List Plugins
        self.plugin_list = QListWidget()
        layout.addWidget(self.plugin_list)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh List")
        self.btn_refresh.clicked.connect(self.load_local_plugins)

        self.btn_install = QPushButton("Simulasikan Unduh Plugin Baru")
        self.btn_install.setObjectName("btn_install")
        self.btn_install.clicked.connect(self.simulate_download)

        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_install)

        layout.addLayout(btn_layout)

    def load_local_plugins(self):
        """Memuat daftar plugin yang sudah terinstal di folder lokal."""
        self.plugin_list.clear()
        plugins = self.plugin_manager.discover_plugins()

        if not plugins:
            item = QListWidgetItem(
                "Belum ada plugin terinstal. Klik tombol unduh di bawah."
            )
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.plugin_list.addItem(item)
            return

        for folder_name, meta in plugins.items():
            name = meta.get("name", folder_name)
            desc = meta.get("description", "Tidak ada deskripsi")
            ver = meta.get("version", "1.0.0")

            display_text = f"📦 {name} (v{ver})\n└ {desc}"
            item = QListWidgetItem(display_text)
            self.plugin_list.addItem(item)

    def simulate_download(self):
        """Simulasi mengunduh plugin baru dari internet."""
        QMessageBox.information(
            self,
            "Download Simulator",
            "Fitur ini akan terhubung ke Cloud Server ML Agents Universe untuk mengunduh agen baru secara dinamis.\n\n(Hanya tersedia jika backend server sudah disiapkan di Fase Produksi)",
        )
