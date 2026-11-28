from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Union

from pygments.lexer import default


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

class TextOutput(Input):
    def __init__(self, text: str):
        self.type = "output_text"
        self.text = text
    def to_dict(self) -> Dict[str, str]:
        return {"type": self.type, "text": self.text}

class FunctionCall(Input):
    def __init__(self, call_id: str, name: str, arguments: str):
        self.type = "function_call"
        self.call_id = call_id
        self.name = name
        self.arguments = arguments
    def to_dict(self) -> Dict[str, str]:
        return {"type": self.type, "call_id": self.call_id, "name": self.name, "arguments": self.arguments}

class FunctionCallOutput(Input):
    def __init__(self, call_id: str, output: str):
        self.type = "function_call_output"
        self.call_id = call_id
        self.output = output
    def to_dict(self) -> Dict[str, str]:
        return {"type": self.type, "call_id": self.call_id, "output": self.output}

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

# openai message
class SystemMessage(Message):
    def __init__(self, input: List[Dict]):
        self.role = "system"
        self.content = input
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }

class UserMessage(Message):
    def __init__(self, input: List[Dict]):
        self.role = "user"
        self.content = input
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }

class AssistantMessage(Message):
    def __init__(self, content: Union[str, List[Dict], None], tool_call_id: str = None):
        self.role = "assistant"
        self.content = content
        self.tool_call_id = tool_call_id
    def to_dict(self) -> Dict[str, object]:
        if self.tool_call_id is not None:
            return {
                "role": self.role,
                "content": self.content,
                "tool_call_id": self.tool_call_id
            }
        else:
            return {
                "role": self.role,
                "content": self.content
            }

# rust_tui event
class Event(ABC):
    @abstractmethod
    def to_dict(self) -> Dict[str, str]:
        pass

class UserEvent(Event):
    def __init__(self, text: str):
        self.role = "user"
        self.content = text
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }

@dataclass
class ContentDeltaEvent(Event):
    def __init__(self, text: str):
        self.role = "content_delta"
        self.content = text
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }

@dataclass
class ContentEvent(Event):
    def __init__(self, text: str):
        self.role = "content"
        self.content = text
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }

class ToolResultEvent(Event):
    def __init__(self, call_id: str, content: str):
        self.role = "tool_result"
        self.content = content
        self.call_id = call_id
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
            "call_id": self.call_id
        }

@dataclass
class ToolCallEvent(Event):
    def __init__(self, call_id: str, name: str, args: str):
        self.role: str = "tool_call"
        self.call_id: str = call_id
        self.name: str = name
        self.args: str = args
    def to_dict(self) -> Dict[str, object]:
        return {
            "role": self.role,
            "call_id": self.call_id,
            "name": self.name,
            "args": self.args
        }

@dataclass
class StopEvent(Event):
    def __init__(self):
        self.role = "stop"
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role}

@dataclass
class ErrorEvent(Event):
    def __init__(self, content: str):
        self.role = "error"
        self.content = content
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }

@dataclass
class TokenEvent(Event):
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