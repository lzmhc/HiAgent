import datetime
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from symtable import Class
from typing import List, Dict, Optional

class Input(ABC):
    @abstractmethod
    def to_dict(self) -> Dict[str, str]:
        pass

class TextInput(Input):
    def __init__(self, text: str):
        self.type = "input_text"
        self.text = text
    def to_dict(self) -> Dict[str, str]:
        return {"type": self.type, "text": self.text}

class TextOutput(Input):
    def __init__(self, text: str):
        self.type = "output_text"
        self.text = text
    def to_dict(self) -> Dict[str, str]:
        return {"type": self.type, "text": self.text}

class ImageInput(Input):
    def __init__(self, url: str):
        self.type = "input_image"
        self.image_url = url
    def to_dict(self) -> Dict[str, str]:
        return {"type": self.type, "image_url": self.image_url}

class AudioInput(Input):
    def __init__(self, url: str):
        self.type = "input_audio"
        self.audio_url = url
    def to_dict(self) -> Dict[str, str]:
        return {"type": self.type, "audio_url": self.audio_url}

class FileInput(Input):
    def __init__(self, url: str):
        self.type = "input_file"
        self.file_url = url
    def to_dict(self) -> Dict[str, str]:
        return {"type": self.type, "file_url": self.file_url}

class Message(ABC):
    def to_dict(self) -> Dict[str, str]:
        pass

class JsonlMessage(Message):
    def __init__(self, id: str, type: str, parentId: str, message: Dict):
        self.id = id
        self.type: str = type
        self.parentId: str = parentId
        self.message: dict = message
    def to_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "type": self.type,
            "parentId": self.parentId,
            "message": self.message,
        }

class SystemMessage(Message):
    def __init__(self, input: List[Dict]):
        self.role = "system"
        self.content = input
        self.timestamp = time.time()
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
        }

class UserMessage(Message):
    def __init__(self, input: List[Dict]):
        self.role = "user"
        self.content = input
        self.timestamp = time.time()
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }

class AssistantMessage(Message):
    def __init__(self, content: List[Dict]):
        self.role = "assistant"
        self.content = content
    def to_dict(self) -> Dict[str, object]:
        return {
            "role": self.role,
            "content": self.content
        }

class ToolResultMessage(Message):
    def __init__(self, content: List[Dict], tool_call_id: str):
        self.role = "tool_result"
        self.content = content
        self.tool_call_id = tool_call_id
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "tool_call_id": self.tool_call_id,
            "content": self.content
        }

@dataclass
class ContentEvent(Message):
    def __init__(self, text: str):
        self.role = "content"
        self.content = text
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }

@dataclass
class ReasonEvent(Message):
    def __init__(self, input: List[Dict]):
        self.role = "reason"
        self.content = input
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }

@dataclass
class ToolCallEvent(Message):
    def __init__(self, id: str, name: str, args: str):
        self.role: str = "toolCall"
        self.type: str = "function"
        self.id: str = id
        self.name: str = name
        self.args: str = args
    def to_dict(self) -> Dict[str, object]:
        return {
            "role": self.role,
            "id": self.id,
            "type": self.type,
            "function": {
                "name": self.name,
                "arguments": self.args
            }
        }


@dataclass
class ToolResultEvent(Message):
    def __init__(self, id: str, name: str, content: str):
        self.role: str = "toolResult"
        self.id: str = id
        self.name: str = name
        self.content = content
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "id": self.id,
            "name": self.name,
            "content": self.content
        }

@dataclass
class StopEvent(Message):
    def __init__(self):
        self.role = "stop"
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role}

@dataclass
class ErrorEvent(Message):
    def __init__(self, content: str):
        self.role = "error"
        self.content = content
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
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