from attr import dataclass
from mainagent.backend.model.states.GraphState import GraphState
from mainagent.backend.model.states.tool_state.ToolMetaDict import ToolMetaDict


@dataclass
class ToolReturnClass:
    state: GraphState
    agent_response: str = ""
    meta: ToolMetaDict = ToolMetaDict()
