from abc import ABC, abstractmethod

from mainagent.backend.model.states.tool_state.ToolReturnClass import ToolReturnClass


class BaseTool(ABC):
    @abstractmethod
    def invoke(self, arg: dict) -> ToolReturnClass:
        pass
