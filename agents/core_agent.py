import json
from typing import List, Dict
from pathlib import Path

from agents.skills import SkillManage
from agents.tool_call_parser import ToolCallParser
from agents.base_llm_adapter import BaseLLMAdapter, create_adapter
from config.global_config import GlobalConfig
from memory.message import (
    SystemMessage, UserMessage, AssistantMessage,
    ToolResultMessage, ToolResultEvent, ErrorEvent,
)
from tools.execute_shell.execute_shell import execute_shell
from tools.search.brave_search import brave_search
from tools.search.bocha_search import bocha_search

available_tools = {
    "bocha_search": bocha_search,
    "brave_search": brave_search,
    "execute_shell": execute_shell
}


def load_agents_md() -> str:
    search_paths = [
        Path(__file__).parent.parent / "AGENTS.md",  # 项目根目录
        Path(__file__).parent.parent / "CLAUDE.md",  # 项目根目录
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
tools = [
    {
        "type": "function",
        "function": {
            "name": "bocha_search",
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
            "name": "execute_shell",
            "description": (
                "执行Linux Shell命令并返回输出结果。"
                "适用于文件管理、系统查询、开发调试等任务。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "需要执行的Shell命令，例如 "
                            "'ls -la'、'pwd'、'ps aux'、'df -h'"
                        )
                    }
                },
                "required": ["command"]
            }
        }
    }
]


class CoreAgent:
    def __init__(self, config: GlobalConfig, messages: List[Dict]):
        super().__init__()
        self.config = config
        self.messages = messages
        self.adapter: BaseLLMAdapter = create_adapter(
            model=self.config.get_config().get_model(),
            api_key=self.config.get_config().get_api_key(),
            base_url=self.config.get_config().get_base_url(),
            timeout=self.config.get_config().get_timeout(),
            temperature=self.config.get_config().get_temperature(),
            max_tokens=self.config.get_config().get_max_tokens(),
        )
        self.skill_manage = SkillManage(self.config)

        agents_md_content = load_agents_md()
        if agents_md_content:
            self.messages.insert(0, SystemMessage(agents_md_content).to_dict())

    def run(self):
        user_msg = self.messages[-1]
        skill_match = self.skill_manage.match_skills(user_msg)
        if skill_match:
            prompt = "\n\n".join(
                f"""
                已加载 Skill：{skill.name}

                Skill 根目录：
                {skill.root_dir}

                Skill 配置文件：
                {skill.prompt_file}

                以下是 Skill 的说明：

                {skill.system_prompt}
                """
                for skill in skill_match
            )
            self.messages.insert(0, SystemMessage(prompt).to_dict())
        try:
            while True:
                stop = False
                parser = ToolCallParser()
                stream = self.adapter.stream_invoke(messages=self.messages, tools=tools)
                parse_result = None
                for event in parser.process_stream(stream):
                    if event["role"] == "content":
                        yield event
                    elif event["role"] == "reason":
                        yield event
                    elif event["role"] == "toolCall":
                        parse_result = event
                    elif event["role"] == "stop":
                        stop = True
                        break

                if parse_result:
                    func = parse_result.get("function", {})
                    tool_call_id = parse_result.get("id")
                    tool_name = func.get("name")
                    tool_args_str = func.get("arguments")
                    try:
                        args = json.loads(tool_args_str) if tool_args_str else {}
                    except json.JSONDecodeError:
                        yield ErrorEvent(content=f"工具参数解析失败：{tool_args_str}").to_dict()
                        return

                    yield parse_result

                    try:
                        tool_ret = available_tools[tool_name](**args)
                    except Exception as e:
                        yield ErrorEvent(content=f"工具执行失败：{e}").to_dict()
                        return

                    tool_ret_str = json.dumps(tool_ret, ensure_ascii=False)

                    yield ToolResultEvent(
                        tool_name=tool_name,
                        content=tool_ret_str,
                    ).to_dict()

                    self.messages.append(
                        AssistantMessage(tool_calls=[parse_result]).to_dict()
                    )
                    self.messages.append(
                        ToolResultMessage(
                            content=tool_ret_str,
                            tool_call_id=tool_call_id,
                        ).to_dict()
                    )
                    continue
                if stop:
                    break
        except Exception as e:
            yield ErrorEvent(content=str(e)).to_dict()
