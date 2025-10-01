from abc import ABC, abstractmethod

from backend.model.states.ToolReturnClass import ToolReturnClass


class BaseTool(ABC):
    @abstractmethod
    def invoke(self, arg: dict) -> ToolReturnClass:
        pass
