import platform
import time
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi import Request
import json
from agents.core_agent import CoreAgent
from config.global_config import GlobalConfig
from memory.message import UserMessage, AssistantMessage, SystemMessage, TextInput, TextOutput, StopEvent, ToolMessage
from memory.session_manager import SessionManager
from tools.mcp.mcp_manage import McpManage

app = FastAPI()
config = GlobalConfig()
session_manager = SessionManager()
mcp_manage = McpManage()
@app.get("/status")
async def status():
    return {
        "name": platform.system(),
        "model": config.get_config().get_model(),
        "model_reasoning_effort": config.get_config().get_think_level()
    }

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    session_id = body["session_id"]
    prompt = body["messages"]
    if not session_id:
        raise HTTPException(status_code=400, detail="not found session_id")
    history = session_manager.load_history(session_id)
    latest_message = UserMessage([TextInput(prompt).to_dict()]).to_dict()
    current_id = str(time.time())
    if len(history) > 0:
        parent_id = history[-1].get("id")
    else:
        parent_id = None
    session_manager.append_jsonl_message(session_id, current_id, "message", parent_id, latest_message)
    messages: List[Dict] = []
    for message in history:
        messages.append(message.get("message"))
    messages.append(latest_message)
    agent = CoreAgent(
        config
    )
    def event_stream(current_id, messages):
        parent_id = current_id
        contents = ""
        for event in agent.run(messages):
            if type(event) == AssistantMessage:
                if isinstance(event.content, str):
                    contents += event.content
            elif type(event) in (SystemMessage, UserMessage, ToolMessage):
                current_id = str(time.time())
                session_manager.append_jsonl_message(session_id, current_id, "message", parent_id, event.to_dict())
                parent_id = current_id
            elif type(event) == StopEvent:
                if contents !="":
                    current_id = str(time.time())
                    session_manager.append_jsonl_message(session_id, current_id, "message", parent_id, AssistantMessage([TextOutput(contents).to_dict()]).to_dict())
                    parent_id = current_id
                    contents = ""
            yield (
                f"data: {json.dumps(event.to_dict())}\n\n"
            )
    return StreamingResponse(
        event_stream(current_id, messages),
        media_type="text/event-stream"
    )


@app.post("/session/new")
async def new_session():
    session_id = session_manager.create_session(None)
    return {"session_id": session_id}

@app.get("/session/{session_id}/history")
async def get_history(session_id: str, limit: int = 50):
    history = []
    for message in session_manager.load_history(session_id, limit):
        history.append(message.get("message"))
    return {"history": history}

@app.get("/sessions")
async def list_sessions():
    sessions = session_manager.list_sessions()
    return {"sessions": sessions}
