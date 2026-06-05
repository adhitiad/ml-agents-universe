"""Tools untuk operasi File System.

Module ini mendefinisikan tool untuk interaksi dengan file system seperti membaca,
menulis file, dan me-listing directory.
"""

import os

from pydantic import BaseModel, Field

from shared.agent.tools.base import BaseTool


class ReadFileInput(BaseModel):
    filepath: str = Field(
        ..., description="Absolute atau relative path ke file yang akan dibaca."
    )


class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = "Membaca isi teks dari sebuah file."
    args_schema: type[BaseModel] | None = ReadFileInput

    def _run(self, filepath: str) -> str:
        try:
            if not os.path.exists(filepath):
                return f"Error: File tidak ditemukan di path '{filepath}'"
            if not os.path.isfile(filepath):
                return f"Error: '{filepath}' bukan sebuah file."

            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            return f"Isi file {filepath}:\n{content}"
        except Exception as e:
            return f"Error membaca file: {e!s}"


class WriteFileInput(BaseModel):
    filepath: str = Field(
        ..., description="Absolute atau relative path ke file yang akan ditulis."
    )
    content: str = Field(
        ..., description="Teks konten yang akan dituliskan ke dalam file."
    )


class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = "Menulis atau menimpa teks ke dalam sebuah file. Jika file belum ada, file akan dibuat."
    args_schema: type[BaseModel] | None = WriteFileInput

    def _run(self, filepath: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return (
                f"Berhasil menulis {len(content)} karakter ke dalam file '{filepath}'."
            )
        except Exception as e:
            return f"Error menulis file: {e!s}"


class ListDirInput(BaseModel):
    directory: str = Field(..., description="Path direktori yang akan dilist isinya.")


class ListDirectoryTool(BaseTool):
    name: str = "list_directory"
    description: str = "Melihat isi dari sebuah folder/direktori."
    args_schema: type[BaseModel] | None = ListDirInput

    def _run(self, directory: str) -> str:
        try:
            if not os.path.exists(directory):
                return f"Error: Direktori '{directory}' tidak ditemukan."
            if not os.path.isdir(directory):
                return f"Error: '{directory}' bukan sebuah direktori."

            items = os.listdir(directory)
            if not items:
                return f"Direktori '{directory}' kosong."

            result = f"Isi direktori '{directory}':\n"
            for item in items:
                path = os.path.join(directory, item)
                item_type = "DIR " if os.path.isdir(path) else "FILE"
                result += f"[{item_type}] {item}\n"
            return result
        except Exception as e:
            return f"Error saat melist direktori: {e!s}"
