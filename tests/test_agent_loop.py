from types import SimpleNamespace

import pytest

import src.agent.loop as loop_module
from src.agent.loop import ReActAgent
from src.tools.registry import ToolRegistry


class FakeCompletions:
    def __init__(self, responses):
        self.responses = iter(responses)

    async def create(self, **kwargs):
        return next(self.responses)


class FakeClient:
    def __init__(self, responses):
        self.chat = SimpleNamespace(completions=FakeCompletions(responses))


class FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls

    def model_dump(self, exclude_none=True):
        payload = {"role": "assistant", "content": self.content}
        if self.tool_calls:
            payload["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in self.tool_calls
            ]
        return {key: value for key, value in payload.items() if value is not None}


def response(message):
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


@pytest.mark.asyncio
async def test_agent_returns_direct_answer(monkeypatch):
    monkeypatch.setattr(
        loop_module,
        "AsyncOpenAI",
        lambda **kwargs: FakeClient([response(FakeMessage(content="No relevant policy found."))]),
    )

    agent = ReActAgent(ToolRegistry())

    answer = await agent.run("What is the data retention policy?")

    assert answer == "No relevant policy found."


@pytest.mark.asyncio
async def test_agent_handles_provider_failure(monkeypatch):
    class FailingClient:
        def __init__(self, **kwargs):
            async def create(**_kwargs):
                raise RuntimeError("provider unavailable")

            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=create),
            )

    monkeypatch.setattr(loop_module, "AsyncOpenAI", FailingClient)

    agent = ReActAgent(ToolRegistry())
    answer = await agent.run("Search the retention policy.")

    assert "RuntimeError" in answer
    assert "provider unavailable" in answer
