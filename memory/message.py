from dataclasses import dataclass, field
from typing import List, Dict, Optional

class SystemMessage:

    def __init__(self, message: str):
        self.role = "system"
        self.content: str = message

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class UserMessage:

    def __init__(self, message: str):
        self.role = "user"
        self.content: str = message

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class AssistantMessage:

    def __init__(self, content: Optional[str] = None,
                 tool_calls: Optional[List[Dict]] = None):
        self.role = "assistant"
        self.content = content
        self.tool_calls = tool_calls

    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = {"role": self.role}
        if self.content is not None:
            d["content"] = self.content
        if self.tool_calls is not None:
            d["tool_calls"] = self.tool_calls
        return d


class ToolResultMessage:

    def __init__(self, content: str, tool_call_id: str):
        self.role = "tool"
        self.content: str = content
        self.tool_call_id: str = tool_call_id

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "tool_call_id": self.tool_call_id,
            "content": self.content,
        }

@dataclass
class ContentEvent:
    content: str
    role: str = field(default="content", init=False)

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
        }


@dataclass
class ReasonEvent:
    content: str
    role: str = field(default="reason", init=False)

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
        }


@dataclass
class ToolCallEvent:
    tool_call_id: str
    tool_name: str
    tool_args: str
    type: str = "function"
    role: str = field(default="toolCall", init=False)

    def to_dict(self) -> Dict[str, object]:
        return {
            "role": self.role,
            "id": self.tool_call_id,
            "type": self.type,
            "function": {
                "name": self.tool_name,
                "arguments": self.tool_args,
            },
        }


@dataclass
class ToolResultEvent:
    tool_name: str
    content: str
    role: str = field(default="toolResult", init=False)

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "tool_name": self.tool_name,
            "content": self.content,
        }


@dataclass
class StopEvent:
    role: str = field(default="stop", init=False)

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role}


@dataclass
class ErrorEvent:
    content: str
    role: str = field(default="error", init=False)

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
        }
