"""Mathematical helper functions untuk ML dan data analysis.

Module ini menyediakan:
- Normalization (min-max, z-score)
- Distance metrics (cosine, euclidean)
- Safe arithmetic (divide-by-zero handling)
- Statistical helpers (moving average)
"""

from __future__ import annotations

import math
from collections.abc import Sequence


def normalize_min_max(
    values: Sequence[float],
    feature_min: float | None = None,
    feature_max: float | None = None,
) -> list[float]:
    """Min-max normalization ke range [0, 1].

    Args:
        values: Sequence angka yang akan dinormalisasi.
        feature_min: Minimum value (None = hitung dari data).
        feature_max: Maximum value (None = hitung dari data).

    Returns:
        List angka yang sudah dinormalisasi ke [0, 1].

    Raises:
        ValueError: Jika values kosong.
    """
    if not values:
        raise ValueError("Input values tidak boleh kosong")

    v_min = feature_min if feature_min is not None else min(values)
    v_max = feature_max if feature_max is not None else max(values)
    range_val = v_max - v_min

    if range_val == 0:
        return [0.0] * len(values)

    return [(v - v_min) / range_val for v in values]


def normalize_z_score(
    values: Sequence[float],
    mean: float | None = None,
    std: float | None = None,
) -> list[float]:
    """Z-score normalization (standardization).

    Args:
        values: Sequence angka yang akan dinormalisasi.
        mean: Mean value (None = hitung dari data).
        std: Standard deviation (None = hitung dari data).

    Returns:
        List angka yang sudah di-standardize.

    Raises:
        ValueError: Jika values kosong.
    """
    if not values:
        raise ValueError("Input values tidak boleh kosong")

    n = len(values)
    mu = mean if mean is not None else sum(values) / n

    if std is not None:
        sigma = std
    else:
        variance = sum((v - mu) ** 2 for v in values) / n
        sigma = math.sqrt(variance)

    if sigma == 0:
        return [0.0] * n

    return [(v - mu) / sigma for v in values]


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Hitung cosine similarity antara dua vector.

    Args:
        a: Vector pertama.
        b: Vector kedua.

    Returns:
        Cosine similarity dalam range [-1, 1].

    Raises:
        ValueError: Jika vector memiliki panjang berbeda atau kosong.
    """
    if len(a) != len(b):
        raise ValueError(f"Vector harus memiliki panjang sama: {len(a)} != {len(b)}")
    if not a:
        raise ValueError("Vector tidak boleh kosong")

    dot_product = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def euclidean_distance(a: Sequence[float], b: Sequence[float]) -> float:
    """Hitung Euclidean distance antara dua vector.

    Args:
        a: Vector pertama.
        b: Vector kedua.

    Returns:
        Euclidean distance (selalu >= 0).

    Raises:
        ValueError: Jika vector memiliki panjang berbeda atau kosong.
    """
    if len(a) != len(b):
        raise ValueError(f"Vector harus memiliki panjang sama: {len(a)} != {len(b)}")
    if not a:
        raise ValueError("Vector tidak boleh kosong")

    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b, strict=True)))


def safe_divide(
    numerator: float,
    denominator: float,
    default: float = 0.0,
) -> float:
    """Division yang aman terhadap zero-division.

    Args:
        numerator: Pembilang.
        denominator: Penyebut.
        default: Nilai fallback jika denominator == 0.

    Returns:
        Hasil pembagian, atau default jika denominator nol.
    """
    if denominator == 0:
        return default
    return numerator / denominator


def moving_average(
    values: Sequence[float],
    window: int,
) -> list[float]:
    """Simple Moving Average (SMA).

    Args:
        values: Sequence angka input.
        window: Ukuran window untuk averaging.

    Returns:
        List moving averages. Panjang = len(values) - window + 1.

    Raises:
        ValueError: Jika window <= 0 atau window > len(values).
    """
    if window <= 0:
        raise ValueError("Window harus > 0")
    if not values:
        return []
    if window > len(values):
        raise ValueError(
            f"Window ({window}) tidak boleh lebih besar dari "
            f"jumlah values ({len(values)})"
        )

    result: list[float] = []
    window_sum = sum(values[:window])
    result.append(window_sum / window)

    for i in range(window, len(values)):
        window_sum += values[i] - values[i - window]
        result.append(window_sum / window)

    return result


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value ke range [min_val, max_val].

    Args:
        value: Nilai yang akan di-clamp.
        min_val: Batas bawah.
        max_val: Batas atas.

    Returns:
        Nilai yang sudah di-clamp.
    """
    return max(min_val, min(value, max_val))


def percentage_change(old_value: float, new_value: float) -> float:
    """Hitung percentage change antara dua nilai.

    Args:
        old_value: Nilai lama.
        new_value: Nilai baru.

    Returns:
        Percentage change. Jika old_value == 0, return 0.0.
    """
    return safe_divide(new_value - old_value, abs(old_value)) * 100.0
