"""File I/O helpers dengan pathlib dan error handling.

Module ini menyediakan fungsi-fungsi aman untuk operasi file:
- safe_read/safe_write dengan error handling
- atomic_write untuk menghindari data corruption
- ensure_directory untuk membuat direktori secara rekursif
- list_files untuk glob pattern matching

Semua paths menggunakan pathlib.Path sesuai aturan monorepo.
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path


logger = logging.getLogger(__name__)


def ensure_directory(path: str | Path) -> Path:
    """Buat direktori jika belum ada, termasuk parent directories.

    Args:
        path: Path ke direktori yang akan dibuat.

    Returns:
        Path object ke direktori yang sudah ada/dibuat.

    Raises:
        OSError: Jika gagal membuat direktori.
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.debug("Direktori tersedia: %s", dir_path)
    return dir_path


def safe_read(path: str | Path, encoding: str = "utf-8") -> str | None:
    """Baca file dengan error handling.

    Args:
        path: Path ke file yang akan dibaca.
        encoding: Encoding file (default: utf-8).

    Returns:
        Isi file sebagai string, atau None jika gagal.
    """
    file_path = Path(path)
    try:
        content = file_path.read_text(encoding=encoding)
        logger.debug("File berhasil dibaca: %s (%d chars)", file_path, len(content))
        return content
    except FileNotFoundError:
        logger.warning("File tidak ditemukan: %s", file_path)
        return None
    except OSError as exc:
        logger.error("Gagal membaca file %s: %s", file_path, exc)
        return None


def safe_read_bytes(path: str | Path) -> bytes | None:
    """Baca file sebagai bytes dengan error handling.

    Args:
        path: Path ke file yang akan dibaca.

    Returns:
        Isi file sebagai bytes, atau None jika gagal.
    """
    file_path = Path(path)
    try:
        return file_path.read_bytes()
    except FileNotFoundError:
        logger.warning("File tidak ditemukan: %s", file_path)
        return None
    except OSError as exc:
        logger.error("Gagal membaca file %s: %s", file_path, exc)
        return None


def safe_write(
    path: str | Path,
    content: str,
    encoding: str = "utf-8",
    create_parents: bool = True,
) -> bool:
    """Tulis konten ke file dengan error handling.

    Akan membuat parent directories jika belum ada.

    Args:
        path: Path ke file tujuan.
        content: Konten yang akan ditulis.
        encoding: Encoding file (default: utf-8).
        create_parents: Apakah buat parent dirs jika belum ada.

    Returns:
        True jika berhasil, False jika gagal.
    """
    file_path = Path(path)
    try:
        if create_parents:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding=encoding)
        logger.debug("File berhasil ditulis: %s (%d chars)", file_path, len(content))
        return True
    except OSError as exc:
        logger.error("Gagal menulis file %s: %s", file_path, exc)
        return False


def atomic_write(
    path: str | Path,
    content: str,
    encoding: str = "utf-8",
) -> bool:
    """Tulis konten ke file secara atomic via temp file + rename.

    Ini mencegah data corruption jika proses terinterupsi
    di tengah penulisan. File ditulis ke temp file terlebih
    dahulu, lalu di-rename ke path tujuan.

    Args:
        path: Path ke file tujuan.
        content: Konten yang akan ditulis.
        encoding: Encoding file (default: utf-8).

    Returns:
        True jika berhasil, False jika gagal.
    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        fd, tmp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w", encoding=encoding) as tmp_file:
                tmp_file.write(content)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())

            # Atomic rename (pada OS yang sama filesystem)
            tmp_path_obj = Path(tmp_path)
            tmp_path_obj.replace(file_path)
            logger.debug("Atomic write berhasil: %s", file_path)
            return True
        except Exception:
            # Cleanup temp file jika rename gagal
            Path(tmp_path).unlink(missing_ok=True)
            raise
    except OSError as exc:
        logger.error("Gagal atomic write %s: %s", file_path, exc)
        return False


def list_files(
    directory: str | Path,
    pattern: str = "*",
    recursive: bool = False,
) -> list[Path]:
    """List files dalam direktori dengan glob pattern.

    Args:
        directory: Path ke direktori.
        pattern: Glob pattern (default: "*" untuk semua file).
        recursive: Jika True, cari secara rekursif.

    Returns:
        Daftar Path ke file yang cocok.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        logger.warning("Direktori tidak ditemukan: %s", dir_path)
        return []

    if recursive:
        return sorted(f for f in dir_path.rglob(pattern) if f.is_file())
    return sorted(f for f in dir_path.glob(pattern) if f.is_file())


def get_file_size(path: str | Path) -> int | None:
    """Dapatkan ukuran file dalam bytes.

    Args:
        path: Path ke file.

    Returns:
        Ukuran file dalam bytes, atau None jika file tidak ada.
    """
    file_path = Path(path)
    try:
        return file_path.stat().st_size
    except OSError:
        return None
