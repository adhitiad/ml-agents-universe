"""Tools untuk OS execution.

Module ini mendefinisikan tool untuk mengeksekusi perintah shell/terminal.
"""

import subprocess

from pydantic import BaseModel, Field

from shared.agent.tools.base import BaseTool


class RunCommandInput(BaseModel):
    command: str = Field(
        ...,
        description="Perintah shell/terminal yang akan dieksekusi (misal: 'mkdir test', 'dir', 'python --version').",
    )


class RunCommandTool(BaseTool):
    name: str = "run_command"
    description: str = "Mengeksekusi perintah command-line/terminal di sistem operasi (Windows/Linux/Mac). Gunakan untuk membuka aplikasi atau menjalankan skrip."
    args_schema: type[BaseModel] | None = RunCommandInput

    def _run(self, command: str) -> str:
        try:
            # Gunakan shell=True agar bisa eksekusi command bawaan shell seperti 'dir', 'start', dll.
            # Timeout 30 detik agar tidak hang.
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )

            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"

            if result.returncode == 0:
                return f"Perintah berhasil dieksekusi.\n{output}"
            else:
                return f"Perintah gagal dengan kode {result.returncode}.\n{output}"
        except subprocess.TimeoutExpired:
            return "Error: Eksekusi perintah timeout (melebihi 30 detik)."
        except Exception as e:
            return f"Error eksekusi perintah: {e!s}"
