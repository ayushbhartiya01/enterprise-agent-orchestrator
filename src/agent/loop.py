import asyncio
from openai import AsyncOpenAI
from src.config import settings
from src.tools.registry import ToolRegistry

SYSTEM_PROMPT = """You are an enterprise operations agent.
Your job is to answer employee questions accurately using internal policy documents and take authorized actions when requested.

Rules:
1. Always search enterprise knowledge before answering policy questions or creating compliance tickets.
2. Never guess company policies. If the knowledge base returns no relevant info, state that clearly.
3. If a tool returns a validation error, read the error message, fix your arguments, and retry.
4. Be concise and cite policy sections when available.
"""


class ReActAgent:
    def __init__(self, registry: ToolRegistry) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
        self.registry = registry
        self.model = settings.llm_model
        self.max_steps = settings.max_agent_steps

    async def run(self, user_query: str) -> str:
        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ]
        tools = self.registry.get_openai_tools()

        for step in range(1, self.max_steps + 1):
            print(f"\n--- [Step {step}/{self.max_steps}] Thinking ---")

            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools if tools else None,
                    tool_choice="auto",
                    temperature=0.0,
                )
            except Exception as exc:
                return f"Agent request failed: {type(exc).__name__}: {exc}"

            if not response.choices:
                return "Agent request failed: The model returned no completion choices."
            assistant_msg = response.choices[0].message
            messages.append(assistant_msg.model_dump(exclude_none=True))

            # If the LLM did not call any tools, it has reached its final answer
            if not assistant_msg.tool_calls:
                print("--- [Done] Final Answer Reached ---")
                return assistant_msg.content or ""

            # Execute all requested tool calls concurrently
            async def _run_single_call(tool_call):
                fn_name = tool_call.function.name
                fn_args = tool_call.function.arguments
                print(f"  -> Calling Tool: {fn_name}({fn_args})")
                output = await self.registry.execute_tool(fn_name, fn_args)
                print(f"  <- Tool Output:  {output}")
                return {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": output,
                }

            tool_results = await asyncio.gather(
                *[_run_single_call(tc) for tc in assistant_msg.tool_calls]
            )
            messages.extend(tool_results)

        return "Agent stopped: Maximum reasoning steps reached without a final answer."
