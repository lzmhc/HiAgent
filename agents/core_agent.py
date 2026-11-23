import asyncio
import json
from typing import List, Dict
from pathlib import Path

from agents.skills import SkillManage
from agents.tool_call_parser import ToolCallParser
from agents.base_llm_adapter import BaseLLMAdapter, create_adapter
from config.global_config import GlobalConfig
from memory.message import (
    SystemMessage, AssistantMessage,
    ToolResultMessage, ToolResultEvent, ErrorEvent, ToolCallEvent, Input, Message, TextInput, TextOutput,
)
from tools.mcp.mcp_manage import mcp_manage

def load_agents_md() -> str:
    search_paths = [
        Path(__file__).parent.parent / "AGENTS.md",
        Path(__file__).parent.parent / "CLAUDE.md",
    ]
    
    agents_content = []
    for path in search_paths:
        if path.exists():
            try:
                content = path.read_text(encoding='utf-8')
                if content.strip():
                    agents_content.append(f"# 来源: {path}\n\n{content}")
            except Exception as e:
                print(f"读取 {path} 失败: {e}")
    
    return "\n\n---\n\n".join(agents_content) if agents_content else ""
# tools = [
#     {
#         "type": "mcp",
#         "server_label": "mcp_server",
#         "server_url": "http://localhost:8001/mcp",
#         "require_approval": "never",
#     }
# ]
# tools = [
#     {"type": "web_search"},
#     {
#         "type": "mcp",
#         "server_label": "mcp_serve",
#         "server_url": "https://mcp.wutwowu.us.kg/mcp",
#         "require_approval": "never",
#     }
# ]
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

    def run(self, message):
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
            while True:
                # stream = self.adapter.stream_invoke(messages=self.messages, tools=tools)
                stream = self.adapter.stream_invoke(message=message, tools=tools)
                for event in self.parser.process_stream(stream):
                    if event["role"] == "content":
                        yield event
                    elif event["role"] == "reason":
                        yield event
                    elif event["role"] == "toolCall":
                        function = event.get("function")
                        id = event.get("id")
                        name = function.get("name")
                        arguments = function.get("arguments")
                        yield event
                        try:
                            args = json.loads(arguments) if arguments else {}
                            tool_ret = getattr(asyncio.run(mcp_manage.call(name, args)), "content")
                            if tool_ret is not None and len(tool_ret) > 0:
                                type = getattr(tool_ret[0], "type")
                                res = getattr(tool_ret[0], type)
                                yield ToolResultEvent(
                                    id=id,
                                    name=name,
                                    content=res,
                                ).to_dict()
                                message = [
                                    # ToolResultMessage(content=[TextInput(res).to_dict()], tool_call_id=id).to_dict()
                                    AssistantMessage(content=[TextOutput(message[0].get("content")[0]["text"]).to_dict()]).to_dict(),
                                    AssistantMessage(content=[TextOutput(res).to_dict()]).to_dict()
                                ]
                                print(f"message={message}")
                        except Exception as e:
                            yield ErrorEvent(content=f"CallTool Erroe：{e}").to_dict()
                    elif event["role"] == "token":
                        yield event
                    elif event["role"] == "stop":
                        yield event
                        return
        except Exception as e:
            yield ErrorEvent(content=str(e)).to_dict()
