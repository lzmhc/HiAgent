import time
import uuid
from typing import List, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi import Request
import json

from agents.core_agent import CoreAgent
from config.global_config import GlobalConfig
from memory.message import UserMessage
from pathlib import Path

from memory.session_manager import SessionManager

app = FastAPI()
session_manager = SessionManager(base_dir="~/.hiagent")
@app.get("/status")
async def status():
    config = GlobalConfig().get_config()
    return {
        "name": "HiAgent",
        "model": config.get_model(),
        "model_reasoning_effort": config.get_think_level(),
        "workspace": str(Path.cwd()),
    }

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    session_id = body["session_id"]
    prompt = body["messages"]
    if not session_id:
        raise HTTPException(status_code=400, detail="not found session_id")
    # 加载历史聊天记录
    history = session_manager.load_history(session_id)
    config = GlobalConfig()
    messages: List[Dict] = [UserMessage(prompt).to_dict()]
    session_manager.append_message(session_id, messages[0])
    agent = CoreAgent(
        config,
        messages=history + messages
    )
    def event_stream():
        messages_list = {}
        for event in agent.run():
            role = event["role"]
            content = event.get("content")
            if role not in messages_list.keys():
                messages_list[role] = ""
            elif content is not None:
                messages_list[role] += content
            yield (
                f"event: {event["role"]}\n"
                f"data: {json.dumps(event,ensure_ascii=False)}\n\n"
            )
        for role in messages_list.keys():
            messages_role = role
            messages_data = messages_list[role]
            if messages_role == "content":
                session_manager.append_message(session_id, {"role": "assistant", "content": messages_data})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )


@app.post("/session/new")
async def new_session():
    session_id = session_manager.create_session(None)
    return {"session_id": session_id}


@app.get("/session/{session_id}/history")
async def get_history(session_id: str, limit: int = 50):
    history = session_manager.load_history(session_id, limit)
    return {"history": history}


@app.get("/sessions")
async def list_sessions():
    """获取所有会话列表"""
    sessions = session_manager.list_sessions()
    return {"sessions": sessions}