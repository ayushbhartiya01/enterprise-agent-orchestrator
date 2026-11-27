import json
from dataclasses import dataclass
from typing import Any, Awaitable, Callable
from pydantic import BaseModel, ValidationError
from src.tools.schemas import ToolExecutionResult


@dataclass
class RegisteredTool:
    name: str
    description: str
    input_schema: type[BaseModel]
    handler: Callable[[Any], Awaitable[ToolExecutionResult]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(
        self,
        name: str,
        description: str,
        input_schema: type[BaseModel],
        handler: Callable[[Any], Awaitable[ToolExecutionResult]],
    ) -> None:
        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered.")
        self._tools[name] = RegisteredTool(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler,
        )

    def get_openai_tools(self) -> list[dict[str, Any]]:
        """Generates strict OpenAI/Groq-compatible tool definitions from Pydantic schemas."""
        tools_payload = []
        for tool in self._tools.values():
            schema = tool.input_schema.model_json_schema()
            schema.pop("title", None)
            tools_payload.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": schema,
                    },
                }
            )
        return tools_payload

    async def execute_tool(self, name: str, raw_arguments: str) -> str:
        """Parses JSON, validates against Pydantic, executes, and returns serialized string."""
        if name not in self._tools:
            return json.dumps(
                {"success": False, "error": f"Unknown tool '{name}'. Available: {list(self._tools.keys())}"}
            )

        tool = self._tools[name]

        # 1. Validate JSON syntax
        try:
            parsed_json = json.loads(raw_arguments or "{}")
        except json.JSONDecodeError as e:
            return json.dumps(
                {"success": False, "error": f"Invalid JSON arguments: {e}. Fix syntax and retry."}
            )

        # 2. Validate against strict Pydantic contract (Self-correction feedback)
        try:
            validated_args = tool.input_schema.model_validate(parsed_json)
        except ValidationError as e:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Schema validation failed: {e.errors()}. Correct the fields and retry.",
                }
            )

        # 3. Execute tool safely
        try:
            result = await tool.handler(validated_args)
            return result.model_dump_json()
        except Exception as e:
            return json.dumps({"success": False, "error": f"Tool execution error: {str(e)}"})
