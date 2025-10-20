
import copy
from backend.model.states.graph_state.GraphState import GraphState
from backend.model.states.tool_state.ToolReturnClass import ToolReturnClass
from backend.graph.qa_graph.build_qa_graph import build_qa_graph
from backend.tools.base_tool import BaseTool
import streamlit as st
from backend.utils import log_decorator


@log_decorator
class qa_tool(BaseTool):
    """Return answers based on top-k knowledge base chunks"""

    def __init__(self) -> None:
        super().__init__()
        self.subgraph = build_qa_graph()

    async def invoke(self, args: dict) -> ToolReturnClass:
        state: GraphState = args["state"]
        state_for_invoke = copy.deepcopy(state)
        qa_state: GraphState = await self.subgraph.ainvoke(
            state_for_invoke)

        new_state = qa_state if isinstance(
            qa_state, GraphState) else GraphState(**qa_state)

        return ToolReturnClass(
            state=new_state,
            agent_response=new_state.messages.ai_response_list[-1].content if new_state.messages.ai_response_list else "No response",
            meta={"tool_name": "qa_tool"}
        )
