from typing import Generator

from memory.message import ReasonEvent, ToolCallEvent, StopEvent, ContentEvent


class ToolCallParser:
    def __init__(self):
        self.normal_text_queue = []
        self.reasoning_queue = []
        self.id = None
        self.name = ""
        self.args = ""

    def process_stream(self, stream: Generator):
        for chunk in stream:
            print(chunk)
            if not getattr(chunk, "choices", None):
                continue
            choice = chunk.choices[0]
            delta = getattr(choice, "delta", None)
            if not delta:
                continue
            # print(delta)
            # 推理内容
            reasoning_content = getattr(delta, "reasoning_content", None)
            if reasoning_content:
                self.reasoning_queue.append(reasoning_content)
                yield ReasonEvent(content=reasoning_content).to_dict()
                continue

            # 普通文本
            content = getattr(delta, "content", None)
            if content:
                self.normal_text_queue.append(content)
                yield ContentEvent(content=content).to_dict()
                continue

            if hasattr(delta, "tool_calls") and delta.tool_calls:
                for tc in delta.tool_calls:
                    if getattr(tc, "id", None):
                        self.id = tc.id
                    func = getattr(tc, "function", None)
                    if func:
                        if getattr(func, "name", None):
                            self.name = func.name
                        if getattr(func, "arguments", None):
                            self.args += func.arguments

            if getattr(choice, "finish_reason", None) == "tool_calls":
                yield ToolCallEvent(
                    id=self.id,
                    name=self.name,
                    args=self.args
                ).to_dict()

            if getattr(choice, "finish_reason", None) == "stop":
                yield StopEvent().to_dict()

