from agents.entertainment.src.agent.entertainment_agent import EntertainmentAgent
from agents.entertainment.src.env.entertainment_env import StreamingEnvironment
from agents.entertainment.src.models.entertainment_models import (
    RecommendationModel,
    TrendModel,
    UserBehaviorModel,
)
from agents.entertainment.src.tools.entertainment_tools import (
    CollaborativeFilterTool,
    ContentBasedFilterTool,
    TrendAnalyzerTool,
    UserProfileTool,
)
from shared.models import AgentConfig, AgentDomain, AgentState


def test_entertainment_models():
    rm = RecommendationModel(user_id="u1", recommended_items=["movie1"], confidence_score=0.8, is_cold_start=False)
    assert rm.user_id == "u1"

    um = UserBehaviorModel(user_id="u2")
    um.watch_history.append("m1")
    assert len(um.watch_history) == 1

    tm = TrendModel(topic="anime", popularity_score=9.5, is_rising=True)
    assert tm.is_rising


def test_entertainment_env():
    env = StreamingEnvironment()
    res = env.simulate_watch("u1", "vid_a", 15.0)
    assert res["status"] == "watched"
    assert res["total_history"] == 1
    assert env.active_users["u1"].session_duration == 15.0


def test_entertainment_tools_cold_start():
    up = UserProfileTool()
    res1 = up._run("old_user")
    assert len(res1["history"]) > 0
    res2 = up._run("new_user")
    assert len(res2["history"]) == 0 # Cold start

    cbf = ContentBasedFilterTool()
    assert len(cbf._run("action")["recommended"]) == 2

    cf = CollaborativeFilterTool()
    res3 = cf._run("old_user")
    assert "item_3" in res3["recommended"]
    res4 = cf._run("new_user")
    assert "error" in res4 # CF fails on cold start

    ta = TrendAnalyzerTool()
    assert len(ta._run("movies")["trending"]) > 0


def test_entertainment_agent():
    cfg = AgentConfig(name="EntTest", domain=AgentDomain.ENTERTAINMENT)
    agent = EntertainmentAgent(config=cfg)
    agent.compile()

    assert agent.health_check().status == "healthy"
    state = AgentState(messages=[])
    res = agent.run(state)
    assert res.messages == []
