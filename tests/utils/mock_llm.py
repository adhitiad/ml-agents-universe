"""Mock LLM untuk unit test deterministik."""

class MockLLM:
    """Mensimulasikan response dari LLM (seperti LangChain ChatOpenAI)."""

    def __init__(self, responses: dict = None):
        self.responses = responses or {}
        self.call_history = []

    def invoke(self, prompt: str) -> str:
        self.call_history.append(prompt)
        # Cari response yang cocok secara parsial
        for key, res in self.responses.items():
            if key.lower() in prompt.lower():
                return res
        return "MOCK_RESPONSE: Default generated text."

    async def ainvoke(self, prompt: str) -> str:
        return self.invoke(prompt)

class MockEnvironment:
    """Mensimulasikan Environment eksternal."""

    def __init__(self, state: dict = None):
        self.state = state or {"status": "initialized"}

    def step(self, action: str) -> dict:
        self.state["last_action"] = action
        return {"observation": f"Executed: {action}", "reward": 1.0}
