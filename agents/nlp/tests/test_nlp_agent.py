from agents.nlp.src.agent.nlp_agent import NLPAgent
from agents.nlp.src.env.nlp_env import ConversationEnvironment, DocumentEnvironment
from agents.nlp.src.models.nlp_models import (
    ConversationModel,
    EmbeddingModel,
    SummarizationModel,
    TextClassificationModel,
)
from agents.nlp.src.tools.nlp_tools import (
    EntityExtractorTool,
    SentimentAnalyzerTool,
    TextCleanerTool,
    TokenizerTool,
    WebScraperTool,
)
from shared.models import AgentConfig, AgentDomain, AgentState


def test_nlp_models():
    conv = ConversationModel(session_id="s1", user_id="u1", language="en")
    assert conv.language == "en"

    cls = TextClassificationModel(text="good", label="positive", confidence=0.99)
    assert cls.label == "positive"

    summ = SummarizationModel(
        original_text="a b c d",
        summary="a d",
        method="extractive",
        compression_ratio=0.5,
    )
    assert summ.compression_ratio == 0.5

    emb = EmbeddingModel(text="test", vector=[0.1, 0.2], model_name="test-model")
    assert emb.model_name == "test-model"


def test_nlp_env():
    env = ConversationEnvironment()
    res = env.step("s1", "Hello")
    assert res["reward"] == 1.0
    assert not res["done"]

    # 5 steps to done
    for _ in range(4):
        res = env.step("s1", "Next")
    assert res["done"]

    doc_env = DocumentEnvironment({"d1": "content"})
    assert doc_env.fetch_document("d1") == "content"
    assert doc_env.fetch_document("unknown") == "Document Not Found."


def test_nlp_tools():
    # Tokenizer
    tok = TokenizerTool()
    assert tok._run("Halo Dunia!").get("token_count") == 2

    # TextCleaner
    clean = TextCleanerTool()
    assert clean._run("<p> Halo   Dunia </p>") == "Halo Dunia"

    # Sentiment
    sent = SentimentAnalyzerTool()
    assert sent._run("Ini sangat bagus").get("sentiment") == "positive"
    assert sent._run("Ini sangat jelek").get("sentiment") == "negative"
    assert sent._run("Biasa saja").get("sentiment") == "neutral"

    # Entity
    ent = EntityExtractorTool()
    assert "Jakarta" in ent._run("Pergi ke Jakarta").get("entities_found", [])

    # WebScraper (mock)
    scrap = WebScraperTool()
    assert isinstance(scrap._run("http://invalid.url.local"), str)


def test_nlp_agent():
    cfg = AgentConfig(name="NLPAgentTest", domain=AgentDomain.NLP)
    agent = NLPAgent(config=cfg)
    agent.compile()

    hc = agent.health_check()
    assert hc.status == "healthy"

    state = AgentState(messages=[])
    res = agent.run(state)
    assert "messages" in res.model_dump()
