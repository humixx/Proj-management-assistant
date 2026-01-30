"""Tool registry for managing agent tools."""
from typing import Optional
from app.agent.tools.base import BaseTool


class ToolRegistry:
    """Registry for managing and accessing tools."""
    
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)
    
    def get_all(self) -> list[BaseTool]:
        return list(self._tools.values())
    
    def get_tool_definitions(self) -> list[dict]:
        return [tool.to_claude_format() for tool in self._tools.values()]
    
    def list_names(self) -> list[str]:
        return list(self._tools.keys())
