from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton

from shared.utils.voice_manager import VoiceManager


class MicButton(QPushButton):
    """Komponen UI kustom untuk tombol Mikrofon dengan penanganan status."""

    # Sinyal yang dipancarkan ketika pendengaran selesai
    speech_recognized = Signal(str)
    speech_error = Signal(str)
    state_changed = Signal(bool)  # True jika sedang mendengarkan, False jika idle

    def __init__(self, voice_manager: VoiceManager, parent=None):
        super().__init__("🎤", parent)
        self.voice_manager = voice_manager
        self.setToolTip("Gunakan Suara")

        self.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border-radius: 15px;
                font-size: 16px;
                padding: 5px;
                min-width: 30px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #3b3b3b;
            }
            QPushButton:disabled {
                background-color: #d9534f;
                color: #ffffff;
            }
        """)

        self.clicked.connect(self._on_click)

    def _on_click(self):
        """Handler saat tombol diklik."""
        self.setEnabled(False)
        self.setText("👂")
        self.state_changed.emit(True)

        # Panggil voice manager untuk mendengarkan
        self.voice_manager.listen(self._on_listen_done)

    def _on_listen_done(self, text: str, error: str | None):
        """Callback dari background thread VoiceManager."""
        self.setEnabled(True)
        self.setText("🎤")
        self.state_changed.emit(False)

        if error:
            self.speech_error.emit(error)
        elif text:
            self.speech_recognized.emit(text)
