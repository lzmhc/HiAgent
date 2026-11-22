import datetime
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional

class Message(ABC):
    @abstractmethod
    def to_dict(self) -> Dict[str, str]:
        pass

class JsonlMessage(Message):
    def __init__(self, id: str, type: str, parentId: str, message: Dict):
        self.id = id
        self.type: str = type
        self.parentId: str = parentId
        self.timestamp = str(datetime.datetime.now())
        self.message: dict = message
    def to_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "type": self.type,
            "parentId": self.parentId,
            "timestamp": self.timestamp,
            "message": self.message,
        }

class SystemMessage(Message):
    def __init__(self, message: str):
        self.role = "system"
        self.content: str = message
        self.timestamp = time.time()
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content, "timestamp": self.timestamp}

class UserMessage(Message):
    def __init__(self, message: str):
        self.role = "user"
        self.content: str = message
        self.timestamp = time.time()
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content, "timestamp": self.timestamp}

class AssistantMessage(Message):
    def __init__(self, content: Optional[str] = None,
                 tool_calls: Optional[List[Dict]] = None):
        self.role = "assistant"
        self.content = content
        self.tool_calls = tool_calls
        self.timestamp = time.time()
    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = {"role": self.role, "timestamp": self.timestamp}
        if self.content is not None:
            d["content"] = self.content
        if self.tool_calls is not None:
            d["tool_calls"] = self.tool_calls
        return d

class ToolResultMessage(Message):
    def __init__(self, content: str, tool_call_id: str):
        self.role = "tool"
        self.content: str = content
        self.tool_call_id: str = tool_call_id
        self.timestamp = time.time()
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "tool_call_id": self.tool_call_id,
            "content": self.content,
            "timestamp": self.timestamp,
        }

@dataclass
class ContentEvent(Message):
    def __init__(self, content: str):
        self.role = "content"
        self.content: str = content
        self.timestamp = time.time()
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }

@dataclass
class ReasonEvent(Message):
    def __init__(self, content: str):
        self.role = "reason"
        self.content: str = content
        self.timestamp = time.time()
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }

@dataclass
class ToolCallEvent(Message):
    def __init__(self, id: str, name: str, args: str):
        self.role: str = "toolCall"
        self.type: str = "function"
        self.id: str = id
        self.name: str = name
        self.args: str = args
        self.timestamp = time.time()
    def to_dict(self) -> Dict[str, object]:
        return {
            "role": self.role,
            "id": self.id,
            "type": self.type,
            "function": {
                "name": self.name,
                "arguments": self.args
            },
            "timestamp": self.timestamp,
        }


@dataclass
class ToolResultEvent(Message):
    def __init__(self, id: str, name: str, content: str):
        self.role: str = "toolResult"
        self.id: str = id
        self.name: str = name
        self.content: str = content
        self.timestamp = time.time()
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "timestamp": self.timestamp,
        }

@dataclass
class StopEvent(Message):
    def __init__(self):
        self.role = "stop"
        self.timestamp = time.time()
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "timestamp": self.timestamp}

@dataclass
class ErrorEvent(Message):
    def __init__(self, content: str):
        self.role = "error"
        self.content: str = content
        self.timestamp = time.time()
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }

@dataclass
class TokenEvent(Message):
    def __init__(self, completion_tokens: int, prompt_tokens: int, total_tokens: int):
        self.role = "token"
        self.completion_tokens: int = completion_tokens
        self.prompt_tokens: int = prompt_tokens
        self.total_tokens: int = total_tokens
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "completion_tokens": self.completion_tokens,
            "prompt_tokens": self.prompt_tokens,
            "total_tokens": self.total_tokens,
        }