import asyncio
from tools.mcp.server import mcp
class McpManage():
    def __init__(self):
        self.mcp = mcp
    async def get_mcp_tool(self):
        try:
            result = await self.mcp.list_tools()
            tool_dicts = [tool.model_dump() for tool in result]
            return tool_dicts
        except Exception as e:
            return []
    async def call(self, name, args):
        try:
            result = await mcp.call_tool(name, args)
            return result
        except Exception as e:
            return None
mcp_manage = McpManage()
if __name__ == '__main__':
    # print(asyncio.run(mcp_manage.get_mcp_tool()))
    # print(asyncio.run(mcp_manage.call("brave_search", {"query": "崩坏 星穹铁道 米哈游 官网 下载 米游社", "count": 5})))
    print(asyncio.run(mcp_manage.call("execute_pty", {"command":"printf 'DISPLAY=%s WAYLAND_DISPLAY=%s\\n' \"$DISPLAY\" \"$WAYLAND_DISPLAY\"; command -v wmctrl; command -v swaymsg; command -v hyprctl; command -v kdotool; ps -eo comm | grep -E '^(code|gnome-shell|kwin_wayland|sway|Hyprland|niri|labwc|xfwm4|mutter)$' | sort -u"})))