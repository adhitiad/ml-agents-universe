import logging
import os
from typing import Any

from pydantic import BaseModel, Field

from shared.agent.tools.base import BaseTool


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Type Text Tool
# ---------------------------------------------------------------------------
class TypeTextInput(BaseModel):
    text: str = Field(..., description="Teks yang ingin diketik.")
    interval: float = Field(
        default=0.01, description="Jeda antar ketikan karakter (detik)."
    )


class TypeTextTool(BaseTool[TypeTextInput]):
    name: str = "type_text"
    description: str = (
        "Mengetikkan teks secara otomatis menggunakan keyboard di posisi kursor aktif."
    )
    args_schema: type[BaseModel] | None = TypeTextInput

    def _run(self, text: str, interval: float = 0.01) -> str:
        try:
            import pyautogui

            pyautogui.write(text, interval=interval)
            return f"Berhasil mengetik: '{text}'"
        except Exception as e:
            return f"Error saat mengetik: {e!s}"


# ---------------------------------------------------------------------------
# 2. Press Key Tool
# ---------------------------------------------------------------------------
class PressKeyInput(BaseModel):
    keys: list[str] = Field(
        ...,
        description="Daftar tombol yang akan ditekan bersamaan. Contoh: ['ctrl', 'c'] atau ['enter']",
    )


class PressKeyTool(BaseTool[PressKeyInput]):
    name: str = "press_key"
    description: str = (
        "Menekan satu tombol atau kombinasi tombol keyboard (shortcut). "
        "Gunakan array string, misal: ['ctrl', 'c'] atau ['enter']."
    )
    args_schema: type[BaseModel] | None = PressKeyInput

    def _run(self, keys: list[str]) -> str:
        try:
            import pyautogui

            if len(keys) == 1:
                pyautogui.press(keys[0])
            else:
                pyautogui.hotkey(*keys)
            return f"Berhasil menekan tombol: {keys}"
        except Exception as e:
            return f"Error saat menekan tombol: {e!s}"


# ---------------------------------------------------------------------------
# 3. Click Mouse Tool
# ---------------------------------------------------------------------------
class ClickMouseInput(BaseModel):
    x: int | None = Field(
        default=None,
        description="Koordinat piksel X. Jika kosong, klik di posisi saat ini.",
    )
    y: int | None = Field(
        default=None,
        description="Koordinat piksel Y. Jika kosong, klik di posisi saat ini.",
    )
    button: str = Field(
        default="left", description="Tombol mouse: 'left', 'right', 'middle'."
    )
    clicks: int = Field(
        default=1, description="Jumlah klik (contoh 2 untuk double click)."
    )


class ClickMouseTool(BaseTool[ClickMouseInput]):
    name: str = "click_mouse"
    description: str = "Memindahkan kursor mouse ke koordinat (X,Y) spesifik di layar lalu mengkliknya."
    args_schema: type[BaseModel] | None = ClickMouseInput

    def _run(
        self,
        x: int | None = None,
        y: int | None = None,
        button: str = "left",
        clicks: int = 1,
    ) -> str:
        try:
            import pyautogui

            pyautogui.click(x=x, y=y, button=button, clicks=clicks)
            return f"Berhasil klik '{button}' ({clicks}x) di posisi ({x}, {y})"
        except Exception as e:
            return f"Error saat klik mouse: {e!s}"


# ---------------------------------------------------------------------------
# 4. Take Screenshot Tool
# ---------------------------------------------------------------------------
class TakeScreenshotInput(BaseModel):
    filename: str = Field(
        default="screenshot.png",
        description="Nama file untuk menyimpan screenshot (misal: capture.png). Akan disimpan di working directory.",
    )


class TakeScreenshotTool(BaseTool[TakeScreenshotInput]):
    name: str = "take_screenshot"
    description: str = "Mengambil gambar tangkapan layar utama komputer (screenshot)."
    args_schema: type[BaseModel] | None = TakeScreenshotInput

    def _run(self, filename: str = "screenshot.png") -> str:
        try:
            import pyautogui

            filepath = os.path.abspath(filename)
            pyautogui.screenshot(filepath)
            return f"Berhasil mengambil screenshot, disimpan di: {filepath}"
        except Exception as e:
            return f"Error saat mengambil screenshot: {e!s}"


# ---------------------------------------------------------------------------
# Registry Exporter
# ---------------------------------------------------------------------------
def get_computer_tools() -> list[BaseTool[Any]]:
    """Mendapatkan semua instansi alat RPA untuk diregistrasi."""
    return [
        TypeTextTool(),
        PressKeyTool(),
        ClickMouseTool(),
        TakeScreenshotTool(),
    ]
