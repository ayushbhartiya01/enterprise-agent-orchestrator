# Enterprise Agent Orchestrator

A small ReAct-style enterprise operations agent built with Python and Pydantic. It connects an OpenAI-compatible chat model to validated tools for grounded knowledge lookup and support-ticket creation.

## Features

- OpenAI-compatible LLM provider support, with Groq defaults
- Pydantic-validated tool arguments and strict JSON schemas
- Concurrent tool execution
- Idempotent support-ticket creation
- Configurable agent step limit
- Async Python implementation

## Setup

Requirements: Python 3.12+ and `uv`.

```bash
cp .env.example .env
uv sync
```

Set `LLM_API_KEY` and, if needed, the provider/model values in `.env`.

```bash
uv run python main.py
```

Pass a custom request as positional text:

```bash
uv run python main.py "What is our employee data retention policy?"
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `LLM_API_KEY` | Required | API credential for the OpenAI-compatible provider |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | Provider base URL |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Chat/completion model |
| `MAX_AGENT_STEPS` | `6` | Maximum reasoning/tool iterations |

## Tests

```bash
uv run pytest
```

## Project Structure

- `main.py`: Example application entry point
- `src/agent/loop.py`: ReAct agent loop
- `src/config.py`: Environment configuration
- `src/tools/registry.py`: Tool registration and execution
- `src/tools/schemas.py`: Pydantic tool contracts
- `src/tools/action_tools.py`: Knowledge and ticketing implementations