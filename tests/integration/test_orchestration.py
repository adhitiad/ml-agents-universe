"""Pengujian komunikasi lintas agen."""

from tests.utils.mock_llm import MockLLM


def test_multi_agent_orchestration():
    """Simulasi: NLP -> Finance -> Economy"""
    # 1. NLP mencerna sentimen
    llm = MockLLM(responses={"sentiment": "Positive outlook on market."})
    nlp_out = llm.invoke("extract sentiment from report")
    assert "Positive" in nlp_out

    # 2. Finance memprediksi harga berdasarkan sentimen NLP
    llm_fin = MockLLM(responses={"Positive": "Buy signal, target $120"})
    fin_out = llm_fin.invoke(nlp_out)
    assert "Buy" in fin_out

    # 3. Economy merevisi GDP berdasarkan capital flow dari Finance
    llm_eco = MockLLM(responses={"Buy": "GDP growth adjusted to +2.5%"})
    eco_out = llm_eco.invoke(fin_out)
    assert "GDP" in eco_out
