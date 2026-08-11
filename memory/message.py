from typing import Optional, List

class Message:
    def __init__(self):
        pass

    def build_user_message(self, message: List[dict]):
        return [{
            "role":"user",
            "content":[{"type":"text","text":message}],
        }]

class PiMessage(Message):
    def __init__(self):
        super().__init__()
        self.role: Optional[str] = None  # user / assistant
        self.content: List[dict] = []
        self.api: Optional[str] = None
        self.provider: Optional[str] = None
        self.model: Optional[str] = None
        self.usage: Optional[dict] = None
        self.stopReason: Optional[str] = None
        self.timestamp: Optional[int] = None
        self.responseId: Optional[str] = None

class CodexMessage(Message):
    def __init__(self):
        super().__init__()
        self.role: Optional[str] = None  # user / assistant
        self.content: List[dict] = []
        self.api: Optional[str] = None
        self.provider: Optional[str] = None
        self.model: Optional[str] = None
        self.usage: Optional[dict] = None
        self.stopReason: Optional[str] = None
        self.timestamp: Optional[int] = None
        self.responseId: Optional[str] = None