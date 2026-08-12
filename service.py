import time
from typing import List, Dict

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi import Request
import json

from agents.core_agent import CoreAgent
from config.global_config import GlobalConfig
from memory.message import UserMessage

app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body["messages"]
    config = GlobalConfig()
    messages: List[Dict] = [UserMessage(prompt).to_dict()]
    agent = CoreAgent(
        config,
        messages=messages
    )

    def event_stream():
        for event in agent.run():
            yield (
                f"event: {event['role']}\n"
                f"data: {json.dumps(event,ensure_ascii=False)}\n\n"
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )
