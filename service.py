import time

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi import Request
import json

from agents.core_agent import CoreAgent
from config.global_config import GlobalConfig

app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body["messages"]
    config = GlobalConfig()
    messages = config.get_message().build_user_message(prompt)
    agent = CoreAgent(
        config,
        messages=messages
    )

    def event_stream():
        assistant_response = ""
        for event in agent.run():
            if event["type"] == "content":
                assistant_response += event["content"]
            yield (
                f"event: {event['type']}\n"
                f"data: {json.dumps(event,ensure_ascii=False)}\n\n"
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )
