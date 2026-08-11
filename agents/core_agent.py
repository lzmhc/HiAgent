import json

from agents.skills import SkillManage
from agents.tool_call_parser import ToolCallParser
from agents.base_llm_adapter import BaseLLMAdapter, create_adapter
from config.global_config import GlobalConfig
from tools.execute_shell.execute_shell import execute_shell
from tools.search.brave_search import brave_search
from tools.search.bocha_search import bocha_search

available_tools = {
    "bocha_search": bocha_search,
    "brave_search": brave_search,
    "execute_shell": execute_shell
}
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
    def __init__(self, config: GlobalConfig, messages):
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

    def run(self):
        user_msg = self.messages[-1]
        skill_match = self.skill_manage.match_skills(user_msg)
        print(f"使用skill{skill_match}")
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
            self.messages.insert(0, {
                "role": "system",
                "content": prompt
            })
        try:
            tool_round = 0
            while True:
                parser = ToolCallParser()
                stream = self.adapter.stream_invoke(messages=self.messages, tools=tools)
                parse_result = None
                for event in parser.process_stream(stream):
                    if event["type"] == "content":
                        yield event
                    elif event["type"] == "reasoning":
                        yield event
                    elif event["type"] == "finish":
                        parse_result = event
                if not parse_result:
                    yield {
                        "type": "error",
                        "content": "解析失败，没有 finish 事件"
                    }
                    return
                if not parse_result["need_tool"]:
                    yield {
                        "type": "finish",
                        "text": parse_result["text"]
                    }
                    return
                tool_name = parse_result["tool_name"]
                tool_args_str = parse_result["tool_args"]
                tool_id = parse_result["tool_id"]
                if tool_name not in available_tools:
                    yield {
                        "type": "error",
                        "content": f"未知工具：{tool_name}"
                    }
                    return

                try:
                    args = json.loads(tool_args_str) if tool_args_str else {}
                except json.JSONDecodeError:
                    yield {
                        "type": "error",
                        "content": f"工具参数解析失败：{tool_args_str}"
                    }
                    return
                yield {
                    "type": "tool_start",
                    "tool": tool_name,
                    "args": args
                }
                try:
                    tool_ret = available_tools[tool_name](** args)
                except Exception as e:
                    yield {
                        "type": "error",
                        "content": f"工具执行失败：{e}"
                    }
                    return
                yield {
                    "type": "tool_result",
                    "tool": tool_name,
                    "result": tool_ret
                }
                self.messages.append({
                    "role": "assistant",
                    "tool_calls": [{
                        "id": tool_id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": tool_args_str
                        }
                    }]
                })
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": json.dumps(tool_ret, ensure_ascii=False)
                })
                tool_round += 1
        except Exception as e:
            yield {
                "type": "error",
                "content": str(e)
            }