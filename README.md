# HiAgent

An LLM-based agent system with tool calling, skill routing, and streaming responses.

## Quick Start

### 1. Install Dependencies

```bash
cd HiAgent
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn openai pyyaml requests
```

### 2. Configuration

Copy the example config and fill in your API keys:

```bash
cp config/config.json.example config/config.json
```

### 3. Start Service

```bash
chmod +x start.sh
./start.sh
```

The service will start at `http://127.0.0.1:8000`.

### 4. Terminal Client

```bash
cd Agent_cli
cargo run
```

Press `Enter` to send messages, `Ctrl+Q` to exit.

## Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: Rust, Ratatui
