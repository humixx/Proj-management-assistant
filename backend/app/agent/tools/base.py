"""Base tool class for agent tools."""
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator


class BaseTool(ABC):
    """Abstract base class for all agent tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict:
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass

    @property
    def supports_streaming(self) -> bool:
        """Override to True if the tool implements execute_streaming."""
        return False

    async def execute_streaming(self, **kwargs) -> AsyncGenerator[dict, None]:
        """Yield progress events during execution. Final yield must be the result.

        Each yielded dict should have a "type" key. The last yield should have
        type="result" with the full tool result in "data".
        Intermediate yields (e.g. type="task_created") are forwarded to the
        frontend as SSE events.
        """
        # Default: just run execute and yield the result
        result = await self.execute(**kwargs)
        yield {"type": "result", "data": result}

    def to_claude_format(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }
