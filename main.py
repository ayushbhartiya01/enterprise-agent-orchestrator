import argparse
import asyncio
from src.agent.loop import ReActAgent
from src.tools.action_tools import create_support_ticket, search_enterprise_knowledge
from src.tools.registry import ToolRegistry
from src.tools.schemas import CreateSupportTicketInput, SearchKnowledgeInput


async def run(query: str) -> None:
    registry = ToolRegistry()
    registry.register(
        name="search_enterprise_knowledge",
        description="Search internal enterprise policy documents for specific facts or rules.",
        input_schema=SearchKnowledgeInput,
        handler=search_enterprise_knowledge,
    )
    registry.register(
        name="create_support_ticket",
        description="Create an internal IT or security support ticket.",
        input_schema=CreateSupportTicketInput,
        handler=create_support_ticket,
    )

    agent = ReActAgent(registry=registry)

    answer = await agent.run(query)
    print(f"\nFinal Response:\n{answer}")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run the enterprise operations agent.")
    parser.add_argument("query", nargs="?", help="Question or operation for the agent.")
    parsed = parser.parse_args()
    query = parsed.query or (
        "Check our employee data retention policy, and if there is a rule about "
        "security incidents involving data exposure, create an appropriate support ticket "
        "for an exposed laptop reported by user u-409."
    )
    await run(query)


if __name__ == "__main__":
    asyncio.run(main())
