
from mainagent.backend.model.states.GraphState import GraphState
from mainagent.backend.model.states.tool_state.ToolReturnClass import ToolReturnClass
from mainagent.backend.pipeline.qa_tool.build_qa_graph import build_qa_graph
from mainagent.backend.pipeline.summary_tool.build_summary_graph import build_summary_graph
from mainagent.backend.tools.base_tool import BaseTool
import streamlit as st


class summary_tool(BaseTool):
    """Return Final Summary"""

    def __init__(self) -> None:
        super().__init__()
        self.subgraph = build_summary_graph()

    def invoke(self, arg: dict) -> ToolReturnClass:
        state: GraphState = arg["state"]
        qa_state: GraphState = self.subgraph.invoke(state)
        if isinstance(qa_state, dict):
            qa_state = GraphState(**qa_state)
        return ToolReturnClass(
            state=qa_state,
            agent_response=state.qa_state.final_summary,
            meta={"tool_name": "summary_tool"}
        )
