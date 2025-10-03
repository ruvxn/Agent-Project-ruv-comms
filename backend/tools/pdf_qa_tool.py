
from backend.model.states.GraphState import GraphState
from backend.model.states.tool_state.ToolReturnClass import ToolReturnClass
from backend.pipeline.qa_tool.build_qa_graph import build_qa_graph
from backend.tools.base_tool import BaseTool
import streamlit as st


class pdf_qa_tool(BaseTool):
    """Return answers based on top-k knowledge base chunks"""

    def __init__(self) -> None:
        super().__init__()
        self.subgraph = build_qa_graph()

    def invoke(self, arg: dict) -> ToolReturnClass:
        state: GraphState = arg["state"]
        qa_state: GraphState = self.subgraph.invoke(state)
        if isinstance(qa_state, dict):
            qa_state = GraphState(**qa_state)
        return ToolReturnClass(
            state=qa_state,
            agent_response=qa_state.messages.ai_response_list[-1] if qa_state.messages.ai_response_list else "No response",
            meta={"tool_name": "pdf_qa_tool"}
        )
