# Repository Guidelines

## Project Structure & Module Organization

```
HiAgent/
├── service.py              # FastAPI entry point (SSE streaming)
├── start.sh                # Launch script (venv + uvicorn)
├── agents/                 # Core agent logic
│   ├── core_agent.py       # Agent loop with tool-calling
│   ├── base_llm_adapter.py # LLM API adapter
│   ├── tool_call_parser.py # Parses tool-call responses
│   └── skills.py           # Skill routing and dispatch
├── tools/                  # Tool implementations
│   ├── shell/              # Shell session management
│   ├── execute_shell/      # Single-command execution
│   ├── search/             # Web search (Bocha, Brave)
│   └── qqbot/              # QQ Bot integration
├── memory/message.py       # Message types (see below)
├── config/                 # Config (config.json, global_config.py)
├── skills/                 # Skill definitions (e.g., tmux)
└── Agent_cli/              # Rust terminal client (Ratatui TUI)
```

### Message Types (`memory/message.py`)

All classes inherit from `Message` and implement `to_dict()`. Each carries a `role` string used in the SSE event stream:

| Class | Role | Purpose |
|---|---|---|
| `SystemMessage` | `system` | System instructions to the LLM |
| `UserMessage` | `user` | End-user input |
| `AssistantMessage` | `assistant` | LLM response, may include `tool_calls` |
| `ContentMessage` | `content` | Final text reply to the client |
| `ReasonMessage` | `reason` | Intermediate reasoning steps |
| `ToolStartMessage` | `toolStart` | Tool invocation is starting |
| `ToolCallMessage` | `toolCall` | Structured tool-call (id, name, args) |
| `ToolMessage` | `tool` | Result from tool execution |
| `StopMessage` | `stop` | Agent loop finished |
| `ErrorMessage` | `error` | Processing error |

## Build, Test, and Development Commands

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn openai pyyaml requests
./start.sh                          # Server at :8000

# Frontend
cd Agent_cli && cargo run           # TUI client
cargo check                         # Type-check only
```

## Coding Style & Naming Conventions

- **Python**: 4-space indent, type hints required. `snake_case` for functions/variables, `PascalCase` for classes.
- **Rust**: `cargo fmt` (edition 2024). Standard `rustfmt` conventions.
- One responsibility per file.

## Testing Guidelines

- No test suite exists yet. Place Python tests in `tests/` as `test_<module>.py` using `pytest`.
- Rust tests: `cargo test` in `Agent_cli/`.
- Manual verification: run `./start.sh`, send a test message via the client.

## Commit & Pull Request Guidelines

- Prefix commits with a category: `feature:`, `fix:`, `refactor:`.
- PRs should describe what changed and why; link issues when applicable.

## Configuration & Security

- Never commit `config/config.json` (contains API keys). Only `config.json.example` is tracked.
- Setup: `cp config/config.json.example config/config.json`
