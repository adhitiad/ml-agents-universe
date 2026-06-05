from agents.science.src.agent.science_agent import ScienceAgent
from agents.science.src.env.science_env import LaboratoryEnvironment
from agents.science.src.models.science_models import (
    ExperimentModel,
    LiteratureModel,
    MolecularModel,
)
from agents.science.src.tools.science_tools import (
    ExperimentDesignerTool,
    LiteratureSearchTool,
    MolecularSimTool,
    StatisticalTestTool,
)
from shared.models import AgentConfig, AgentDomain, AgentState


def test_science_models():
    em = ExperimentModel(experiment_id="exp_1", hypothesis="H1")
    assert not em.is_completed

    mm = MolecularModel(smiles="C1=CC=CC=C1")
    assert mm.predicted_solubility == 0.0

    lm = LiteratureModel(doi="10.123/xyz", title="A", abstract="B")
    assert len(lm.embedding_vector) == 0


def test_science_env():
    env = LaboratoryEnvironment()
    em = ExperimentModel(experiment_id="exp_1", hypothesis="H1")

    res = env.run_experiment(em)
    assert res["status"] == "completed"
    assert res["significant"] is True
    assert env.active_experiments["exp_1"].is_completed


def test_science_tools():
    ls = LiteratureSearchTool()
    assert len(ls._run("Cancer")["results"]) == 2

    ed = ExperimentDesignerTool()
    assert ed._run("H1")["independent_vars"][0] == "temp"

    ms = MolecularSimTool()
    assert ms._run("C")["toxicity_risk"] == 0.2

    st = StatisticalTestTool()
    assert st._run("exp_1")["significant"] is True
    assert "error" in st._run("invalid_exp")


def test_science_agent():
    cfg = AgentConfig(name="SciTest", domain=AgentDomain.SCIENCE)
    agent = ScienceAgent(config=cfg)
    agent.compile()

    assert agent.health_check().status == "healthy"
    state = AgentState(messages=[])
    res = agent.run(state)
    assert res.messages == []
