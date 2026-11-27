import asyncio
from src.tools.schemas import (
    CreateSupportTicketInput,
    SearchKnowledgeInput,
    ToolExecutionResult,
)

# Simulated database to enforce idempotency across retries
_CREATED_TICKETS: dict[str, dict] = {}


async def search_enterprise_knowledge(args: SearchKnowledgeInput) -> ToolExecutionResult:
    """Temporary stub—will be replaced by your live enterprise-llama-rag MCP tool in Step 4."""
    await asyncio.sleep(0.2)  # Simulate network latency
    query_lower = args.query.lower()

    if "retention" in query_lower or "data" in query_lower:
        return ToolExecutionResult(
            success=True,
            data=(
                "[Policy Doc - Sec 4.2]: Employee data must be retained for 7 years "
                "after offboarding in encrypted cold storage. Critical security incidents "
                "involving data exposure require a 'critical' priority IT ticket within 2 hours."
            ),
        )

    return ToolExecutionResult(
        success=True,
        data="No matching policy documents found above grounding threshold (0.4).",
    )


async def create_support_ticket(args: CreateSupportTicketInput) -> ToolExecutionResult:
    """Simulates calling an internal ticketing API (e.g., Jira/ServiceNow) with idempotency."""
    await asyncio.sleep(0.2)

    if args.idempotency_key in _CREATED_TICKETS:
        existing = _CREATED_TICKETS[args.idempotency_key]
        return ToolExecutionResult(
            success=True,
            data={"status": "already_exists_idempotent_hit", "ticket": existing},
        )

    ticket = {
        "ticket_id": f"INC-{len(_CREATED_TICKETS) + 1001}",
        "title": args.title,
        "priority": args.priority,
        "description": args.description,
    }
    _CREATED_TICKETS[args.idempotency_key] = ticket

    return ToolExecutionResult(
        success=True,
        data={"status": "created", "ticket": ticket},
    )
