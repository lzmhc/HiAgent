import json
import os
import pty
import select
import subprocess
import termios

import requests
from pathlib import Path
from pydantic import Field
from fastmcp import FastMCP
mcp = FastMCP("Hi MCP Server")

class ShellSession:
    def __init__(self):
        self.master, slave = pty.openpty()
        env = os.environ.copy()
        env["TERM"] = "dumb"
        env["PS1"] = ""
        env["PROMPT_COMMAND"] = ""
        attr = termios.tcgetattr(slave)
        attr[1] &= ~termios.ONLCR
        attr[3] &= ~termios.ECHO
        termios.tcsetattr(slave, termios.TCSANOW, attr)
        self.proc = subprocess.Popen(
            ["/bin/bash", "--norc", "+m"],
            stdin=slave,
            stdout=slave,
            stderr=slave,
            close_fds=True,
            preexec_fn=os.setsid,
            env=env,
        )
        os.close(slave)
    def execute(self, command: str):
        send = (command + "\n").encode("utf-8")
        os.write(self.master, send)
        while True:
            r, _, _ = select.select([self.master], [], [], 10)
            if not r:
                break
            chunk = os.read(self.master, 1024 * 10)
            print(chunk)
            if not chunk:
                break
            yield chunk.decode("utf-8")
            # yield chunk
shell_session = ShellSession()
@mcp.tool(
    name="execute_pty",
    title="execute_pty",
    description="Execute a shell command or a multiline shell scriptin a PTY.",
    meta={"version": "1.0", "author": "lzmhc"}
)
def execute_pty(command: str = Field(description = "The shell command or multiline script to execute.")):
    return shell_session.execute(command)

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

if __name__ == "__main__":
    mcp.run(transport="http", port=8001)
    # mcp.run()
