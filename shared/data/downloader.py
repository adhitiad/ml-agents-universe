"""Unified Dataset Downloader.

Utility terpusat untuk mengunduh dataset dari berbagai sumber:
HTTP direct download, HuggingFace datasets, dan file lokal.
Mendukung streaming download, checksum, dan idempotent skip.
"""

from __future__ import annotations

import hashlib
import logging
import zipfile
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Ukuran chunk untuk streaming download (64 KB)
_CHUNK_SIZE = 65_536


class DatasetDownloader:
    """Mengunduh dataset dari berbagai sumber secara idempotent."""

    def __init__(self, base_dir: Path | None = None) -> None:
        """Inisialisasi downloader.

        Args:
            base_dir: Direktori root data. Default: `data/raw/` relatif ke project root.
        """
        if base_dir is None:
            base_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def domain_dir(self, domain: str) -> Path:
        """Mengembalikan path direktori untuk domain tertentu.

        Args:
            domain: Nama domain agent (nlp, finance, dll).

        Returns:
            Path ke direktori domain.
        """
        d = self.base_dir / domain
        d.mkdir(parents=True, exist_ok=True)
        return d

    def download_http(
        self,
        url: str,
        dest_path: Path,
        *,
        expected_sha256: str | None = None,
        timeout: float = 300.0,
    ) -> Path:
        """Download file via HTTP streaming.

        Args:
            url: URL sumber file.
            dest_path: Path tujuan penyimpanan.
            expected_sha256: Hash SHA256 yang diharapkan (opsional).
            timeout: Timeout dalam detik.

        Returns:
            Path file yang telah diunduh.

        Raises:
            ValueError: Jika checksum tidak cocok.
            httpx.HTTPStatusError: Jika HTTP request gagal.
        """
        if dest_path.exists():
            logger.info("File sudah ada, skip download: %s", dest_path)
            return dest_path

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Mengunduh %s → %s", url, dest_path)

        hasher = hashlib.sha256()
        with httpx.stream("GET", url, timeout=timeout, follow_redirects=True) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0

            with open(dest_path, "wb") as f:
                for chunk in resp.iter_bytes(chunk_size=_CHUNK_SIZE):
                    f.write(chunk)
                    hasher.update(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = (downloaded / total) * 100
                        if downloaded % (1024 * 1024) < _CHUNK_SIZE:
                            logger.info(
                                "  Progress: %.1f%% (%d / %d bytes)",
                                pct,
                                downloaded,
                                total,
                            )

        if expected_sha256 and hasher.hexdigest() != expected_sha256:
            dest_path.unlink()
            msg = (
                f"Checksum mismatch! Expected {expected_sha256}, "
                f"got {hasher.hexdigest()}"
            )
            raise ValueError(msg)

        logger.info("Download selesai: %s (%d bytes)", dest_path, downloaded)
        return dest_path

    def download_and_extract_zip(
        self,
        url: str,
        extract_dir: Path,
        *,
        timeout: float = 300.0,
    ) -> Path:
        """Download file ZIP dan ekstrak ke direktori.

        Args:
            url: URL file ZIP.
            extract_dir: Direktori tujuan ekstraksi.
            timeout: Timeout dalam detik.

        Returns:
            Path direktori hasil ekstraksi.
        """
        if extract_dir.exists() and any(extract_dir.iterdir()):
            logger.info("Direktori sudah ada & berisi file, skip: %s", extract_dir)
            return extract_dir

        zip_path = extract_dir.parent / "temp_download.zip"
        self.download_http(url, zip_path, timeout=timeout)

        logger.info("Mengekstrak ZIP → %s", extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        zip_path.unlink()
        logger.info("Ekstraksi selesai: %s", extract_dir)
        return extract_dir

    def download_huggingface(
        self,
        repo_id: str,
        dest_dir: Path,
        *,
        split: str = "train",
        max_samples: int | None = None,
    ) -> list[dict[str, Any]]:
        """Download dataset dari HuggingFace Hub.

        Args:
            repo_id: ID repository HuggingFace (misal: 'claritylab/utcd').
            dest_dir: Direktori untuk menyimpan cache.
            split: Split dataset (train, test, validation).
            max_samples: Limit jumlah sampel. None = semua.

        Returns:
            List of dict berisi data records.
        """
        try:
            from datasets import load_dataset
        except ImportError:
            logger.warning(
                "Library 'datasets' tidak terinstall. "
                "Install dengan: pip install datasets"
            )
            return []

        logger.info("Mengunduh dataset HuggingFace: %s (split=%s)", repo_id, split)
        dest_dir.mkdir(parents=True, exist_ok=True)

        ds = load_dataset(repo_id, split=split, cache_dir=str(dest_dir))

        if max_samples is not None:
            ds = ds.select(range(min(max_samples, len(ds))))

        records = [dict(row) for row in ds]
        logger.info("HuggingFace download selesai: %d records", len(records))
        return records

    @staticmethod
    def compute_sha256(file_path: Path) -> str:
        """Hitung SHA256 checksum dari file.

        Args:
            file_path: Path ke file.

        Returns:
            String hex SHA256.
        """
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(_CHUNK_SIZE):
                hasher.update(chunk)
        return hasher.hexdigest()
