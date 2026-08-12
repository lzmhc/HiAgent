import datetime
from typing import List, Dict

class Message:
    def __init__(self, message: str):
        self.role = None
        self.content: str = message
        self.timestamp: datetime.datetime = datetime.datetime.now()
    def to_dict(self) -> Dict:
        return {}
# 系统消息
class SystemMessage(Message):
    def __init__(self, message: str):
        super().__init__(message)
        self.role = "system"

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

# 用户消息
class UserMessage(Message):
    def __init__(self, message: str):
        super().__init__(message)
        self.role = "user"

    def to_dict(self) -> Dict[str, object]:
        return {
            "role":self.role,
            "content":self.content,
            "timestamp":self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
#
class AssistantMessage(Message):
    def __init__(self, message: str, tool_calls: List[Dict[str, object]]):
        super().__init__(message)
        self.role = "assistant"
        self.tool_calls = tool_calls

    def to_dict(self) -> Dict[str, object]:
        return {
            "role":self.role,
            "content":self.content,
            "tool_calls":self.tool_calls,
            "timestamp":self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
# 回复消息
class ContentMessage(Message):
    def __init__(self, message: str):
        super().__init__(message)
        self.role = "content"

    def to_dict(self) -> Dict:
        return {
            "role":self.role,
            "content":self.content,
            "timestamp":self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
# 推理消息
class ReasonMessage(Message):
    def __init__(self, message: str):
        super().__init__(message)
        self.role = "reason"

    def to_dict(self) -> Dict[str, object]:
        return {
            "role":self.role,
            "content":self.content,
            "timestamp":self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

# 开始调用工具消息
class ToolStartMessage(Message):
    def __init__(self, tool_name: str, tool_args: str):
        self.role = "toolStart"
        self.content = None
        self.tool_name = tool_name
        self.tool_args = tool_args

    def to_dict(self) -> Dict[str, object]:
        return {
            "role":self.role,
            "tool_name":self.tool_name,
            "tool_args":self.tool_args
        }
# 工具调用
class ToolCallMessage(Message):
    def __init__(self, id: str, type: str, name: str, arguments: str):
        self.role = "toolCall"
        self.id = id
        self.type = type
        self.function = {
            "name": name,
            "arguments": arguments
        }
    def to_dict(self) -> Dict[str, object]:
        return {
            "role":self.role,
            "id":self.id,
            "type":self.type,
            "function":self.function
        }
# 工具调用结果
class ToolMessage(Message):
    def __init__(self, message: str, tool_call_id: str):
        super().__init__(message)
        self.role = "tool"
        self.tool_call_id = tool_call_id
    def to_dict(self) -> Dict[str, object]:
        return {
            "role":self.role,
            "tool_call_id":self.tool_call_id,
            "content":self.content,
        }
# 停止
class StopMessage(Message):
    def __init__(self):
        self.role = "stop"
    def to_dict(self) -> Dict[str, object]:
        return {
            "role":self.role,
        }
# 错误消息
class ErrorMessage(Message):
    def __init__(self, message: str):
        super().__init__(message)
        self.role = "error"

    def to_dict(self) -> Dict[str, object]:
        return {
            "role":self.role,
            "content": self.content,
            "timestamp":self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }

