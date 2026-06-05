"""Pengujian Data Pipeline end-to-end."""

from tests.utils.test_data_factory import TestDataFactory


def test_data_extraction_to_lake():
    """Simulasi ETL sederhana."""

    # 1. Extract
    raw_data = TestDataFactory.generate_finance_ticks(5)
    assert len(raw_data) == 5
    assert "price" in raw_data[0]

    # 2. Transform (Mock)
    transformed = [{"t": d["timestamp"], "p": d["price"] * 1.1} for d in raw_data]
    assert transformed[0]["p"] > 100.0

    # 3. Load (Mock)
    data_lake_sim = {}
    data_lake_sim["finance/processed"] = transformed
    assert len(data_lake_sim["finance/processed"]) == 5
