import markdown
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from shared.utils.voice_manager import VoiceManager
from ui.controller import AgentController
from ui.mic_button import MicButton
from ui.plugin_store import PluginStoreDialog


class AgentWorker(QThread):
    """QThread untuk mengeksekusi LangGraph secara asinkron.

    Tujuannya agar tidak memblokir UI thread utama dari PySide6.
    """

    response_ready = Signal(str)

    def __init__(self, controller: AgentController, query: str):
        super().__init__()
        self.controller = controller
        self.query = query

    def run(self):
        try:
            response = self.controller.run_query(self.query)
            self.response_ready.emit(response)
        except Exception as e:
            self.response_ready.emit(f"Error: {e!s}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ML Agents Universe - Desktop Assistant (Qt)")
        self.resize(800, 600)

        # CSS Styling dasar
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QTextBrowser {
                background-color: #252526;
                color: #d4d4d4;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 10px;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
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
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QLabel {
                color: #cccccc;
                font-size: 18px;
                font-weight: bold;
            }
        """)

        self.controller = AgentController()
        self.worker = None
        self.voice_manager = VoiceManager()

        # Setup UI
        self._setup_ui()

        # Load History from SQLite
        history = self.controller.get_chat_history()
        if history:
            for role, text in history:
                self.append_message(role, text)
        else:
            # Welcome message if no history
            self.append_message(
                "agent",
                "Halo! Saya adalah System Agent. Memori saya kini terhubung ke SQLite. Apa yang bisa saya bantu hari ini?",
            )

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header Layout
        header_layout = QHBoxLayout()
        header = QLabel("🤖 Super Assistant (System Agent - Qt Native)")
        header_layout.addWidget(header)
        header_layout.addStretch()

        self.btn_store = QPushButton("🛒 Plugin Store")
        self.btn_store.clicked.connect(self.open_plugin_store)
        header_layout.addWidget(self.btn_store)

        main_layout.addLayout(header_layout)

        # Chat display
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(True)
        main_layout.addWidget(self.chat_display, stretch=1)

        # Input area
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(
            "Ketik instruksi atau pertanyaan Anda di sini..."
        )
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field, stretch=1)

        self.btn_mic = MicButton(self.voice_manager)
        self.btn_mic.speech_recognized.connect(self._on_speech_recognized)
        self.btn_mic.speech_error.connect(self._on_speech_error)
        self.btn_mic.state_changed.connect(self._on_mic_state_changed)
        input_layout.addWidget(self.btn_mic)

        self.send_button = QPushButton("Kirim")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)

    def append_message(self, role: str, text: str):
        """Menambahkan pesan ke dalam layar chat menggunakan HTML/Markdown."""
        # Convert markdown to html
        html_text = markdown.markdown(text, extensions=["fenced_code", "tables"])

        if role == "user":
            color = "#4daafc"
            align = "right"
            sender = "Anda"
        else:
            color = "#4ec9b0"
            align = "left"
            sender = "System Agent"

        # Membungkus HTML dalam div dengan styling warna
        chat_html = f"""
        <div style="text-align: {align}; margin-bottom: 10px;">
            <b style="color: {color};">{sender}:</b><br>
            <span style="color: #d4d4d4;">{html_text}</span>
        </div>
        """

        self.chat_display.append(chat_html)

    def send_message(self):
        query = self.input_field.text().strip()
        if not query:
            return

        # Tampilkan pesan user
        self.append_message("user", query)

        # Kosongkan dan matikan input
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)

        self.append_message("agent", "<i>Sedang memproses...</i>")

        # Mulai eksekusi background
        self.worker = AgentWorker(self.controller, query)
        self.worker.response_ready.connect(self.on_response_ready)
        self.worker.start()

    def on_response_ready(self, response: str):
        # Kita hapus teks 'Sedang memproses...' dengan trik sederhana (atau biarkan menumpuk,
        # tapi untuk kesederhanaan kita abaikan penghapusan, cukup tambahkan respon baru)
        self.append_message("agent", response)

        # Aktifkan kembali input
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()

        # Bacakan respon menggunakan suara
        self.voice_manager.speak(response)

    def open_plugin_store(self):
        dialog = PluginStoreDialog(self)
        dialog.exec()

    def _on_speech_recognized(self, text: str):
        self.input_field.setText(text)

    def _on_speech_error(self, error: str):
        self.input_field.setText(f"Error: {error}")

    def _on_mic_state_changed(self, is_listening: bool):
        if is_listening:
            self.input_field.setPlaceholderText("Mendengarkan...")
            self.send_button.setEnabled(False)
        else:
            self.input_field.setPlaceholderText(
                "Ketik instruksi atau pertanyaan Anda di sini..."
            )
            self.send_button.setEnabled(True)

    def closeEvent(self, event: QCloseEvent):
        """Sembunyikan jendela ke System Tray alih-alih menutup aplikasi."""
        self.hide()
        event.ignore()
