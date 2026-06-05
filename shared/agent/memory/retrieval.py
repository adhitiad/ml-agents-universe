"""Utilitas pengambilan memori (Retrieval Scoring).

Menyediakan fungsi utilitas untuk meranking pesan dari VectorStore
atau mengkombinasikan berbagai hasil search.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class RetrievedItem:
    text: str
    relevance_score: float
    recency_score: float = 0.0

    @property
    def final_score(self) -> float:
        """Kombinasi skor (misalnya 70% relevance, 30% recency)."""
        return (self.relevance_score * 0.7) + (self.recency_score * 0.3)


def calculate_recency_score(index: int, total_items: int) -> float:
    """Fungsi pembusukan (decay function) sederhana berdasarkan indeks.
    Indeks yang lebih mendekati total_items akan memiliki skor lebih tinggi (1.0).
    """
    if total_items <= 1:
        return 1.0
    return index / (total_items - 1)


def rank_items(items: Sequence[RetrievedItem]) -> list[RetrievedItem]:
    """Urutkan items berdasarkan final_score tertinggi."""
    return sorted(items, key=lambda x: x.final_score, reverse=True)
