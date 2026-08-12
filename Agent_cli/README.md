# Agent_cli

Terminal chat client for an SSE agent backend, built with `ratatui` + `crossterm`.

## Run

1. Start the backend (default `http://127.0.0.1:8000/chat`).
2. In this project directory:
   - `cargo run`

## Configuration

- `CHAT_API_URL` — override backend endpoint at runtime (example: `CHAT_API_URL=http://host:8000/chat cargo run`).

## Controls

- `Enter` — send current input
- `Up/Down` — scroll chat
- `Esc` — clear input
- `Ctrl+Q` — quit

## Project layout

- `src/main.rs` — terminal bootstrap and main event loop
- `src/app.rs` — chat state and event handling
- `src/ui.rs` — TUI layout rendering
- `src/api.rs` — SSE client to backend
- `src/agent_event.rs` — shared event types

## Notes

- Runtime tool event types (`tool_start`, `tool_result`) are supported if the backend emits them.
- On panic, the terminal state is restored before printing the error.
