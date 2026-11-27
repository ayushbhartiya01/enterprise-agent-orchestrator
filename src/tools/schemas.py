from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SearchKnowledgeInput(StrictModel):
    query: str = Field(
        ...,
        min_length=5,
        description="A specific, focused question to search in enterprise documents. Do not pass broad summary requests."
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of top relevant passages to return."
    )


class CreateSupportTicketInput(StrictModel):
    title: str = Field(..., min_length=5, max_length=100, description="Short summary of the issue.")
    priority: Literal["low", "medium", "high", "critical"] = Field(
        default="medium",
        description="Urgency level based on business impact."
    )
    description: str = Field(..., description="Detailed context including findings from enterprise docs.")
    idempotency_key: str = Field(
        ...,
        description="Unique deterministic key (e.g. 'ticket-user123-vpn-issue') to prevent duplicate ticket creation on retries."
    )


class ToolExecutionResult(BaseModel):
    success: bool
    data: dict | str | None = None
    error: str | None = None
