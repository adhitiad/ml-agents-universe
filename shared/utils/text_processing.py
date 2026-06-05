"""Text processing utilities untuk NLP dan data cleaning.

Module ini menyediakan fungsi-fungsi sederhana untuk:
- Cleaning teks (strip HTML, normalize whitespace)
- Tokenisasi sederhana (whitespace + punctuation)
- Truncation dengan word boundary
- Keyword extraction berbasis frekuensi
"""

from __future__ import annotations

import re
import string
from collections import Counter


# Pre-compiled regex patterns
_HTML_TAG_PATTERN: re.Pattern[str] = re.compile(r"<[^>]+>")
_MULTI_WHITESPACE_PATTERN: re.Pattern[str] = re.compile(r"\s+")
_URL_PATTERN: re.Pattern[str] = re.compile(
    r"https?://[^\s<>\"']+|www\.[^\s<>\"']+",
)

# Common stopwords (Bahasa Indonesia + English minimal set)
_STOPWORDS: frozenset[str] = frozenset(
    {
        # English
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "shall",
        "can",
        "need",
        "dare",
        "ought",
        "and",
        "but",
        "or",
        "nor",
        "not",
        "so",
        "yet",
        "both",
        "either",
        "neither",
        "each",
        "every",
        "all",
        "any",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "only",
        "own",
        "same",
        "than",
        "too",
        "very",
        "just",
        "because",
        "as",
        "until",
        "while",
        "of",
        "at",
        "by",
        "for",
        "with",
        "about",
        "against",
        "between",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "to",
        "from",
        "up",
        "down",
        "in",
        "out",
        "on",
        "off",
        "over",
        "under",
        "again",
        "then",
        "once",
        "here",
        "there",
        "when",
        "where",
        "why",
        "how",
        "what",
        "which",
        "who",
        "whom",
        "this",
        "that",
        "these",
        "those",
        "i",
        "me",
        "my",
        "myself",
        "we",
        "our",
        "ours",
        "you",
        "your",
        "he",
        "him",
        "his",
        "she",
        "her",
        "it",
        "its",
        "they",
        "them",
        "their",
        # Bahasa Indonesia
        "dan",
        "atau",
        "ini",
        "itu",
        "yang",
        "di",
        "ke",
        "dari",
        "untuk",
        "dengan",
        "pada",
        "adalah",
        "akan",
        "sudah",
        "telah",
        "sedang",
        "juga",
        "saya",
        "kami",
        "kita",
        "mereka",
        "anda",
        "dia",
        "beliau",
        "tidak",
        "bukan",
        "jangan",
        "oleh",
        "dalam",
        "lagi",
        "masih",
        "hanya",
        "ada",
        "bisa",
        "dapat",
        "harus",
        "perlu",
        "jika",
        "kalau",
        "maka",
        "karena",
        "sebab",
        "agar",
        "supaya",
        "tetapi",
        "namun",
        "walau",
        "meski",
        "saat",
        "ketika",
        "sebelum",
        "sesudah",
    }
)


def clean_text(text: str, remove_urls: bool = True) -> str:
    """Bersihkan teks dari HTML tags, URLs, dan whitespace berlebih.

    Args:
        text: Teks input yang akan dibersihkan.
        remove_urls: Jika True, hapus URLs dari teks.

    Returns:
        Teks yang sudah dibersihkan.
    """
    result = text

    # Hapus HTML tags
    result = _HTML_TAG_PATTERN.sub(" ", result)

    # Hapus URLs
    if remove_urls:
        result = _URL_PATTERN.sub(" ", result)

    # Normalize whitespace
    result = _MULTI_WHITESPACE_PATTERN.sub(" ", result)

    return result.strip()


def simple_tokenize(
    text: str,
    lowercase: bool = True,
    remove_punctuation: bool = True,
) -> list[str]:
    """Tokenisasi sederhana berbasis whitespace dan punctuation.

    Args:
        text: Teks yang akan di-tokenisasi.
        lowercase: Jika True, convert ke lowercase.
        remove_punctuation: Jika True, hapus punctuation.

    Returns:
        Daftar token.
    """
    if lowercase:
        text = text.lower()

    if remove_punctuation:
        text = text.translate(str.maketrans("", "", string.punctuation))

    tokens = text.split()
    return [t for t in tokens if t]


def truncate_text(
    text: str,
    max_length: int,
    suffix: str = "...",
    respect_word_boundary: bool = True,
) -> str:
    """Truncate teks ke panjang maksimum dengan word boundary.

    Args:
        text: Teks yang akan di-truncate.
        max_length: Panjang maksimum output (termasuk suffix).
        suffix: String yang ditambahkan di akhir jika terpotong.
        respect_word_boundary: Jika True, potong di batas kata.

    Returns:
        Teks yang sudah di-truncate.
    """
    if len(text) <= max_length:
        return text

    truncate_at = max_length - len(suffix)
    if truncate_at <= 0:
        return suffix[:max_length]

    truncated = text[:truncate_at]

    if respect_word_boundary:
        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space]

    return truncated.rstrip() + suffix


def extract_keywords(
    text: str,
    top_n: int = 10,
    min_word_length: int = 3,
    stopwords: frozenset[str] | None = None,
) -> list[str]:
    """Ekstrak keywords dari teks berdasarkan frekuensi term.

    Menggunakan simple term frequency (TF) tanpa IDF.
    Untuk produksi, gunakan library NLP seperti spaCy atau NLTK.

    Args:
        text: Teks sumber.
        top_n: Jumlah keywords teratas yang dikembalikan.
        min_word_length: Panjang minimum kata untuk dipertimbangkan.
        stopwords: Set stopwords kustom (None = gunakan default).

    Returns:
        Daftar keywords terurut berdasarkan frekuensi.
    """
    if stopwords is None:
        stopwords = _STOPWORDS

    tokens = simple_tokenize(text, lowercase=True, remove_punctuation=True)

    # Filter stopwords dan kata pendek
    filtered = [t for t in tokens if len(t) >= min_word_length and t not in stopwords]

    # Hitung frekuensi
    counter = Counter(filtered)
    return [word for word, _ in counter.most_common(top_n)]


def count_words(text: str) -> int:
    """Hitung jumlah kata dalam teks.

    Args:
        text: Teks input.

    Returns:
        Jumlah kata.
    """
    return len(text.split())


def normalize_whitespace(text: str) -> str:
    """Normalize semua whitespace menjadi single space.

    Args:
        text: Teks input.

    Returns:
        Teks dengan whitespace yang dinormalisasi.
    """
    return _MULTI_WHITESPACE_PATTERN.sub(" ", text).strip()
