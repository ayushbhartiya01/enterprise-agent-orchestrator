import json

import pytest

from src.tools.registry import ToolRegistry
from src.tools.schemas import SearchKnowledgeInput, ToolExecutionResult


async def _search(args: SearchKnowledgeInput) -> ToolExecutionResult:
    return ToolExecutionResult(success=True, data={"query": args.query})


@pytest.mark.asyncio
async def test_registry_executes_valid_arguments():
    registry = ToolRegistry()
    registry.register("search", "Search docs", SearchKnowledgeInput, _search)

    result = await registry.execute_tool(
        "search",
        '{"query": "retention policy", "top_k": 3}',
    )

    assert '"success":true' in result
    assert '"query":"retention policy"' in result


@pytest.mark.asyncio
async def test_registry_rejects_extra_and_malformed_arguments():
    registry = ToolRegistry()
    registry.register("search", "Search docs", SearchKnowledgeInput, _search)

    extra = await registry.execute_tool("search", '{"query": "policy", "unknown": true}')
    malformed = await registry.execute_tool("search", "{")

    assert json.loads(extra)["success"] is False
    assert "extra" in extra.lower()
    assert json.loads(malformed)["success"] is False
    assert "invalid json" in malformed.lower()


def test_registry_rejects_duplicate_names():
    registry = ToolRegistry()
    registry.register("search", "Search docs", SearchKnowledgeInput, _search)

    with pytest.raises(ValueError, match="already registered"):
        registry.register("search", "Duplicate", SearchKnowledgeInput, _search)
