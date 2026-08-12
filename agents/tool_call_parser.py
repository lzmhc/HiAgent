import json
import re
from typing import Generator

from memory.message import ReasonMessage, ToolCallMessage, StopMessage, ContentMessage


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
                yield ReasonMessage(reasoning_content).to_dict()
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
                yield ContentMessage(content).to_dict()
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
                yield ToolCallMessage(self.tool_call_id, "function", self.tool_name, self.tool_args).to_dict()
            if getattr(choice, "finish_reason", None) == "stop":
                yield StopMessage().to_dict()

        # if self.xml_buffer:
        #     try:
        #         func_match = re.search(r"<function=(.*?)>", self.xml_buffer, re.S)
        #         if func_match:
        #             self.tool_name = func_match.group(1).strip()
        #         params = {}
        #         for p_match in re.finditer(r"<parameter=(.*?)>(.*?)</parameter>", self.xml_buffer, re.S):
        #             key = p_match.group(1).strip()
        #             val = p_match.group(2).strip()
        #             params[key] = val
        #         self.tool_args = json.dumps(params, ensure_ascii=False)
        #         self.tool_call_id = f"xml_{self.tool_name}"
        #     except Exception:
        #         self.tool_name = ""
        #         self.tool_args = ""
        #         self.tool_call_id = None
