"""Pabrik penghasil Data Dummy untuk Testing (Mirip Faker)."""

import random


class TestDataFactory:
    """Men-generate data sintetis per domain."""

    @staticmethod
    def generate_nlp_corpus(num_docs: int = 5) -> list[dict]:
        return [{"id": i, "text": f"This is sample document {i}."} for i in range(num_docs)]

    @staticmethod
    def generate_finance_ticks(num_ticks: int = 10) -> list[dict]:
        return [{"timestamp": "2026-06-04T10:00:00", "price": 100.0 + random.random()} for _ in range(num_ticks)]

    @staticmethod
    def generate_experiment_hypothesis() -> str:
        return "Hypothesis: Increasing X will increase Y by 10%."
