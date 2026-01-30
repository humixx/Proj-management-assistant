"""Base tool class for agent tools."""
from abc import ABC, abstractmethod
from typing import Any


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
    
    def to_claude_format(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }
