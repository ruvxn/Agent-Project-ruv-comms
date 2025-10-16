from backend.model.states.StateManager import StateManager
from backend.model.states.graph_state.GraphState import GraphState
from backend.model.states.tool_state.ToolReturnClass import ToolReturnClass
from backend.tools.get_tool_registry import get_tool_registry
from langchain_core.messages import AIMessage


def command(tool_name: str, result: ToolReturnClass) -> GraphState:
    tool_registry = get_tool_registry()
    state = StateManager.get_state()

    StateManager.update_substate(
        "messages", [m[1] for m in result.state.messages])
    state.logs.append("[command] Message state updated")
    StateManager.update_substate("logs", result.state.logs)
    state.logs.append("[command] Log state updated")

    if tool_name == tool_registry["qa_tool"]["name"]:
        StateManager.update_substate("qa_state", result.state.qa_state)

        state.logs.append("[command] QA tool state updated")

    elif tool_name == tool_registry["summary_tool"]["name"]:
        StateManager.update_substate(
            "summary_state", result.state.summary_state)
        state.logs.append("[command] Summary tool state updated")

    return StateManager.get_state()
