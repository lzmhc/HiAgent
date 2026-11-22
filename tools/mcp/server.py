import json
import requests
from pathlib import Path
from pydantic import Field
from fastmcp import FastMCP
from tools.shell.shell_pty import ShellManager
mcp = FastMCP("Hi MCP Server")

shell_manager = ShellManager()
@mcp.tool(
    name="execute_pty",
    title="execute_pty",
    description="Execute a shell command or a multiline shell scriptin a PTY.",
    meta={"version": "1.0", "author": "lzmhc"}
)
def execute_pty(command: str = Field(description = "The shell command or multiline script to execute.")):
    return shell_manager.execute_shell(command)

@mcp.tool(
    name="brave_search",
    title="brave_search",
    description="联网搜索互联网最新信息",
    meta={"version": "1.0", "author": "lzmhc"}
)
def brave_search(
        query: str = Field(description="搜索关键词"),
        count: int = Field(default=5, description="返回结果数量，默认5")):
    config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    api_key = config.get("brave_api", None)
    url = "https://api.search.brave.com/res/v1/web/search"
    proxies = {
        "http": "http://127.0.0.1:7897",
        "https": "http://127.0.0.1:7897"
    }
    data = json.dumps({
        "q": query,
        "search_lang": "ca",
        "count": count
    })
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    response = requests.post(
        url,
        data=data,
        headers=headers,
        proxies=proxies,
        timeout=10
    )
    return response.json()

# if __name__ == "__main__":
#     mcp.run()
