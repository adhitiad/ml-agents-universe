import math

from agents.education.src.agent.education_agent import EducationAgent
from agents.education.src.env.education_env import (
    ClassroomEnvironment,
    TutoringEnvironment,
)
from agents.education.src.models.education_models import (
    ItemModel,
    LearningPathModel,
    StudentModel,
)
from agents.education.src.tools.education_tools import (
    AssessmentGeneratorTool,
    ContentRecommenderTool,
    IRTCalculatorTool,
    KnowledgeTracerTool,
)
from shared.models import AgentConfig, AgentDomain, AgentState


def test_education_models_anonymization():
    # Test hashing and PII protection
    sm = StudentModel(student_id="john_doe_123")
    assert sm.anonymized is True
    assert sm.student_id.startswith("anon_")
    assert "john" not in sm.student_id

    im = ItemModel(item_id="math_1", difficulty=0.5, discrimination=1.2)
    assert im.guessing == 0.0

    lp = LearningPathModel(topic_id="t1", prerequisites=["t0"])
    assert len(lp.prerequisites) == 1


def test_education_env():
    # Classroom
    c_env = ClassroomEnvironment(num_students=5)
    res = c_env.broadcast_lesson("algebra")
    assert res["status"] == "lesson_completed"
    assert res["students_reached"] == 5
    for st in c_env.students:
        assert math.isclose(st.knowledge_probability["algebra"], 0.15, abs_tol=0.01) # 0.1 + 0.05

    # Tutoring
    sm = StudentModel(student_id="test_student")
    t_env = TutoringEnvironment(sm)
    res_t = t_env.conduct_session("algebra", 0.8)
    assert res_t["status"] == "tutoring_completed"
    assert sm.knowledge_probability["algebra"] == 0.26 # 0.1 + (0.2 * 0.8)
    assert len(t_env.interaction_logs) == 1


def test_education_tools():
    # IRT
    irt = IRTCalculatorTool()
    res_irt = irt._run(ability=1.0, difficulty=1.0)
    assert math.isclose(res_irt["prob_correct"], 0.5, abs_tol=0.01)

    res_irt_overflow = irt._run(ability=-500.0, difficulty=500.0)
    assert res_irt_overflow["prob_correct"] == 0.0

    res_irt_underflow = irt._run(ability=500.0, difficulty=-500.0)
    assert res_irt_underflow["prob_correct"] == 1.0

    # BKT
    bkt = KnowledgeTracerTool()
    res_bkt_c = bkt._run(prior_prob=0.5, correct_answer=True)
    assert res_bkt_c["new_knowledge_prob"] > 0.5

    res_bkt_w = bkt._run(prior_prob=0.5, correct_answer=False)
    assert res_bkt_w["new_knowledge_prob"] < 0.5

    # Recommender
    rec = ContentRecommenderTool()
    assert rec._run("algebra")["recommended_topic"] == "algebra_advanced"

    # Assessment
    ass = AssessmentGeneratorTool()
    assert ass._run(0.7)["avg_difficulty"] == 0.7


def test_education_agent():
    cfg = AgentConfig(name="EducationAgentTest", domain=AgentDomain.EDUCATION)
    agent = EducationAgent(config=cfg)
    agent.compile()

    hc = agent.health_check()
    assert hc.status == "healthy"

    state = AgentState(messages=[])
    res = agent.run(state)
    assert res.metadata.get("plan") is not None
