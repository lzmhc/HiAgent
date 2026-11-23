from typing import Generator

from openai.types.responses import ResponseCompletedEvent, ResponseCreatedEvent, ResponseInProgressEvent, \
    ResponseOutputItemAddedEvent, ResponseContentPartAddedEvent, ResponseTextDeltaEvent, ResponseAudioDeltaEvent, \
    ResponseTextDoneEvent, ResponseOutputItemDoneEvent, ResponseWebSearchCallSearchingEvent, ResponseFunctionWebSearch, \
    ResponseFunctionToolCall

from memory.message import ReasonEvent, ToolCallEvent, ContentEvent, ToolResultEvent, TokenEvent, StopEvent


class ToolCallParser:
    def __init__(self):
        self.id = None
        self.name = ""
        self.args = ""

    def process_stream(self, stream: Generator):
        for chunk in stream:
            print(chunk)
            if type(chunk) == ResponseCreatedEvent:
                pass
            elif type(chunk) == ResponseInProgressEvent:
                pass
            elif type(chunk) == ResponseOutputItemAddedEvent:
                pass
            elif type(chunk) == ResponseContentPartAddedEvent:
                pass
            elif type(chunk) == ResponseTextDeltaEvent:
                yield ContentEvent(chunk.delta).to_dict()
            elif type(chunk) == ResponseAudioDeltaEvent:
                pass
            elif type(chunk) == ResponseTextDoneEvent:
                # yield ContentEvent(chunk.text).to_dict()
                pass
            elif type(chunk) == ResponseOutputItemDoneEvent:
                item = chunk.item
                if type(item) == ResponseFunctionWebSearch:
                    action = item.action
                    if action.type == "find_in_page":
                        yield ToolCallEvent(item.id, item.action.type, str(item.action.url)).to_dict()
                    elif action.type == "search":
                        yield ToolCallEvent(item.id, item.action.type, str(item.action.query)).to_dict()
                elif type(item) == ResponseFunctionToolCall:
                    arguments = item.arguments
                    yield ToolCallEvent(item.id, item.name, str(arguments)).to_dict()
            elif type(chunk) == ResponseCompletedEvent:
                usage = chunk.response.usage
                output = chunk.response.output
                yield TokenEvent(usage.input_tokens, usage.output_tokens, usage.total_tokens).to_dict()
                if output and len(output) > 0:
                    item = output[0]
                    if item.type == "message" and item.phase == "final_answer":
                        print("stop")
                        yield StopEvent().to_dict()