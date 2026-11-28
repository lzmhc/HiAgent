import asyncio
import json

from agents.skills import SkillManage
from agents.tool_call_parser import ToolCallParser
from agents.base_llm_adapter import BaseLLMAdapter, create_adapter
from config.global_config import GlobalConfig
from memory.message import (
    SystemMessage, AssistantMessage, ErrorEvent, Input, Message, TextInput, TextOutput, TokenEvent,
    StopEvent, FunctionCallOutput, ContentEvent, ToolCallEvent, ToolResultEvent, ContentDeltaEvent, FunctionCall,
)
from tools.mcp.mcp_manage import mcp_manage

tools = [
    {
        "type": "function",
        "function": {
            "name": "brave_search",
            "description": "联网搜索互联网最新信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "count": {
                        "type": "integer",
                        "description": "返回结果数量，默认5",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_pty",
            "description": (
                "Execute a shell command or a multiline shell scriptin a PTY."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command or multiline script to execute. "
                    }
                },
                "required": ["command"]
            }
        }
    }
]

class CoreAgent:
    def __init__(self, config: GlobalConfig):
        super().__init__()
        self.config = config
        self.adapter: BaseLLMAdapter = create_adapter(
            model=self.config.get_config().get_model(),
            api_key=self.config.get_config().get_api_key(),
            base_url=self.config.get_config().get_base_url(),
            timeout=self.config.get_config().get_timeout(),
            temperature=self.config.get_config().get_temperature(),
            max_tokens=self.config.get_config().get_max_tokens(),
        )
        # self.skill_manage = SkillManage(self.config)
        self.parser = ToolCallParser()
        # agents_md_content = load_agents_md()
        # if agents_md_content:
        #     self.messages.insert(0, SystemMessage(agents_md_content).to_dict())

    def run(self, messages):
        # user_msg = self.messages[-1]
        # skill_match = self.skill_manage.match_skills(user_msg)
        # if skill_match:
        #     prompt = "\n\n".join(
        #         f"""
        #         已加载 Skill：{skill.name}
        #
        #         Skill 根目录：
        #         {skill.root_dir}
        #
        #         Skill 配置文件：
        #         {skill.prompt_file}
        #
        #         以下是 Skill 的说明：
        #
        #         {skill.system_prompt}
        #         """
        #         for skill in skill_match
        #     )
        #     self.messages.insert(0, SystemMessage(prompt).to_dict())
        try:
            assistant = ""
            while True:
            # for i in range(0, 10):
                # stream = self.adapter.stream_invoke(messages=self.messages, tools=tools)
                stream = self.adapter.stream_invoke(messages=messages, tools=tools)
                for event in self.parser.process_stream(stream):
                    if type(event) == ContentDeltaEvent:
                        yield event
                    elif type(event) == AssistantMessage:
                        messages.append(event.to_dict())
                        yield event
                    elif type(event) == FunctionCall:
                        call_id = event.call_id
                        name = event.name
                        arguments = event.arguments
                        messages.append(event.to_dict())
                        yield event
                        yield ToolCallEvent(call_id, name, arguments)
                        try:
                            args = json.loads(arguments) if arguments else {}
                            tool_ret = getattr(asyncio.run(mcp_manage.call(name, args)), "content")
                            if tool_ret is not None and len(tool_ret) > 0:
                                res = getattr(tool_ret[0], tool_ret[0].type)
                                tool_result = FunctionCallOutput(call_id, res)
                                messages.append(tool_result.to_dict())
                                yield tool_result
                                yield ToolResultEvent(call_id, res)
                                # print(f"messages={messages}")
                            else:
                                yield ErrorEvent(content=f"Tool Result is Null")
                                return
                        except Exception as e:
                            yield ErrorEvent(content=f"CallTool Erroe：{e}")
                            return
                    elif type(event) == TokenEvent:
                        yield event
                    elif type(event) == StopEvent:
                        yield event
                        return
        except Exception as e:
            yield ErrorEvent(content=str(e))
