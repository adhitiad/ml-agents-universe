from agents.mathematics.src.agent.math_agent import MathAgent
from agents.mathematics.src.env.math_env import ProofEnvironment
from agents.mathematics.src.models.math_models import (
    ProofStepModel,
    ReasoningModel,
    TheoremModel,
)
from agents.mathematics.src.tools.math_tools import (
    LaTeXConverterTool,
    MathSearchTool,
    ProofCheckerTool,
    SymbolicSolverTool,
)
from shared.models import AgentConfig, AgentDomain, AgentState


def test_math_models():
    ps = ProofStepModel(step_number=1, statement="x=1", justification="given")
    assert ps.is_valid is None

    tm = TheoremModel(name="Pythagoras", statement="a^2+b^2=c^2")
    assert len(tm.prerequisites) == 0

    rm = ReasoningModel(problem_statement="Solve x", steps=[ps])
    assert not rm.conclusion_reached


def test_math_env():
    env = ProofEnvironment("T1")
    ps_valid = ProofStepModel(step_number=1, statement="A", justification="B")
    res1 = env.add_step(ps_valid)
    assert res1["status"] == "accepted"

    ps_invalid = ProofStepModel(step_number=2, statement="invalid math", justification="none")
    res2 = env.add_step(ps_invalid)
    assert res2["status"] == "rejected"


def test_math_tools():
    ss = SymbolicSolverTool()
    assert ss._run("x+1=2")["solution"] == "x = 1"
    assert ss._run("x+2=2")["solution"] == "x = 0"

    pc = ProofCheckerTool()
    assert pc._run("A", "B")["is_valid"] is True
    assert pc._run("invalid", "C")["is_valid"] is False

    lc = LaTeXConverterTool()
    assert "\\begin{equation}" in lc._run("x=1")["latex"]

    ms = MathSearchTool()
    assert "Definisi standar" in ms._run("Limit")["definition"]


def test_math_agent():
    cfg = AgentConfig(name="MathTest", domain=AgentDomain.MATHEMATICS)
    agent = MathAgent(config=cfg)
    agent.compile()

    assert agent.health_check().status == "healthy"
    state = AgentState(messages=[])
    res = agent.run(state)
    assert "metadata" in res.model_dump()
