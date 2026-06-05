import logging
import threading
from collections.abc import Callable


logger = logging.getLogger(__name__)


class VoiceManager:
    """Manajer untuk Text-to-Speech (TTS) dan Speech-to-Text (STT) lokal."""

    def __init__(self):
        self.tts_engine = None
        self.recognizer = None
        self.microphone = None
        self._is_listening = False

        # Coba inisialisasi TTS (pyttsx3)
        try:
            import pyttsx3

            self.tts_engine = pyttsx3.init()
            # Opsional: Atur kecepatan dan volume
            self.tts_engine.setProperty("rate", 150)
            self.tts_engine.setProperty("volume", 1.0)
        except ImportError:
            logger.warning("Library 'pyttsx3' tidak ditemukan. TTS dinonaktifkan.")
        except Exception as e:
            logger.error(f"Gagal inisialisasi pyttsx3: {e}")

        # Coba inisialisasi STT (SpeechRecognition)
        try:
            import speech_recognition as sr

            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            # Kalibrasi noise di background thread
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except ImportError:
            logger.warning(
                "Library 'SpeechRecognition' / 'PyAudio' tidak ditemukan. STT dinonaktifkan."
            )
        except Exception as e:
            logger.error(f"Gagal inisialisasi microphone: {e}")

    def speak(self, text: str, on_complete: Callable | None = None):
        """Membacakan teks menggunakan suara sistem (non-blocking)."""
        engine = self.tts_engine
        if not engine:
            logger.warning("TTS Engine tidak tersedia.")
            if on_complete:
                on_complete()
            return

        def _speak_thread():
            try:
                # pyttsx3 bersifat blocking, jadi harus di thread terpisah
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                logger.error(f"Error saat speak TTS: {e}")
            finally:
                if on_complete:
                    on_complete()

        threading.Thread(target=_speak_thread, daemon=True).start()

    def listen(self, callback: Callable[[str, str | None], None]):
        """Mendengarkan suara dari microphone dan mengubah ke teks.
        callback(text: str, error: Optional[str])
        """
        recognizer = self.recognizer
        microphone = self.microphone

        if not recognizer or not microphone:
            callback("", "SpeechRecognition belum siap atau tidak ada microphone.")
            return

        if self._is_listening:
            logger.warning("Sudah sedang mendengarkan...")
            return

        self._is_listening = True

        def _listen_thread():
            try:
                with microphone as source:
                    logger.info("Mendengarkan suara...")
                    audio = recognizer.listen(
                        source, timeout=5, phrase_time_limit=10
                    )

                logger.info("Memproses suara...")
                # Gunakan Google Web Speech API (gratis) untuk saat ini,
                # Nanti bisa diganti dengan model Whisper lokal (offline) jika diinginkan.
                text = recognizer.recognize_google(audio, language="id-ID")  # type: ignore
                callback(text, None)
            except __import__(
                "speech_recognition", fromlist=["UnknownValueError"]
            ).UnknownValueError:
                callback("", "Suara tidak terdengar jelas.")
            except __import__(
                "speech_recognition", fromlist=["WaitTimeoutError"]
            ).WaitTimeoutError:
                callback("", "Tidak ada suara (Timeout).")
            except Exception as e:
                logger.error(f"Error saat mendengarkan: {e}")
                callback("", str(e))
            finally:
                self._is_listening = False

        threading.Thread(target=_listen_thread, daemon=True).start()
