import pytest

from src.tools.action_tools import create_support_ticket
from src.tools.action_tools import _CREATED_TICKETS
from src.tools.schemas import CreateSupportTicketInput


@pytest.fixture(autouse=True)
def clear_created_tickets():
    _CREATED_TICKETS.clear()
    yield
    _CREATED_TICKETS.clear()


@pytest.mark.asyncio
async def test_ticket_creation_is_idempotent():
    args = CreateSupportTicketInput(
        title="Exposed laptop incident",
        priority="critical",
        description="Laptop u-409 exposed employee data.",
        idempotency_key="ticket-u-409-exposed-laptop",
    )

    first = await create_support_ticket(args)
    second = await create_support_ticket(args)

    assert first.success is True
    assert first.data["status"] == "created"
    assert second.success is True
    assert second.data["status"] == "already_exists_idempotent_hit"
    assert first.data["ticket"] == second.data["ticket"]
