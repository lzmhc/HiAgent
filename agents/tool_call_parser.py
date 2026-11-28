from typing import Generator
from memory.message import TokenEvent, StopEvent, \
    AssistantMessage, TextOutput, FunctionCall, ContentEvent, ContentDeltaEvent


class ToolCallParser:
    def __init__(self):
        self.call_id = None
        self.name = None
        self.args = None

    def process_stream(self, stream: Generator):
        for event in stream:
            print(event)
            if event.type == "response.output_text.delta":
                yield ContentDeltaEvent(event.delta)
            elif event.type == "response.output_text.done":
                yield AssistantMessage(event.text)
            elif event.type == "response.output_item.added":
                item = event.item
                if item.type == "function_call":
                    self.name = item.name
                    self.call_id = item.call_id
            elif event.type == "response.function_call_arguments.done":
                self.args = event.arguments
            elif event.type == "response.completed":
                usage = event.response.usage
                yield TokenEvent(usage.input_tokens, usage.output_tokens, usage.total_tokens)
                output = event.response.output
                if getattr(output[0], "phase", None) is not None and output[0].phase == "final_answer":
                    print("stop")
                    yield StopEvent()
            if self.call_id is not None and self.name is not None and self.args is not None:
                yield FunctionCall(self.call_id, self.name, self.args)
                self.call_id = None
                self.name = None
                self.args = None
            # elif type(event) == ResponseOutputItemDoneEvent:
            #     item = event.item
            #     if type(item) == ResponseFunctionWebSearch:
            #         action = item.action
            #         if action.type == "find_in_page":
            #             yield ToolCallEvent(item.id, item.action.type, str(item.action.url)).to_dict()
            #         elif action.type == "search":
            #             yield ToolCallEvent(item.id, item.action.type, str(item.action.query)).to_dict()
            #     elif type(item) == ResponseFunctionToolCall:
            #         arguments = item.arguments
            #         yield ToolCallEvent(item.id, item.name, str(arguments)).to_dict()
            #     elif type(item) == ResponseOutputMessage:
            #         if item.phase == "final_answer":
            #             print("stop")
            #             yield StopEvent().to_dict()
