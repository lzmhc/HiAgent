import json
import re
from typing import Generator

from memory.message import ReasonEvent, ToolCallEvent, StopEvent, ContentEvent


class ToolCallParser:
    def __init__(self):
        self.normal_text_queue = []
        self.reasoning_queue = []
        self.tool_call_id = None
        self.tool_name = ""
        self.tool_args = ""

        self.xml_mode = False
        self.xml_buffer = ""

    def process_stream(self, stream: Generator):
        for chunk in stream:
            if not getattr(chunk, "choices", None):
                continue
            print(chunk.choices[0])
            choice = chunk.choices[0]
            delta = getattr(choice, "delta", None)
            if not delta:
                continue

            # 推理内容
            reasoning_content = getattr(delta, "reasoning_content", None)
            if reasoning_content:
                self.reasoning_queue.append(reasoning_content)
                yield ReasonEvent(content=reasoning_content).to_dict()
                continue

            # 普通文本
            content = getattr(delta, "content", None)
            if content:
                if self.xml_mode:
                    self.xml_buffer += content
                    if "</tool_call>" in self.xml_buffer:
                        self.need_call_tool = True
                        self.xml_mode = False
                    continue

                if "<tool_call>" in content:
                    self.xml_mode = True
                    self.xml_buffer += content
                    continue

                self.normal_text_queue.append(content)
                yield ContentEvent(content=content).to_dict()
                continue

            if hasattr(delta, "tool_calls") and delta.tool_calls:
                for tc in delta.tool_calls:
                    if getattr(tc, "id", None):
                        self.tool_call_id = tc.id
                    func = getattr(tc, "function", None)
                    if func:
                        if getattr(func, "name", None):
                            self.tool_name = func.name
                        if getattr(func, "arguments", None):
                            self.tool_args += func.arguments

            if getattr(choice, "finish_reason", None) == "tool_calls":
                yield ToolCallEvent(
                    tool_call_id=self.tool_call_id,
                    tool_name=self.tool_name,
                    tool_args=self.tool_args,
                ).to_dict()

            if getattr(choice, "finish_reason", None) == "stop":
                yield StopEvent().to_dict()
